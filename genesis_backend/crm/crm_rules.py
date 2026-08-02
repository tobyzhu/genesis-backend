# coding=utf-8
"""客户关怀规则引擎：按 CrmRule 批量生成 CrmCase 回访/回馈任务。"""

from __future__ import annotations

import calendar
import datetime
from typing import Any, Dict, List, Optional

from django.db import transaction

from baseinfo.models import Empl, Vip
from cashier.models import Expvstoll
from crm.models import CrmCase, CrmRule

RULE_BIRTHDAY = "birthday"
RULE_ANNIVERSARY = "anniversary"
RULE_TRANSACTION = "transaction"
RULE_LIFECYCLE = "lifecycle"
RULE_CUSTOM = "custom"

DEFAULT_CASETYPE = "10"
DEFAULT_TEMPLATES = {
    RULE_BIRTHDAY: "{vname} 生日关怀，本月送上生日祝福与到店礼遇",
    RULE_ANNIVERSARY: "{vname} 入会周年关怀",
    RULE_TRANSACTION: "{vname} 消费后回访（{casetype_name}）",
    RULE_LIFECYCLE: "{vname} 生命周期关怀（{segment}）",
    RULE_CUSTOM: "{vname} 客户关怀",
}


def _parse_yyyymmdd(raw: str) -> Optional[datetime.date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _birth_month(birth: Optional[str]) -> str:
    """从生日字段提取月份，兼容 YYYYMMDD / MMDD / YYYY-MM-DD。"""
    birth = (birth or "").strip()
    if not birth:
        return ""
    if len(birth) >= 8 and birth[:4].isdigit() and birth[4:6].isdigit():
        return birth[4:6]
    if birth[:2].isdigit():
        return birth[:2]
    return ""


def render_template(template: str, vip: Vip, extra: Optional[Dict[str, Any]] = None) -> str:
    """渲染任务描述模板，支持 {vname}/{vcode}/{birth}/{segment} 等占位符。"""
    ctx = {
        "vname": (vip.vname or "").strip() or "会员",
        "vcode": (vip.vcode or "").strip() or "",
        "vipuuid": str(vip.uuid),
        "birth": (vip.birth or "").strip() or "",
        "indate": (vip.indate or "").strftime("%Y-%m-%d") if vip.indate else "",
        "mtcode": (vip.mtcode or "").strip() or "",
        "segment": "",
        "casetype_name": "",
        "days_since": "",
    }
    if extra:
        ctx.update(extra)
    text = template or ""
    for key, value in ctx.items():
        text = text.replace("{%s}" % key, str(value or ""))
    return text[:256]


def _month_bounds(year: int, month: int) -> tuple:
    last = calendar.monthrange(year, month)[1]
    return datetime.date(year, month, 1), datetime.date(year, month, last)


def _target_month(base: Optional[datetime.date], offset: int) -> datetime.date:
    base = base or datetime.date.today()
    total = base.year * 12 + (base.month - 1) + int(offset or 0)
    year, zero_based_month = divmod(total, 12)
    return datetime.date(year, zero_based_month + 1, 1)


def _assignee_ecode(vip: Vip, rule: CrmRule) -> str:
    policy = (rule.assignee_policy or "vip_ecode").strip()
    if policy == "vip_ecode2":
        return (vip.ecode2 or "").strip()[:16]
    if policy == "fixed":
        return (rule.fixed_ecode or "").strip()[:16]
    if policy == "store_manager":
        return ""
    return (vip.ecode or "").strip()[:16]


def _empl_for(company: str, ecode: str) -> Optional[Empl]:
    if not ecode:
        return None
    return Empl.objects.filter(company=company, ecode=ecode, flag="Y").first()


def _has_case_in_window(company, storecode, vip, rule, start, end) -> bool:
    qs = CrmCase.objects.filter(
        company=company,
        flag="Y",
        vipuuid=vip,
        rule=rule,
        planbegindate__lte=end,
        planfinishdate__gte=start,
    )
    if storecode:
        qs = qs.filter(storecode=storecode)
    return qs.exists()


def _has_case_same_start(company, storecode, vip, rule, start) -> bool:
    qs = CrmCase.objects.filter(
        company=company,
        flag="Y",
        vipuuid=vip,
        rule=rule,
        planbegindate=start,
    )
    if storecode:
        qs = qs.filter(storecode=storecode)
    return qs.exists()


def _create_case(
    *,
    company: str,
    storecode: str,
    vip: Vip,
    rule: CrmRule,
    start: datetime.date,
    end: datetime.date,
    casedesc: str,
    vsdate: Optional[datetime.date] = None,
    ecode: str = "",
) -> CrmCase:
    return CrmCase.objects.create(
        company=company,
        storecode=storecode or (vip.storecode or ""),
        flag="Y",
        vipuuid=vip,
        rule=rule,
        casetype=(rule.casetype or DEFAULT_CASETYPE),
        status="10",
        planbegindate=start,
        planfinishdate=end,
        casedesc=casedesc[:128],
        vsdate=vsdate,
        ecode=ecode,
        empl=_empl_for(company, ecode),
        creater="crm_rule",
    )


def _base_extra(rule: CrmRule) -> Dict[str, Any]:
    return {
        "casetype_name": rule.get_casetype_display() if hasattr(rule, "get_casetype_display") else "",
    }


def _candidate_vips(company: str, storecode: str) -> Any:
    qs = Vip.objects.filter(company=company, flag="Y")
    if storecode:
        qs = qs.filter(storecode=storecode)
    return qs


def _generate_birthday(company, storecode, rule, base_date, dry_run, limit):
    target = _target_month(base_date, rule.month_offset or 1)
    start, end = _month_bounds(target.year, target.month)
    qs = _candidate_vips(company, storecode)
    rows = []
    created = skipped = 0
    errors = []
    for vip in qs.iterator(chunk_size=500):
        month = _birth_month(vip.birth)
        if not month or int(month) != target.month:
            continue
        ecode = _assignee_ecode(vip, rule)
        casedesc = render_template(rule.casedesc_template or DEFAULT_TEMPLATES[RULE_BIRTHDAY], vip, _base_extra(rule))
        preview = {
            "vipuuid": str(vip.uuid),
            "vname": vip.vname,
            "vcode": vip.vcode,
            "mtcode": vip.mtcode,
            "ecode": ecode,
            "planbegindate": start.isoformat(),
            "planfinishdate": end.isoformat(),
            "casedesc": casedesc,
        }
        if _has_case_in_window(company, storecode, vip, rule, start, end):
            skipped += 1
            continue
        rows.append(preview)
        if not dry_run:
            _create_case(
                company=company,
                storecode=storecode,
                vip=vip,
                rule=rule,
                start=start,
                end=end,
                casedesc=casedesc[:128],
                ecode=ecode,
            )
            created += 1
        if limit and len(rows) >= limit:
            break
    return {"rows": rows, "created": created, "skipped": skipped, "errors": errors}


def _generate_anniversary(company, storecode, rule, base_date, dry_run, limit):
    target = _target_month(base_date, rule.month_offset or 0)
    start, end = _month_bounds(target.year, target.month)
    qs = _candidate_vips(company, storecode)
    rows = []
    created = skipped = 0
    errors = []
    for vip in qs.iterator(chunk_size=500):
        if not vip.indate or vip.indate.month != target.month:
            continue
        ecode = _assignee_ecode(vip, rule)
        casedesc = render_template(
            rule.casedesc_template or DEFAULT_TEMPLATES[RULE_ANNIVERSARY],
            vip,
            _base_extra(rule),
        )
        preview = {
            "vipuuid": str(vip.uuid),
            "vname": vip.vname,
            "vcode": vip.vcode,
            "mtcode": vip.mtcode,
            "ecode": ecode,
            "planbegindate": start.isoformat(),
            "planfinishdate": end.isoformat(),
            "casedesc": casedesc,
        }
        if _has_case_in_window(company, storecode, vip, rule, start, end):
            skipped += 1
            continue
        rows.append(preview)
        if not dry_run:
            _create_case(
                company=company,
                storecode=storecode,
                vip=vip,
                rule=rule,
                start=start,
                end=end,
                casedesc=casedesc[:128],
                ecode=ecode,
            )
            created += 1
        if limit and len(rows) >= limit:
            break
    return {"rows": rows, "created": created, "skipped": skipped, "errors": errors}


def _generate_transaction(company, storecode, rule, base_date, dry_run, limit):
    ttype = (rule.ttype or "").strip()
    qs = Expvstoll.objects.filter(
        company=company,
        flag="Y",
        valiflag="Y",
    )
    if ttype:
        qs = qs.filter(ttype=ttype)
    if storecode:
        qs = qs.filter(storecode=storecode)
    pairs = list(qs.order_by("-vsdate").values_list("vipuuid", "vsdate").distinct()[:2000])
    vip_ids = [str(p[0]) for p in pairs if p[0]]
    vips = {str(v.uuid): v for v in Vip.objects.filter(uuid__in=vip_ids)}
    rows = []
    created = skipped = 0
    errors = []
    for vipuuid, vsdate_raw in pairs:
        vip = vips.get(str(vipuuid))
        if not vip:
            continue
        trans_date = _parse_yyyymmdd(vsdate_raw or "")
        if not trans_date:
            continue
        target = trans_date + datetime.timedelta(days=int(rule.days_offset or 0))
        start = target
        end = target + datetime.timedelta(days=6)
        ecode = _assignee_ecode(vip, rule)
        casedesc = render_template(
            rule.casedesc_template or DEFAULT_TEMPLATES[RULE_TRANSACTION],
            vip,
            _base_extra(rule),
        )
        preview = {
            "vipuuid": str(vip.uuid),
            "vname": vip.vname,
            "vcode": vip.vcode,
            "mtcode": vip.mtcode,
            "ecode": ecode,
            "planbegindate": start.isoformat(),
            "planfinishdate": end.isoformat(),
            "casedesc": casedesc,
            "vsdate": trans_date.isoformat(),
        }
        if _has_case_same_start(company, storecode, vip, rule, start):
            skipped += 1
            continue
        rows.append(preview)
        if not dry_run:
            _create_case(
                company=company,
                storecode=storecode,
                vip=vip,
                rule=rule,
                start=start,
                end=end,
                casedesc=casedesc,
                vsdate=trans_date,
                ecode=ecode,
            )
            created += 1
        if limit and len(rows) >= limit:
            break
    return {"rows": rows, "created": created, "skipped": skipped, "errors": errors}


def _generate_lifecycle(company, storecode, rule, base_date, dry_run, limit):
    from assistant.vip_lifecycle import compute_lifecycle_batch

    segment = (rule.lifecycle_segment or "at_risk").strip().lower() or "at_risk"
    stores = [storecode] if storecode else list(
        Vip.objects.filter(company=company, flag="Y")
        .exclude(storecode__isnull=True)
        .exclude(storecode="")
        .values_list("storecode", flat=True)
        .distinct()
    )
    rows = []
    created = skipped = 0
    errors = []
    for sc in stores:
        batch = compute_lifecycle_batch(
            company,
            sc,
            segment=segment,
            limit=limit or 100,
            include_trend=False,
        )
        start = base_date or datetime.date.today()
        end = start + datetime.timedelta(days=7)
        for row in batch.get("vips") or []:
            vip = Vip.objects.filter(uuid=row.get("vipuuid")).first()
            if not vip:
                continue
            ecode = _assignee_ecode(vip, rule)
            casedesc = render_template(
                rule.casedesc_template or DEFAULT_TEMPLATES[RULE_LIFECYCLE],
                vip,
                {
                    "segment": row.get("segment") or segment,
                    "days_since": row.get("days_since_last_visit") or "",
                    "casetype_name": rule.get_casetype_display() if hasattr(rule, "get_casetype_display") else "",
                },
            )
            preview = {
                "vipuuid": str(vip.uuid),
                "vname": vip.vname,
                "vcode": vip.vcode,
                "mtcode": vip.mtcode,
                "ecode": ecode,
                "planbegindate": start.isoformat(),
                "planfinishdate": end.isoformat(),
                "casedesc": casedesc,
                "segment": row.get("segment") or segment,
            }
            if _has_case_in_window(company, sc, vip, rule, start, end):
                skipped += 1
                continue
            rows.append(preview)
            if not dry_run:
                _create_case(
                    company=company,
                    storecode=sc,
                    vip=vip,
                    rule=rule,
                    start=start,
                    end=end,
                    casedesc=casedesc[:128],
                    ecode=ecode,
                )
                created += 1
            if limit and len(rows) >= limit:
                break
        if limit and len(rows) >= limit:
            break
    return {"rows": rows, "created": created, "skipped": skipped, "errors": errors}


def _generate_custom(company, storecode, rule, base_date, dry_run, limit):
    start = (base_date or datetime.date.today()) + datetime.timedelta(days=int(rule.days_offset or 0))
    end = start + datetime.timedelta(days=6)
    qs = _candidate_vips(company, storecode)
    rows = []
    created = skipped = 0
    errors = []
    for vip in qs.iterator(chunk_size=500):
        ecode = _assignee_ecode(vip, rule)
        casedesc = render_template(rule.casedesc_template or DEFAULT_TEMPLATES[RULE_CUSTOM], vip, _base_extra(rule))
        preview = {
            "vipuuid": str(vip.uuid),
            "vname": vip.vname,
            "vcode": vip.vcode,
            "mtcode": vip.mtcode,
            "ecode": ecode,
            "planbegindate": start.isoformat(),
            "planfinishdate": end.isoformat(),
            "casedesc": casedesc,
        }
        if _has_case_same_start(company, storecode, vip, rule, start):
            skipped += 1
            continue
        rows.append(preview)
        if not dry_run:
            _create_case(
                company=company,
                storecode=storecode,
                vip=vip,
                rule=rule,
                start=start,
                end=end,
                casedesc=casedesc[:128],
                ecode=ecode,
            )
            created += 1
        if limit and len(rows) >= limit:
            break
    return {"rows": rows, "created": created, "skipped": skipped, "errors": errors}


GENERATORS = {
    RULE_BIRTHDAY: _generate_birthday,
    RULE_ANNIVERSARY: _generate_anniversary,
    RULE_TRANSACTION: _generate_transaction,
    RULE_LIFECYCLE: _generate_lifecycle,
    RULE_CUSTOM: _generate_custom,
}


def generate_crm_cases(
    company: str,
    storecode: str = "",
    *,
    rule: Optional[CrmRule] = None,
    rule_type: str = "",
    target_date: Optional[datetime.date] = None,
    dry_run: bool = True,
    limit: int = 500,
) -> Dict[str, Any]:
    """按单个规则生成任务。rule 为空时从启用的规则中挑选 rule_type。"""
    company = (company or "").strip()
    storecode = (storecode or "").strip()
    if not company:
        return {
            "error": "缺少 company",
            "dry_run": dry_run,
            "created": 0,
            "skipped": 0,
            "errors": ["缺少 company"],
            "previews": [],
        }

    qs = CrmRule.objects.filter(company=company, flag="Y", enabled="Y")
    if rule is not None:
        qs = qs.filter(uuid=rule.uuid)
    elif rule_type:
        qs = qs.filter(rule_type=rule_type)
    if storecode:
        qs = qs.filter(storecode__in=["", storecode])
    rules = list(qs.order_by("rule_name")[:20])
    if not rules:
        return {
            "error": "没有匹配的启用规则",
            "dry_run": dry_run,
            "created": 0,
            "skipped": 0,
            "errors": [],
            "previews": [],
        }

    total_created = 0
    total_skipped = 0
    all_errors = []
    all_previews = []
    for one in rules:
        gen = GENERATORS.get(one.rule_type)
        if not gen:
            all_errors.append("规则类型不支持: %s" % one.rule_type)
            continue
        try:
            result = gen(company, storecode, one, target_date, dry_run, limit)
            total_created += result["created"]
            total_skipped += result["skipped"]
            all_errors.extend(result["errors"])
            all_previews.extend(result["rows"])
            if not dry_run:
                one.last_run_at = datetime.datetime.now()
                one.last_run_summary = "生成 %d 条，跳过 %d 条" % (result["created"], result["skipped"])
                one.save(update_fields=["last_run_at", "last_run_summary", "last_modified"])
        except Exception as exc:  # noqa: BLE001
            all_errors.append("%s: %s" % (one.rule_name, exc))
    return {
        "company": company,
        "storecode": storecode or "*",
        "dry_run": dry_run,
        "created": total_created,
        "skipped": total_skipped,
        "errors": all_errors[:20],
        "previews": all_previews[:limit],
    }
