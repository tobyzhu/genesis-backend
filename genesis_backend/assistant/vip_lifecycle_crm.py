# coding=utf-8
"""客户生命周期 → CRM 回访任务（VipCaseDetail）。"""

from __future__ import annotations

import datetime as pydatetime
from typing import Any, Dict, List, Optional

from django.db import transaction

from assistant.vip_lifecycle import (
    SEGMENT_AT_RISK,
    SEGMENT_SLEEPING,
    compute_lifecycle_batch,
    recommended_actions_for_segment,
)
from baseinfo.models import Appoption, Vip
from crm.models import VipCaseDetail

LIFECYCLE_TASK_PREFIX = "[生命周期"
DEFAULT_CASETYPE = "10"
DEFAULT_TASK_STATUS = "10"  # 未开始

_SEGMENT_DAYS = {
    SEGMENT_AT_RISK: 3,
    SEGMENT_SLEEPING: 7,
}

_SEGMENT_LABEL = {
    SEGMENT_AT_RISK: "流失预警回访",
    SEGMENT_SLEEPING: "沉睡唤醒回访",
}


def _resolve_lifecycle_casetype(company: str) -> str:
    row = (
        Appoption.objects.filter(flag="Y", company=company, seg="vipcasetype")
        .values_list("itemname", "itemvalues")
        .first()
    )
    if row:
        return (row[0] or "").strip() or DEFAULT_CASETYPE
    row = (
        Appoption.objects.filter(flag="Y", company="common", seg="vipcasetype")
        .values_list("itemname", "itemvalues")
        .first()
    )
    if row:
        return (row[0] or "").strip() or DEFAULT_CASETYPE
    return DEFAULT_CASETYPE


def _task_detail(segment: str, row: Dict[str, Any]) -> str:
    seg_label = _SEGMENT_LABEL.get(segment, "生命周期回访")
    factors = row.get("risk_factors") or []
    factor_txt = "；".join(factors[:2]) if factors else ""
    actions = row.get("recommended_actions") or recommended_actions_for_segment(segment)
    act = actions[0].get("title") if actions else ""
    parts = [f"{LIFECYCLE_TASK_PREFIX}{seg_label}]"]
    if factor_txt:
        parts.append(factor_txt)
    if act:
        parts.append(f"建议：{act}")
    return " ".join(parts)[:1000]


def _has_open_lifecycle_task(company: str, storecode: str, vipuuid: str) -> bool:
    return (
        VipCaseDetail.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            vipuuid_id=vipuuid,
            status__in=("10", "20"),
            detail__contains=LIFECYCLE_TASK_PREFIX,
        ).exists()
    )


def create_lifecycle_crm_tasks(
    company: str,
    storecode: str = "",
    *,
    segment: str = SEGMENT_AT_RISK,
    ecode: str = "",
    limit: int = 100,
    dry_run: bool = False,
    creater_ecode: str = "",
) -> Dict[str, Any]:
    """
    为生命周期分级客户生成 VipCaseDetail 回访任务（顾问 nextecode=vip.ecode）。
    同一客户已有未完成的 [生命周期] 任务则跳过。
    storecode 为空则遍历该公司全部门店。
    """
    company = (company or "").strip()
    sc = (storecode or "").strip()
    seg = (segment or SEGMENT_AT_RISK).strip().lower()
    if seg not in (SEGMENT_AT_RISK, SEGMENT_SLEEPING):
        return {"error": "segment 仅支持 at_risk 或 sleeping", "created": 0, "skipped": 0}

    stores = [sc] if sc else list(
        Vip.objects.filter(company=company, flag="Y")
        .values_list("storecode", flat=True)
        .distinct()
    )
    total_created = 0
    total_skipped = 0
    all_errors: List[str] = []
    all_previews: List[Dict[str, Any]] = []
    last_meta: Dict[str, Any] = {}

    per_store_limit = max(10, int(limit / max(len(stores), 1)))

    for store in stores:
        if not store:
            continue
        one = _create_lifecycle_crm_tasks_for_store(
            company,
            store,
            segment=seg,
            ecode=(ecode or "").strip(),
            limit=per_store_limit,
            dry_run=dry_run,
            creater_ecode=creater_ecode,
        )
        total_created += int(one.get("created") or 0)
        total_skipped += int(one.get("skipped") or 0)
        all_errors.extend(one.get("errors") or [])
        all_previews.extend(one.get("previews") or [])
        last_meta = one

    return {
        "company": company,
        "storecode": sc or "*",
        "segment": seg,
        "dry_run": dry_run,
        "casetype": last_meta.get("casetype", DEFAULT_CASETYPE),
        "nextdate": last_meta.get("nextdate", ""),
        "created": total_created,
        "skipped": total_skipped,
        "errors": all_errors,
        "previews": all_previews[:20],
    }


def _create_lifecycle_crm_tasks_for_store(
    company: str,
    storecode: str,
    *,
    segment: str,
    ecode: str,
    limit: int,
    dry_run: bool,
    creater_ecode: str,
) -> Dict[str, Any]:
    batch = compute_lifecycle_batch(
        company,
        storecode,
        segment=segment,
        ecode=ecode,
        limit=limit,
        include_trend=False,
    )
    casetype = _resolve_lifecycle_casetype(company)
    today = pydatetime.date.today()
    follow_days = _SEGMENT_DAYS.get(segment, 3)
    nextdate = today + pydatetime.timedelta(days=follow_days)
    creater = (creater_ecode or "").strip()

    created = 0
    skipped = 0
    errors: List[str] = []
    previews: List[Dict[str, Any]] = []
    to_create: List[VipCaseDetail] = []

    for row in batch.get("vips") or []:
        vu = (row.get("vipuuid") or "").strip()
        if not vu:
            skipped += 1
            continue
        if _has_open_lifecycle_task(company, storecode, vu):
            skipped += 1
            continue
        try:
            vip = Vip.objects.get(company=company, storecode=storecode, uuid=vu, flag="Y")
        except Vip.DoesNotExist:
            skipped += 1
            continue
        adviser = (vip.ecode or "").strip()
        if not adviser:
            skipped += 1
            continue
        detail = _task_detail(segment, row)
        preview = {
            "vipuuid": vu,
            "vcode": row.get("vcode"),
            "vname": row.get("vname"),
            "nextecode": adviser,
            "nextdate": nextdate.isoformat(),
            "detail": detail,
        }
        previews.append(preview)
        if dry_run:
            created += 1
            continue
        to_create.append(
            VipCaseDetail(
                company=company,
                storecode=storecode,
                flag="Y",
                creater=creater or adviser,
                vipuuid=vip,
                casetype=casetype,
                detail=detail,
                ecode=adviser,
                nextecode=adviser,
                nextdate=nextdate,
                status=DEFAULT_TASK_STATUS,
            )
        )

    if to_create and not dry_run:
        try:
            with transaction.atomic():
                VipCaseDetail.objects.bulk_create(to_create, batch_size=100)
            created = len(to_create)
        except Exception as exc:
            errors.append(str(exc))
            created = 0

    return {
        "company": company,
        "storecode": storecode,
        "segment": segment,
        "dry_run": dry_run,
        "casetype": casetype,
        "nextdate": nextdate.isoformat(),
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "previews": previews[:20],
    }


def tool_vip_lifecycle_create_crm_tasks(
    company: str,
    storecode: str,
    segment: str = "at_risk",
    ecode: str = "",
    limit: int = 50,
    dry_run: bool = True,
    **_kwargs,
) -> Dict[str, Any]:
    """为预警/休眠客户生成 CRM 回访任务（默认 dry_run 预览）。"""
    return create_lifecycle_crm_tasks(
        company,
        storecode,
        segment=segment,
        ecode=ecode,
        limit=limit,
        dry_run=bool(dry_run),
    )
