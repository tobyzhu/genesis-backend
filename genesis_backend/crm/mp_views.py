# coding=utf-8
"""客户关怀小程序端 API：员工个人视角，强制 company + storecode + ecode。"""

from __future__ import annotations

import datetime
import json

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from baseinfo.models import Empl, Vip
from common.constants import CASESTATUS
from crm.models import CrmCase, CrmCaseDetail, CrmRule, VipCaseDetail
from crm.pc_views import (
    _empl_for_ecode,
    _empl_map,
    _json_body,
    _ok,
    _param,
    _parse_date_param,
    _serialize_attempt,
    _serialize_task,
    _serialize_timeline,
    _task_qs,
)


def _mp_scope(request):
    company = _param(request, "company")
    storecode = _param(request, "storecode")
    ecode = _param(request, "ecode")
    if not company or not storecode or not ecode:
        return None, None, None, "缺少 company/storecode/ecode"
    return company, storecode, ecode, ""


def _owned_task(company, storecode, ecode, uuid):
    try:
        task = CrmCase.objects.select_related("vipuuid", "rule").get(
            uuid=uuid,
            company=company,
            storecode=storecode,
            flag="Y",
            ecode=ecode,
        )
    except CrmCase.DoesNotExist:
        return None
    return task


def _task_params(request):
    return {
        "status": _param(request, "status"),
        "rule_uuid": _param(request, "rule_uuid"),
        "rule_type": _param(request, "rule_type"),
        "vipuuid": _param(request, "vipuuid"),
        "date_from": _param(request, "date_from"),
        "date_to": _param(request, "date_to"),
        "keyword": _param(request, "keyword"),
        "ecode": _param(request, "ecode"),
        "due_date": _param(request, "due_date"),
        "overdue": _param(request, "overdue"),
        "unassigned": "",
        "source": _param(request, "source"),
    }


@csrf_exempt
def mp_task_list(request):
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    qs = _task_qs(company, [storecode], _task_params(request)).filter(ecode=ecode)
    page = max(1, int(_param(request, "page") or 1))
    page_size = min(100, max(1, int(_param(request, "page_size") or 20)))
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    tasks = list(page_obj.object_list.select_related("vipuuid", "rule"))
    empl_map = _empl_map(company, [ecode])
    return _ok({
        "total": paginator.count,
        "page": page,
        "page_size": page_size,
        "items": [_serialize_task(t, empl_map) for t in tasks],
    })


@csrf_exempt
def mp_task_summary(request):
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    qs = _task_qs(company, [storecode], _task_params(request)).filter(ecode=ecode)
    today = datetime.date.today().isoformat()
    counts = {
        "total": qs.count(),
        "today": qs.filter(planbegindate__lte=today, planfinishdate__gte=today).count(),
        "overdue": qs.filter(status__in=("10", "20"), planfinishdate__lt=today).count(),
        "in_progress": qs.filter(status="20").count(),
        "completed": qs.filter(status="30").count(),
    }
    rule_type_map = dict(CrmRule.RULE_TYPE)
    groups = []
    for row in qs.values("rule__rule_type").annotate(c=Count("uuid")).order_by("-c"):
        key = row["rule__rule_type"] or "manual"
        groups.append({
            "key": key,
            "label": rule_type_map.get(key) or ("手工任务" if key == "manual" else key),
            "count": row["c"],
        })
    return _ok({"counts": counts, "groups": groups})


@csrf_exempt
def mp_task_detail(request, uuid):
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    details = list(CrmCaseDetail.objects.filter(caseid=task, flag="Y").order_by("create_time"))
    empl_ids = [d.ecode_id for d in details if d.ecode_id]
    empl_map = {}
    if empl_ids:
        empl_map = {
            str(e.uuid): e.ecode or ""
            for e in Empl.objects.filter(uuid__in=empl_ids, flag="Y")
        }
    payload = _serialize_task(task, _empl_map(company, [ecode]))
    payload["attempts"] = [_serialize_attempt(d, empl_map) for d in details]
    return _ok(payload)


@csrf_exempt
def mp_task_attempt(request, uuid):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    data = _json_body(request)
    detail_text = str(data.get("detail") or data.get("detaildescription") or "").strip()
    if not detail_text:
        return JsonResponse({"ok": False, "error": "缺少触达内容"}, status=400)
    channel = str(data.get("channel") or "90").strip()
    outcome = str(data.get("outcome") or "").strip()
    contact_time = datetime.datetime.now()
    nextdate = _parse_date_param(data.get("nextdate"))
    nextecode = str(data.get("nextecode") or ecode or "").strip()
    detail = CrmCaseDetail.objects.create(
        company=company,
        storecode=storecode,
        caseid=task,
        channel=channel,
        outcome=outcome,
        detail=detail_text[:512],
        detaildescription=detail_text,
        ecode=_empl_for_ecode(company, ecode),
        contact_time=contact_time,
        nextdate=nextdate,
        nextecode=nextecode,
        creater=ecode,
    )
    if task.status == "10":
        task.status = "20"
        task.save(update_fields=["status", "last_modified"])
    VipCaseDetail.objects.create(
        company=company,
        storecode=storecode,
        vipuuid=task.vipuuid,
        caseid=task.uuid,
        casetype=task.casetype or "10",
        detail=detail_text[:1024],
        detaildescription=detail_text,
        ecode=ecode,
        nextdate=nextdate,
        nextecode=nextecode,
        status="20",
        creater=ecode,
    )
    return _ok(_serialize_attempt(detail), 201)


@csrf_exempt
def mp_task_attempt_delete(request, uuid, attempt_uuid):
    """DELETE /crm/mp/tasks/<uuid>/attempt/<attempt_uuid>/ - 员工删除自己的触达记录。"""
    if request.method != "DELETE":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    attempt = CrmCaseDetail.objects.filter(uuid=attempt_uuid, caseid=task, flag="Y").first()
    if not attempt:
        return JsonResponse({"ok": False, "error": "触达记录不存在"}, status=404)
    from crm.pc_views import _delete_attempt_and_log

    _delete_attempt_and_log(task, attempt)
    return _ok({"uuid": str(attempt.uuid), "deleted": True})


@csrf_exempt
def mp_task_complete(request, uuid):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    data = _json_body(request)
    note = str(data.get("note") or data.get("detail") or "").strip()
    nextdate = _parse_date_param(data.get("nextdate"))
    nextecode = str(data.get("nextecode") or ecode or "").strip()
    had_attempt = CrmCaseDetail.objects.filter(caseid=task, flag="Y").exists()
    if note:
        CrmCaseDetail.objects.create(
            company=company,
            storecode=storecode,
            caseid=task,
            channel=str(data.get("channel") or "90"),
            outcome=str(data.get("outcome") or "10"),
            detail=note[:512],
            detaildescription=note,
            ecode=_empl_for_ecode(company, ecode),
            contact_time=datetime.datetime.now(),
            nextdate=nextdate,
            nextecode=nextecode,
            creater=ecode,
        )
        if not had_attempt:
            VipCaseDetail.objects.create(
                company=company,
                storecode=storecode,
                vipuuid=task.vipuuid,
                caseid=task.uuid,
                casetype=task.casetype or "10",
                detail=note[:1024],
                detaildescription=note,
                ecode=ecode,
                nextdate=nextdate,
                nextecode=nextecode,
                status="20",
                creater=ecode,
            )
    task.status = "30"
    task.finishedate = datetime.date.today()
    task.save(update_fields=["status", "finishedate", "last_modified"])
    return _ok({"uuid": str(task.uuid), "status": "30"})


@csrf_exempt
def mp_task_status(request, uuid):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    data = _json_body(request)
    new_status = str(data.get("status") or "").strip()
    if new_status not in ("10", "20", "40"):
        return JsonResponse({"ok": False, "error": "status 无效"}, status=400)
    task.status = new_status
    task.save(update_fields=["status", "last_modified"])
    return _ok({"uuid": str(task.uuid), "status": task.status})


@csrf_exempt
def mp_task_suggest(request, uuid):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    task = _owned_task(company, storecode, ecode, uuid)
    if not task:
        return JsonResponse({"ok": False, "error": "任务不存在或不属于当前员工"}, status=404)
    data = _json_body(request)
    variants_raw = str(data.get("variants") or "3")
    try:
        variants = int(variants_raw)
    except (TypeError, ValueError):
        variants = 3
    emp = Empl.objects.filter(company=company, ecode=ecode, flag="Y").first()
    current_ename = (emp.ename if emp else "") or ""
    from crm.touch_suggestion import generate_touch_suggestion

    result = generate_touch_suggestion(
        company,
        storecode,
        task,
        channel=str(data.get("channel") or ""),
        outcome=str(data.get("outcome") or ""),
        variants=variants,
        current_ecode=ecode,
        current_ename=current_ename,
    )
    return _ok(result)


@csrf_exempt
def mp_timeline(request):
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    if request.method == "POST":
        data = _json_body(request)
        vipuuid = str(data.get("vipuuid") or "").strip()
        if not vipuuid:
            return JsonResponse({"ok": False, "error": "缺少 vipuuid"}, status=400)
        try:
            vip = Vip.objects.get(uuid=vipuuid, company=company, storecode=storecode, flag="Y")
        except Vip.DoesNotExist:
            return JsonResponse({"ok": False, "error": "客户不存在"}, status=404)
        detail_text = str(data.get("detail") or data.get("detaildescription") or "").strip()
        if not detail_text:
            return JsonResponse({"ok": False, "error": "缺少记录内容"}, status=400)
        log = VipCaseDetail.objects.create(
            company=company,
            storecode=storecode,
            vipuuid=vip,
            casetype=str(data.get("casetype") or "10"),
            detail=detail_text[:1024],
            detaildescription=detail_text,
            ecode=ecode,
            nextdate=_parse_date_param(data.get("nextdate")),
            nextecode=str(data.get("nextecode") or ecode or ""),
            status="20",
            creater=ecode,
        )
        return _ok(_serialize_timeline(log), 201)
    vipuuid = _param(request, "vipuuid")
    qs = VipCaseDetail.objects.filter(company=company, storecode=storecode, flag="Y")
    if vipuuid:
        qs = qs.filter(vipuuid__uuid=vipuuid)
    qs = qs.select_related("vipuuid").order_by("-create_time")[:100]
    return _ok([_serialize_timeline(log) for log in qs])


@csrf_exempt
def mp_vip_search(request):
    company, storecode, ecode, err = _mp_scope(request)
    if err:
        return JsonResponse({"ok": False, "error": err}, status=400)
    keyword = _param(request, "keyword").strip()
    qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    if keyword:
        qs = qs.filter(
            Q(vname__icontains=keyword)
            | Q(vcode__icontains=keyword)
            | Q(mtcode__icontains=keyword)
            | Q(pinyin__icontains=keyword)
        )
    rows = []
    for v in qs.order_by("pinyin", "vcode")[:30]:
        rows.append({
            "uuid": str(v.uuid),
            "vcode": v.vcode or "",
            "vname": v.vname or "",
            "mtcode": v.mtcode or "",
            "viplevel": v.viplevel or "",
        })
    return _ok(rows)
