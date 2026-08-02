# coding=utf-8
"""客户关怀 PC 端 JSON API：规则、任务、触达记录、客户流水。"""

from __future__ import annotations

import datetime
import json
import uuid
from collections import OrderedDict

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from baseinfo.models import Empl, Vip
from common.constants import CASETYPE, CASESTATUS
from crm.crm_rules import generate_crm_cases
from crm.models import CrmCase, CrmCaseDetail, CrmRule, VipCaseDetail
from report.scope import django_user_id_from_request


def _json_body(request):
    """读取并缓存 JSON body，避免多次访问 request.body。"""
    if not hasattr(request, "_crm_json_body"):
        request._crm_json_body = {}
        try:
            raw = request.body
        except Exception:
            raw = b""
        if raw:
            try:
                parsed = json.loads(raw.decode("utf-8") or "{}")
                if isinstance(parsed, dict):
                    request._crm_json_body = parsed
            except (ValueError, UnicodeDecodeError):
                pass
    return request._crm_json_body


def _param(request, key, default=""):
    """GET/POST/JSON body/Header 参数读取。"""
    val = request.GET.get(key)
    if val in (None, ""):
        val = request.POST.get(key)
    if val in (None, ""):
        val = _json_body(request).get(key)
    if val in (None, ""):
        header = "HTTP_X_%s" % key.upper().replace("-", "_")
        val = request.META.get(header)
    return "" if val is None else str(val).strip()


def _err(msg, status=400):
    return JsonResponse({"ok": False, "error": msg}, status=status)


def _ok(data, status=200):
    return JsonResponse({"ok": True, "data": data}, status=status)


def _resolve_scope(request, company):
    """解析公司/门店作用域。返回 (storecodes, profile, ecode)。"""
    from common.genesis_auth import profile_allowed_storecodes
    from common.models import GenesisUserProfile
    from django.contrib.auth.models import User

    storecode = _param(request, "storecode")
    user_id = django_user_id_from_request(request)
    profile = None
    if user_id is not None:
        try:
            user = User.objects.select_related("genesis_profile").get(
                pk=user_id, is_active=True
            )
            profile = user.genesis_profile
        except (User.DoesNotExist, GenesisUserProfile.DoesNotExist):
            return None, None, "", "用户不存在或未绑定档案"
        if (profile.company or "").strip() != company:
            return None, None, "", "公司与用户档案不一致"
        allowed = list(profile_allowed_storecodes(profile))
        if storecode and storecode not in allowed:
            return None, None, "", "无权访问该门店"
        storecodes = [storecode] if storecode else allowed
        ecode = (profile.employee_code or user.username or "").strip()
        return storecodes, profile, ecode, ""
    # 兼容旧调用：无登录用户时按显式门店过滤
    storecodes = [storecode] if storecode else []
    return storecodes, None, _param(request, "ecode"), ""


def _serialize_rule(rule):
    return {
        "uuid": str(rule.uuid),
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "rule_type_name": rule.get_rule_type_display(),
        "casetype": rule.casetype or "",
        "casetype_name": rule.get_casetype_display() if rule.casetype else "",
        "days_offset": rule.days_offset,
        "month_offset": rule.month_offset,
        "ttype": rule.ttype or "",
        "lifecycle_segment": rule.lifecycle_segment or "",
        "casedesc_template": rule.casedesc_template or "",
        "assignee_policy": rule.assignee_policy,
        "assignee_policy_name": rule.get_assignee_policy_display(),
        "fixed_ecode": rule.fixed_ecode or "",
        "enabled": rule.enabled or "Y",
        "storecode": rule.storecode or "",
        "last_run_at": rule.last_run_at.strftime("%Y-%m-%d %H:%M") if rule.last_run_at else "",
        "last_run_summary": rule.last_run_summary or "",
        "create_time": rule.create_time.strftime("%Y-%m-%d %H:%M") if rule.create_time else "",
    }


def _serialize_vip(vip):
    if not vip:
        return {}
    return {
        "uuid": str(vip.uuid),
        "vcode": vip.vcode or "",
        "vname": vip.vname or "",
        "mtcode": vip.mtcode or "",
        "telph": vip.telph or "",
        "viptype": vip.viptype or "",
        "status": vip.status or "",
        "birth": vip.birth or "",
        "indate": vip.indate.strftime("%Y-%m-%d") if vip.indate else "",
        "ecode": vip.ecode or "",
        "ecode2": vip.ecode2 or "",
        "storecode": vip.storecode or "",
    }


def _serialize_attempt(detail, empl_map=None):
    empl_map = empl_map or {}
    ecode = ""
    if detail.ecode_id:
        ecode = empl_map.get(str(detail.ecode_id), "")
        if not ecode:
            try:
                ecode = detail.ecode.ecode or ""
            except Exception:
                ecode = ""
    channel_choices = dict(CrmCaseDetail.CRM_CHANNEL)
    outcome_choices = dict(CrmCaseDetail.CRM_OUTCOME)
    content = (detail.detail or detail.detaildescription or "").strip()
    return {
        "uuid": str(detail.uuid),
        "channel": detail.channel or "",
        "channel_name": channel_choices.get(detail.channel or "", detail.channel or ""),
        "outcome": detail.outcome or "",
        "outcome_name": outcome_choices.get(detail.outcome or "", detail.outcome or ""),
        "detail": detail.detail or "",
        "detaildescription": detail.detaildescription or "",
        "content": content,
        "ecode": ecode,
        "contact_time": detail.contact_time.strftime("%Y-%m-%d %H:%M") if detail.contact_time else (detail.create_time.strftime("%Y-%m-%d %H:%M") if detail.create_time else ""),
        "nextdate": detail.nextdate.isoformat() if detail.nextdate else "",
        "nextecode": detail.nextecode or "",
        "create_time": detail.create_time.strftime("%Y-%m-%d %H:%M") if detail.create_time else "",
    }


def _serialize_task(task, empl_map=None, vip=None):
    empl_map = empl_map or {}
    if vip is None:
        vip = task.vipuuid
    casetype_choices = dict(CASETYPE)
    status_choices = dict(CASESTATUS)
    rule = task.rule
    return {
        "uuid": str(task.uuid),
        "casetype": task.casetype or "",
        "casetype_name": casetype_choices.get(task.casetype or "", task.casetype or ""),
        "status": task.status or "10",
        "status_name": status_choices.get(task.status or "10", task.status or ""),
        "planbegindate": task.planbegindate.isoformat() if task.planbegindate else "",
        "planfinishdate": task.planfinishdate.isoformat() if task.planfinishdate else "",
        "finishedate": task.finishedate.isoformat() if task.finishedate else "",
        "casedesc": task.casedesc or "",
        "vsdate": task.vsdate.isoformat() if task.vsdate else "",
        "ecode": task.ecode or "",
        "empl_name": empl_map.get(task.ecode or "", ""),
        "storecode": task.storecode or "",
        "vip": _serialize_vip(vip),
        "rule": {
            "uuid": str(rule.uuid),
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
        } if rule else None,
        "create_time": task.create_time.strftime("%Y-%m-%d %H:%M") if task.create_time else "",
    }


def _task_qs(company, storecodes, params):
    qs = CrmCase.objects.filter(company=company, flag="Y")
    if storecodes:
        qs = qs.filter(storecode__in=storecodes)
    status = params.get("status", "")
    if status:
        qs = qs.filter(status=status)
    rule_uuid = params.get("rule_uuid", "")
    if rule_uuid:
        qs = qs.filter(rule__uuid=rule_uuid)
    rule_type = params.get("rule_type", "")
    if rule_type:
        qs = qs.filter(rule__rule_type=rule_type)
    vipuuid = params.get("vipuuid", "")
    if vipuuid:
        qs = qs.filter(vipuuid__uuid=vipuuid)
    date_from = params.get("date_from", "")
    date_to = params.get("date_to", "")
    if date_from:
        qs = qs.filter(planbegindate__gte=date_from)
    if date_to:
        qs = qs.filter(planbegindate__lte=date_to)
    keyword = params.get("keyword", "").strip()
    if keyword:
        vip_ids = list(
            Vip.objects.filter(
                company=company,
                flag="Y",
            )
            .filter(
                Q(vname__icontains=keyword)
                | Q(vcode__icontains=keyword)
                | Q(mtcode__icontains=keyword)
            )
            .values_list("uuid", flat=True)[:500]
        )
        qs = qs.filter(vipuuid__in=vip_ids)
    ecode = params.get("ecode", "")
    if ecode:
        qs = qs.filter(ecode=ecode)
    due_date = params.get("due_date", "")
    if due_date:
        qs = qs.filter(planbegindate__lte=due_date, planfinishdate__gte=due_date)
    overdue = params.get("overdue", "")
    if overdue in ("1", "true", "yes"):
        today = datetime.date.today().isoformat()
        qs = qs.filter(status__in=("10", "20"), planfinishdate__lt=today)
    unassigned = params.get("unassigned", "")
    if unassigned in ("1", "true", "yes"):
        qs = qs.filter(Q(ecode__isnull=True) | Q(ecode=""))
    source = params.get("source", "")
    if source == "manual":
        qs = qs.filter(rule__isnull=True)
    return qs.order_by("-planbegindate", "-create_time")


def _empl_map(company, ecodes):
    ecodes = [e for e in (ecodes or []) if e]
    if not ecodes:
        return {}
    return dict(
        Empl.objects.filter(company=company, ecode__in=ecodes, flag="Y")
        .values_list("ecode", "ename")
    )


@csrf_exempt
def crm_dicts(request):
    """GET /crm/pc/dicts/ - 前端字典。"""
    from crm.models import CrmCaseDetail as D
    return _ok({
        "casetype": [{"value": k, "label": v} for k, v in CASETYPE],
        "status": [{"value": k, "label": v} for k, v in CASESTATUS],
        "channel": [{"value": k, "label": v} for k, v in D.CRM_CHANNEL],
        "outcome": [{"value": k, "label": v} for k, v in D.CRM_OUTCOME],
        "rule_type": [{"value": k, "label": v} for k, v in CrmRule.RULE_TYPE],
        "assignee_policy": [{"value": k, "label": v} for k, v in CrmRule.ASSIGNEE_POLICY],
        "lifecycle_segment": [
            {"value": "at_risk", "label": "流失预警"},
            {"value": "sleeping", "label": "沉睡唤醒"},
        ],
    })


# ===== 规则 =====

@csrf_exempt
def crm_rule_list(request):
    if request.method == "POST":
        return crm_rule_create(request)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    qs = CrmRule.objects.filter(company=company, flag="Y")
    storecode = _param(request, "storecode")
    if storecode:
        qs = qs.filter(Q(storecode=storecode) | Q(storecode="") | Q(storecode__isnull=True))
    rules = list(qs.order_by("-create_time"))
    return _ok([_serialize_rule(r) for r in rules])


@csrf_exempt
def crm_rule_detail(request, uuid):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        rule = CrmRule.objects.get(uuid=uuid, company=company, flag="Y")
    except CrmRule.DoesNotExist:
        return _err("规则不存在", 404)

    if request.method == "GET":
        return _ok(_serialize_rule(rule))
    if request.method == "DELETE":
        rule.delete()
        return _ok({"uuid": str(rule.uuid)})
    if request.method in ("PUT", "PATCH"):
        data = _json_body(request)
        editable = [
            "rule_name", "rule_type", "casetype", "days_offset", "month_offset",
            "ttype", "lifecycle_segment", "casedesc_template", "assignee_policy",
            "fixed_ecode", "enabled",
        ]
        for key in editable:
            if key in data:
                setattr(rule, key, data[key])
        rule.last_modified = datetime.datetime.now()
        rule.save()
        return _ok(_serialize_rule(rule))
    return _err("method not allowed", 405)


@csrf_exempt
def crm_rule_create(request):
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    data = _json_body(request)
    rule_name = str(data.get("rule_name") or "").strip()
    rule_type = str(data.get("rule_type") or "birthday").strip()
    if not rule_name:
        return _err("缺少 rule_name")
    if rule_type not in dict(CrmRule.RULE_TYPE):
        return _err("rule_type 无效")
    rule_storecode = str(data.get("storecode") or "") or (storecodes[0] if storecodes else "")
    rule = CrmRule.objects.create(
        company=company,
        storecode=rule_storecode,
        rule_name=rule_name,
        rule_type=rule_type,
        casetype=str(data.get("casetype") or ""),
        days_offset=int(data.get("days_offset") or 0),
        month_offset=int(data.get("month_offset") or 1),
        ttype=str(data.get("ttype") or ""),
        lifecycle_segment=str(data.get("lifecycle_segment") or ""),
        casedesc_template=str(data.get("casedesc_template") or ""),
        assignee_policy=str(data.get("assignee_policy") or "vip_ecode"),
        fixed_ecode=str(data.get("fixed_ecode") or ""),
        enabled=str(data.get("enabled") or "Y"),
        creater=ecode or "pc",
    )
    return _ok(_serialize_rule(rule), 201)


@csrf_exempt
def crm_rule_preview(request, uuid):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        rule = CrmRule.objects.get(uuid=uuid, company=company, flag="Y", enabled="Y")
    except CrmRule.DoesNotExist:
        return _err("规则不存在或未启用", 404)
    target = _parse_date_param(_param(request, "date"))
    result = generate_crm_cases(
        company,
        rule.storecode or (storecodes[0] if storecodes else ""),
        rule=rule,
        target_date=target,
        dry_run=True,
        limit=int(_param(request, "limit") or 200),
    )
    return _ok(result)


@csrf_exempt
def crm_rule_run(request, uuid):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        rule = CrmRule.objects.get(uuid=uuid, company=company, flag="Y", enabled="Y")
    except CrmRule.DoesNotExist:
        return _err("规则不存在或未启用", 404)
    target = _parse_date_param(_param(request, "date"))
    result = generate_crm_cases(
        company,
        rule.storecode or (storecodes[0] if storecodes else ""),
        rule=rule,
        target_date=target,
        dry_run=False,
        limit=int(_param(request, "limit") or 1000),
    )
    return _ok(result)


def _parse_date_param(raw):
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


# ===== 任务 =====

@csrf_exempt
def crm_task_list(request):
    if request.method == "POST":
        return crm_task_create(request)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    params = {
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
        "unassigned": _param(request, "unassigned"),
        "source": _param(request, "source"),
    }
    qs = _task_qs(company, storecodes, params)
    scope = _param(request, "scope")
    if scope == "mine":
        mine = ecode or _param(request, "ecode")
        if mine:
            qs = qs.filter(ecode=mine)
    page = max(1, int(_param(request, "page") or 1))
    page_size = min(200, max(1, int(_param(request, "page_size") or 20)))
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    tasks = list(page_obj.object_list.select_related("vipuuid", "rule"))
    empl_map = _empl_map(company, [t.ecode for t in tasks])
    return _ok({
        "total": paginator.count,
        "page": page,
        "page_size": page_size,
        "items": [_serialize_task(t, empl_map) for t in tasks],
    })


@csrf_exempt
def crm_task_summary(request):
    """GET /crm/pc/tasks/summary/ - 回访工作台统计与分组。"""
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    params = {
        "rule_uuid": _param(request, "rule_uuid"),
        "rule_type": _param(request, "rule_type"),
        "vipuuid": _param(request, "vipuuid"),
        "date_from": _param(request, "date_from"),
        "date_to": _param(request, "date_to"),
        "keyword": _param(request, "keyword"),
        "ecode": _param(request, "ecode"),
        "source": _param(request, "source"),
    }
    qs = _task_qs(company, storecodes, params)
    scope = _param(request, "scope")
    if scope == "mine":
        mine = ecode or _param(request, "ecode")
        if mine:
            qs = qs.filter(ecode=mine)
    today = datetime.date.today().isoformat()
    counts = {
        "total": qs.count(),
        "today": qs.filter(planbegindate__lte=today, planfinishdate__gte=today).count(),
        "overdue": qs.filter(status__in=("10", "20"), planfinishdate__lt=today).count(),
        "in_progress": qs.filter(status="20").count(),
        "completed": qs.filter(status="30").count(),
        "paused": qs.filter(status="40").count(),
        "unassigned": qs.filter(Q(ecode__isnull=True) | Q(ecode="")).count(),
    }

    rule_type_map = dict(CrmRule.RULE_TYPE)
    rule_groups = []
    for row in qs.values("rule__rule_type").annotate(c=Count("uuid")).order_by("-c"):
        key = row["rule__rule_type"] or "manual"
        label = rule_type_map.get(key) or ("手工任务" if key == "manual" else key)
        rule_groups.append({"key": key, "label": label, "count": row["c"]})

    status_map = dict(CASESTATUS)
    status_groups = []
    for row in qs.values("status").annotate(c=Count("uuid")).order_by("-c"):
        key = row["status"] or ""
        status_groups.append({"key": key, "label": status_map.get(key, key or "未知"), "count": row["c"]})

    assignee_rows = list(qs.values("ecode").annotate(c=Count("uuid")).order_by("-c"))
    empl_map = _empl_map(company, [r["ecode"] for r in assignee_rows if r["ecode"]])
    assignee_groups = []
    for row in assignee_rows:
        key = row["ecode"] or "unassigned"
        label = empl_map.get(row["ecode"] or "") or ("未派单" if key == "unassigned" else row["ecode"] or "")
        assignee_groups.append({"key": key, "label": label, "count": row["c"]})

    store_groups = []
    for row in qs.values("storecode").annotate(c=Count("uuid")).order_by("storecode"):
        key = row["storecode"] or ""
        store_groups.append({"key": key, "label": key or "未指定", "count": row["c"]})

    return _ok({
        "counts": counts,
        "groups": {
            "rule_type": rule_groups,
            "status": status_groups,
            "assignee": assignee_groups,
            "storecode": store_groups,
        },
    })


@csrf_exempt
def crm_task_create(request):
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    data = _json_body(request)
    vipuuid = str(data.get("vipuuid") or "").strip()
    if not vipuuid:
        return _err("缺少 vipuuid")
    try:
        vip = Vip.objects.get(uuid=vipuuid, company=company, flag="Y")
    except Vip.DoesNotExist:
        return _err("客户不存在", 404)
    storecode = (
        str(data.get("storecode") or "")
        or (vip.storecode or "")
        or (storecodes[0] if storecodes else "")
    )
    rule = None
    rule_uuid = str(data.get("rule_uuid") or "").strip()
    if rule_uuid:
        rule = CrmRule.objects.filter(uuid=rule_uuid, company=company, flag="Y").first()
    task_ecode = str(data.get("ecode") or ecode or "").strip()
    casetype = str(data.get("casetype") or "")
    if not casetype and rule and rule.casetype:
        casetype = rule.casetype
    task = CrmCase.objects.create(
        company=company,
        storecode=storecode,
        vipuuid=vip,
        rule=rule,
        casetype=casetype or "10",
        casedesc=str(data.get("casedesc") or ""),
        planbegindate=_parse_date_param(data.get("planbegindate")) or datetime.date.today(),
        planfinishdate=_parse_date_param(data.get("planfinishdate")) or datetime.date.today(),
        status="10",
        ecode=task_ecode,
        empl=_empl_for_ecode(company, task_ecode),
        creater=ecode or "pc",
    )
    empl_map = _empl_map(company, [task_ecode])
    return _ok(_serialize_task(task, empl_map, vip), 201)


def _empl_for_ecode(company, ecode):
    if not ecode:
        return None
    return Empl.objects.filter(company=company, ecode=ecode, flag="Y").first()


@csrf_exempt
def crm_task_detail(request, uuid):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        task = CrmCase.objects.select_related("vipuuid", "rule").get(
            uuid=uuid, company=company, flag="Y"
        )
    except CrmCase.DoesNotExist:
        return _err("任务不存在", 404)
    if storecodes and task.storecode and task.storecode not in storecodes:
        return _err("无权访问该任务", 403)
    details = list(CrmCaseDetail.objects.filter(caseid=task, flag="Y").order_by("create_time"))
    empl_ids = [d.ecode_id for d in details if d.ecode_id]
    empl_map = {}
    if empl_ids:
        empl_map = {
            str(e.uuid): e.ecode or ""
            for e in Empl.objects.filter(uuid__in=empl_ids, flag="Y")
        }
    attempts = [_serialize_attempt(d, empl_map) for d in details]
    task_empl_map = _empl_map(company, [task.ecode or ""])
    payload = _serialize_task(task, task_empl_map)
    payload["attempts"] = attempts
    return _ok(payload)


@csrf_exempt
def crm_task_attempt(request, uuid):
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        task = CrmCase.objects.select_related("vipuuid").get(
            uuid=uuid, company=company, flag="Y"
        )
    except CrmCase.DoesNotExist:
        return _err("任务不存在", 404)
    if storecodes and task.storecode and task.storecode not in storecodes:
        return _err("无权访问该任务", 403)
    data = _json_body(request)
    channel = str(data.get("channel") or "90").strip()
    outcome = str(data.get("outcome") or "").strip()
    detail_text = str(data.get("detail") or data.get("detaildescription") or "").strip()
    if not detail_text:
        return _err("缺少触达内容")
    exec_ecode = str(data.get("ecode") or ecode or "").strip()
    contact_time = data.get("contact_time") or None
    if contact_time:
        try:
            contact_time = datetime.datetime.strptime(str(contact_time), "%Y-%m-%d %H:%M")
        except ValueError:
            contact_time = datetime.datetime.now()
    else:
        contact_time = datetime.datetime.now()
    nextdate = _parse_date_param(data.get("nextdate"))
    nextecode = str(data.get("nextecode") or "").strip()
    empl = _empl_for_ecode(company, exec_ecode)
    detail = CrmCaseDetail.objects.create(
        company=company,
        storecode=task.storecode or "",
        caseid=task,
        channel=channel,
        outcome=outcome,
        detail=detail_text[:512],
        detaildescription=detail_text,
        ecode=empl,
        contact_time=contact_time,
        nextdate=nextdate,
        nextecode=nextecode,
        creater=exec_ecode or "pc",
    )
    if task.status == "10":
        task.status = "20"
        task.save(update_fields=["status", "last_modified"])
    # 每次触达都追加一条客户流水（vipcasedetail 保持简单记录语义）
    VipCaseDetail.objects.create(
        company=company,
        storecode=task.storecode or "",
        vipuuid=task.vipuuid,
        casetype=task.casetype or "10",
        detail=detail_text[:1024],
        detaildescription=detail_text,
        ecode=exec_ecode,
        nextdate=nextdate,
        nextecode=nextecode,
        status="20",
        creater=exec_ecode or "pc",
    )
    return _ok(_serialize_attempt(detail), 201)


@csrf_exempt
def crm_task_suggest(request, uuid):
    """POST /crm/pc/tasks/<uuid>/suggest/ - AI 回访话术建议。"""
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        task = CrmCase.objects.select_related("vipuuid", "rule").get(
            uuid=uuid, company=company, flag="Y"
        )
    except CrmCase.DoesNotExist:
        return _err("任务不存在", 404)
    if storecodes and task.storecode and task.storecode not in storecodes:
        return _err("无权访问该任务", 403)
    from crm.touch_suggestion import generate_touch_suggestion

    variants_raw = _param(request, "variants")
    try:
        variants = int(variants_raw)
    except (TypeError, ValueError):
        variants = 3
    result = generate_touch_suggestion(
        company,
        task.storecode or "",
        task,
        channel=_param(request, "channel"),
        outcome=_param(request, "outcome"),
        variants=variants,
    )
    return _ok(result)


@csrf_exempt
def crm_task_complete(request, uuid):
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        task = CrmCase.objects.select_related("vipuuid").get(
            uuid=uuid, company=company, flag="Y"
        )
    except CrmCase.DoesNotExist:
        return _err("任务不存在", 404)
    if storecodes and task.storecode and task.storecode not in storecodes:
        return _err("无权访问该任务", 403)
    data = _json_body(request)
    note = str(data.get("note") or data.get("detail") or "").strip()
    outcome = str(data.get("outcome") or "").strip()
    nextdate = _parse_date_param(data.get("nextdate"))
    nextecode = str(data.get("nextecode") or "").strip()
    had_attempt = CrmCaseDetail.objects.filter(caseid=task, flag="Y").exists()
    if note:
        exec_ecode = str(data.get("ecode") or ecode or "").strip()
        detail = CrmCaseDetail.objects.create(
            company=company,
            storecode=task.storecode or "",
            caseid=task,
            channel=str(data.get("channel") or "90"),
            outcome=outcome or "10",
            detail=note[:512],
            detaildescription=note,
            ecode=_empl_for_ecode(company, exec_ecode),
            contact_time=datetime.datetime.now(),
            nextdate=nextdate,
            nextecode=nextecode,
            creater=exec_ecode or "pc",
        )
        if not had_attempt:
            VipCaseDetail.objects.create(
                company=company,
                storecode=task.storecode or "",
                vipuuid=task.vipuuid,
                casetype=task.casetype or "10",
                detail=note[:1024],
                detaildescription=note,
                ecode=exec_ecode,
                nextdate=nextdate,
                nextecode=nextecode,
                status="20",
                creater=exec_ecode or "pc",
            )
    task.status = "30"
    task.finishedate = datetime.date.today()
    task.save(update_fields=["status", "finishedate", "last_modified"])
    return _ok({"uuid": str(task.uuid), "status": "30"})


@csrf_exempt
def crm_task_status(request, uuid):
    if request.method != "POST":
        return _err("method not allowed", 405)
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        task = CrmCase.objects.get(uuid=uuid, company=company, flag="Y")
    except CrmCase.DoesNotExist:
        return _err("任务不存在", 404)
    if storecodes and task.storecode and task.storecode not in storecodes:
        return _err("无权访问该任务", 403)
    data = _json_body(request)
    new_status = str(data.get("status") or "").strip()
    if new_status not in ("10", "20", "30", "40"):
        return _err("status 无效")
    if new_status == "30":
        task.finishedate = datetime.date.today()
    task.status = new_status
    task_ecode = str(data.get("ecode") or "").strip()
    if task_ecode:
        task.ecode = task_ecode
        task.empl = _empl_for_ecode(company, task_ecode)
    task.save()
    return _ok({"uuid": str(task.uuid), "status": task.status, "ecode": task.ecode or ""})


# ===== 客户沟通流水（vipcasedetail） =====

@csrf_exempt
def crm_timeline(request):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    if request.method == "POST":
        data = _json_body(request)
        vipuuid = str(data.get("vipuuid") or "").strip()
        if not vipuuid:
            return _err("缺少 vipuuid")
        try:
            vip = Vip.objects.get(uuid=vipuuid, company=company, flag="Y")
        except Vip.DoesNotExist:
            return _err("客户不存在", 404)
        detail_text = str(data.get("detail") or data.get("detaildescription") or "").strip()
        if not detail_text:
            return _err("缺少记录内容")
        log = VipCaseDetail.objects.create(
            company=company,
            storecode=str(data.get("storecode") or vip.storecode or (storecodes[0] if storecodes else "")),
            vipuuid=vip,
            casetype=str(data.get("casetype") or "10"),
            detail=detail_text[:1024],
            detaildescription=detail_text,
            ecode=str(data.get("ecode") or ecode or ""),
            nextdate=_parse_date_param(data.get("nextdate")),
            nextecode=str(data.get("nextecode") or ""),
            status=str(data.get("status") or "20"),
            creater=ecode or "pc",
        )
        return _ok(_serialize_timeline(log), 201)

    vipuuid = _param(request, "vipuuid")
    qs = VipCaseDetail.objects.filter(company=company, flag="Y")
    if storecodes:
        qs = qs.filter(storecode__in=storecodes)
    if vipuuid:
        qs = qs.filter(vipuuid__uuid=vipuuid)
    qs = qs.select_related("vipuuid").order_by("-create_time")[:200]
    return _ok([_serialize_timeline(log) for log in qs])


def _serialize_timeline(log):
    casetype_choices = dict(CASETYPE)
    content = (log.detail or log.detaildescription or "").strip()
    return {
        "uuid": str(log.uuid),
        "vipuuid": str(log.vipuuid.uuid) if log.vipuuid else "",
        "vname": (log.vipuuid.vname if log.vipuuid else "") or "",
        "vcode": (log.vipuuid.vcode if log.vipuuid else "") or "",
        "mtcode": (log.vipuuid.mtcode if log.vipuuid else "") or "",
        "casetype": log.casetype or "",
        "casetype_name": casetype_choices.get(log.casetype or "", log.casetype or ""),
        "detail": log.detail or "",
        "detaildescription": log.detaildescription or "",
        "content": content,
        "ecode": log.ecode or "",
        "nextdate": log.nextdate.isoformat() if log.nextdate else "",
        "nextecode": log.nextecode or "",
        "status": log.status or "",
        "create_time": log.create_time.strftime("%Y-%m-%d %H:%M") if log.create_time else "",
    }


@csrf_exempt
def crm_timeline_detail(request, uuid):
    company = _param(request, "company")
    if not company:
        return _err("缺少 company")
    storecodes, profile, ecode, err = _resolve_scope(request, company)
    if err:
        return _err(err, 403)
    try:
        log = VipCaseDetail.objects.select_related("vipuuid").get(
            uuid=uuid, company=company, flag="Y"
        )
    except VipCaseDetail.DoesNotExist:
        return _err("记录不存在", 404)
    if request.method == "DELETE":
        log.delete()
        return _ok({"uuid": str(log.uuid)})
    if request.method in ("PUT", "PATCH"):
        data = _json_body(request)
        for key in ("detail", "detaildescription", "casetype", "nextdate", "nextecode", "status", "ecode"):
            if key in data and key not in ("nextdate",):
                setattr(log, key, data[key])
        if "nextdate" in data:
            log.nextdate = _parse_date_param(data.get("nextdate"))
        log.save()
        return _ok(_serialize_timeline(log))
    return _ok(_serialize_timeline(log))
