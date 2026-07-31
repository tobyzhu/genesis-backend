#coding = utf-8
"""VIP / 客户管理专用只读查询工具。"""

from __future__ import annotations

import datetime as pydatetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db.models import Count, DecimalField, F, Max, Sum, Value
from django.db.models.functions import Coalesce

from baseinfo.models import Empl, Vip
from cashier.models import Expense, Expvstoll
from crm.models import CrmCase, VipCaseDetail

from assistant.data_tools import MAX_ROWS, _date_window, _lim, _safe_float

BATCH_EXPORT_MAX = 5000

_DECIMAL_RATIO_FIELD = DecimalField(max_digits=8, decimal_places=4)
_DECIMAL_AMOUNT_FIELD = DecimalField(max_digits=18, decimal_places=2)
_DECIMAL_ZERO_RATIO = Value(Decimal("0"), output_field=_DECIMAL_RATIO_FIELD)


def _expense_ratio_amount_expr(*ratio_fields: str):
    """s_mount * ratio(s)，全部使用 Decimal 避免 ORM 混合类型错误。"""
    expr = None
    for ratio_field in ratio_fields:
        part = F("s_mount") * Coalesce(F(ratio_field), _DECIMAL_ZERO_RATIO)
        expr = part if expr is None else expr + part
    if expr is None:
        raise ValueError("至少需要一个 ratio 字段")
    return expr


def _sum_expense_ratio_amount(*ratio_fields: str) -> Sum:
    return Sum(_expense_ratio_amount_expr(*ratio_fields), output_field=_DECIMAL_AMOUNT_FIELD)

_VIP_DETAIL_FIELDS = (
    "uuid", "vcode", "vname", "mtcode", "telph", "sex", "birth", "indate",
    "viptype", "viplevel", "status", "tags", "source", "occupation",
    "ecode", "ecode2", "addr", "email", "wechat", "vdesc", "pinyin",
    "referrervcode", "create_time", "last_modified",
)


def _resolve_empl_names(company: str, ecodes: List[str]) -> Dict[str, str]:
    codes = {c.strip() for c in ecodes if c and c.strip()}
    if not codes:
        return {}
    return {
        (e.ecode or ""): (e.ename or e.ecode or "")
        for e in Empl.objects.filter(company=company, flag="Y", ecode__in=list(codes)).only("ecode", "ename")
    }


def _format_indate(val: Any) -> str:
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)


def _format_vsdate(val: Any) -> str:
    """expvstoll.vsdate 常为 YYYYMMDD 字符串。"""
    s = str(val or "").strip().replace("-", "")
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return str(val or "").strip()


def _vip_basic_info_fields(
    *,
    ecode: str = "",
    ecode2: str = "",
    indate: Any = None,
    birth: str = "",
    viplevel: str = "",
    empl_map: Dict[str, str],
) -> Dict[str, Any]:
    ec = (ecode or "").strip()
    ec2 = (ecode2 or "").strip()
    return {
        "ecode": ec,
        "adviser_name": empl_map.get(ec, ""),
        "ecode2": ec2,
        "therapist_name": empl_map.get(ec2, ""),
        "indate": _format_indate(indate),
        "birth": (birth or "").strip(),
        "viplevel": (viplevel or "").strip(),
    }


def tool_get_vip_detail(
    company: str, storecode: str, vipuuid: str = "", vcode: str = "", **_kwargs
) -> Dict[str, Any]:
    """按 vipuuid 或 vcode 查询会员档案详情。"""
    vu = (vipuuid or "").strip()
    vc = (vcode or "").strip()
    if not vu and not vc:
        return {"error": "需要 vipuuid 或 vcode"}
    qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    if vu:
        qs = qs.filter(uuid=vu)
    else:
        qs = qs.filter(vcode=vc)
    v = qs.first()
    if not v:
        return {"error": "未找到会员", "vipuuid": vu, "vcode": vc}
    empl_map = _resolve_empl_names(company, [v.ecode or "", v.ecode2 or ""])
    row: Dict[str, Any] = {"vipuuid": str(v.uuid)}
    for f in _VIP_DETAIL_FIELDS:
        val = getattr(v, f, None)
        if f in {"create_time", "last_modified"} and val is not None:
            row[f] = val.strftime("%Y-%m-%d %H:%M:%S")
        elif f == "uuid":
            continue
        else:
            row[f] = "" if val is None else str(val)
    row["adviser_name"] = empl_map.get((v.ecode or "").strip(), "")
    row["therapist_name"] = empl_map.get((v.ecode2 or "").strip(), "")
    return row


def tool_list_vip_transactions(
    company: str,
    storecode: str,
    vipuuid: str = "",
    days: int = 365,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> List[Dict[str, Any]]:
    """某会员的消费/成交记录（有效交易 valiflag='Y'）。"""
    vu = (vipuuid or "").strip()
    if not vu:
        return []
    from assistant.data_tools import _expvstoll_base_queryset

    lim = _lim(limit)
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    base_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=date_field)
    qs = base_qs.filter(vipuuid_id=vu).order_by("-create_time")[:lim]
    rows = []
    for x in qs:
        rows.append(
            {
                "uuid": str(x.uuid),
                "exptxserno": x.exptxserno or "",
                "totmount": str(x.totmount) if x.totmount is not None else "",
                "vsdate": x.vsdate or "",
                "cdate": x.cdate or "",
                "ttype": x.ttype or "",
                "ecode": x.ecode or "",
                "date_field": used_date_field,
                "create_time": x.create_time.strftime("%Y-%m-%d %H:%M:%S") if x.create_time else "",
            }
        )
    return rows


def tool_list_vip_crm_cases(
    company: str,
    storecode: str,
    vipuuid: str = "",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> List[Dict[str, Any]]:
    """某会员的 CRM 服务案例列表。"""
    vu = (vipuuid or "").strip()
    if not vu:
        return []
    lim = _lim(limit)
    qs = (
        CrmCase.objects.filter(company=company, storecode=storecode, flag="Y", vipuuid_id=vu)
        .select_related("vipuuid", "empl")
        .order_by("-create_time")[:lim]
    )
    rows = []
    for c in qs:
        empl = c.empl
        rows.append(
            {
                "case_uuid": str(c.uuid),
                "casetype": c.casetype or "",
                "viptype": c.viptype or "",
                "status": c.status or "",
                "casedesc": c.casedesc or "",
                "ecode": c.ecode or "",
                "empl_name": (empl.ename if empl else "") or "",
                "planbegindate": str(c.planbegindate) if c.planbegindate else "",
                "planfinishdate": str(c.planfinishdate) if c.planfinishdate else "",
                "finishedate": str(c.finishedate) if c.finishedate else "",
                "vsdate": str(c.vsdate) if c.vsdate else "",
            }
        )
    return rows


def tool_list_vip_communications(
    company: str,
    storecode: str,
    vipuuid: str = "",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> List[Dict[str, Any]]:
    """某会员的沟通/回访记录（vipcasedetail）。"""
    vu = (vipuuid or "").strip()
    if not vu:
        return []
    lim = _lim(limit)
    qs = (
        VipCaseDetail.objects.filter(company=company, storecode=storecode, flag="Y", vipuuid_id=vu)
        .order_by("-create_time")[:lim]
    )
    empl_map = _resolve_empl_names(company, [r.ecode or "" for r in qs] + [r.nextecode or "" for r in qs])
    rows = []
    for r in qs:
        rows.append(
            {
                "uuid": str(r.uuid),
                "casetype": r.casetype or "",
                "detail": r.detail or "",
                "detaildescription": (r.detaildescription or "")[:500],
                "ecode": r.ecode or "",
                "empl_name": empl_map.get((r.ecode or "").strip(), ""),
                "status": r.status or "",
                "nextdate": str(r.nextdate) if r.nextdate else "",
                "nextecode": r.nextecode or "",
                "next_empl_name": empl_map.get((r.nextecode or "").strip(), ""),
                "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else "",
            }
        )
    return rows


def tool_vip_consumption_summary(
    company: str,
    storecode: str,
    vipuuid: str = "",
    days: int = 365,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    **_kwargs,
) -> Dict[str, Any]:
    """某会员在时间段内的消费汇总。"""
    vu = (vipuuid or "").strip()
    if not vu:
        return {"error": "需要 vipuuid"}
    from assistant.data_tools import _expvstoll_base_queryset

    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    base_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=date_field)
    qs = base_qs.filter(vipuuid_id=vu)
    agg = qs.aggregate(trans_count=Count("uuid"), total_amount=Sum("totmount"))
    last = qs.order_by("-create_time").values("vsdate", "totmount", "create_time").first()
    return {
        "vipuuid": vu,
        "range": {"from": df, "to": dt, "date_field": used_date_field},
        "summary": {
            "trans_count": int(agg.get("trans_count") or 0),
            "total_amount": _safe_float(agg.get("total_amount")),
        },
        "last_transaction": {
            "vsdate": (last or {}).get("vsdate") or "",
            "totmount": str((last or {}).get("totmount") or ""),
            "create_time": (
                last["create_time"].strftime("%Y-%m-%d %H:%M:%S")
                if last and last.get("create_time")
                else ""
            ),
        },
    }


def _batch_lim(n: Any, default: int = BATCH_EXPORT_MAX) -> int:
    try:
        return max(1, min(int(n or default), BATCH_EXPORT_MAX))
    except (TypeError, ValueError):
        return min(default, BATCH_EXPORT_MAX)


def _parse_yyyymmdd_date(s: Any) -> Optional[pydatetime.date]:
    t = str(s or "").strip().replace("-", "")
    if len(t) == 8 and t.isdigit():
        try:
            return pydatetime.datetime.strptime(t, "%Y%m%d").date()
        except ValueError:
            return None
    return None


def _days_between(from_d: pydatetime.date, to_d: pydatetime.date) -> int:
    return max(0, (to_d - from_d).days)


def _risk_level(days_since: Optional[int], never_visited: bool, critical_days: int) -> str:
    if never_visited:
        return "never_visited"
    if days_since is None:
        return "unknown"
    if days_since >= critical_days:
        return "critical"
    return "warning"


def _fetch_trans_stats_map(company: str, storecode: str) -> Dict[str, Dict[str, Any]]:
    rows = (
        Expvstoll.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            valiflag="Y",
            vipuuid__isnull=False,
        )
        .values("vipuuid")
        .annotate(
            last_vsdate=Max("vsdate"),
            trans_count=Count("uuid"),
            lifetime_amount=Sum("totmount"),
        )
    )
    return {str(r["vipuuid"]): r for r in rows}


def _fetch_last_vsdate_map(
    company: str, storecode: str, vip_uuids: List[str]
) -> Dict[str, str]:
    """会员最后一次有效到店日期（valiflag='Y' 的 max(vsdate)）。"""
    uuids = [u for u in vip_uuids if u]
    if not uuids:
        return {}
    rows = (
        Expvstoll.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            valiflag="Y",
            vipuuid__in=uuids,
        )
        .values("vipuuid")
        .annotate(last_vsdate=Max("vsdate"))
    )
    return {str(r["vipuuid"]): (r.get("last_vsdate") or "") for r in rows}


def tool_vip_sleeping_alert(
    company: str,
    storecode: str,
    inactive_days: int = 90,
    critical_days: int = 180,
    viptype: str = "",
    min_lifetime_amount: float = 0,
    limit: int = MAX_ROWS,
    ecode: str = "",
    **_kwargs,
) -> Dict[str, Any]:
    """
    沉睡会员预警：在 inactive_days 内无有效消费（valiflag='Y'）的会员列表。
    risk_level: warning=超 inactive_days；critical=超 critical_days；never_visited=从未消费。
    """
    try:
        inactive_d = max(30, min(int(inactive_days or 90), 3650))
    except (TypeError, ValueError):
        inactive_d = 90
    try:
        critical_d = max(inactive_d, min(int(critical_days or 180), 3650))
    except (TypeError, ValueError):
        critical_d = max(180, inactive_d)
    lim = _lim(limit)
    min_amt = _safe_float(min_lifetime_amount)

    today = pydatetime.date.today()
    cutoff = (today - pydatetime.timedelta(days=inactive_d)).strftime("%Y%m%d")

    vip_qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    vt = (viptype or "").strip()
    if vt:
        vip_qs = vip_qs.filter(viptype=vt)
    adv = (ecode or "").strip()
    if adv:
        vip_qs = vip_qs.filter(ecode=adv)

    trans_map = _fetch_trans_stats_map(company, storecode)
    ecode_set: set[str] = set()
    for ec, ec2 in vip_qs.values_list("ecode", "ecode2").iterator(chunk_size=1000):
        if ec:
            ecode_set.add(ec.strip())
        if ec2:
            ecode_set.add(ec2.strip())
    empl_map = _resolve_empl_names(company, list(ecode_set))

    sleeping_rows: List[Dict[str, Any]] = []
    total_checked = 0
    for v in vip_qs.iterator(chunk_size=500):
        total_checked += 1
        vu = str(v.uuid)
        stats = trans_map.get(vu)
        last_vsdate = (stats or {}).get("last_vsdate") or ""
        lifetime_amount = _safe_float((stats or {}).get("lifetime_amount"))
        trans_count = int((stats or {}).get("trans_count") or 0)

        if min_amt > 0 and lifetime_amount < min_amt:
            continue

        never_visited = trans_count == 0 or not last_vsdate
        days_since: Optional[int] = None
        is_sleeping = False

        if never_visited:
            base_date = v.indate or (v.create_time.date() if v.create_time else None)
            if base_date:
                days_since = _days_between(base_date, today)
                is_sleeping = days_since >= inactive_d
            else:
                is_sleeping = True
        else:
            last_d = _parse_yyyymmdd_date(last_vsdate)
            if last_d:
                days_since = _days_between(last_d, today)
            is_sleeping = bool(last_vsdate < cutoff)

        if not is_sleeping:
            continue

        risk = _risk_level(days_since, never_visited, critical_d)
        sleeping_rows.append(
            {
                "vipuuid": vu,
                "vcode": v.vcode or "",
                "vname": v.vname or "",
                "mtcode": v.mtcode or "",
                "telph": v.telph or "",
                "viptype": v.viptype or "",
                "status": v.status or "",
                "viplevel": v.viplevel or "",
                "ecode": v.ecode or "",
                "adviser_name": empl_map.get((v.ecode or "").strip(), ""),
                "ecode2": v.ecode2 or "",
                "therapist_name": empl_map.get((v.ecode2 or "").strip(), ""),
                "last_vsdate": last_vsdate or "",
                "days_since_last_visit": days_since if days_since is not None else "",
                "lifetime_trans_count": trans_count,
                "lifetime_amount": lifetime_amount,
                "risk_level": risk,
                "indate": str(v.indate) if v.indate else "",
                "birth": v.birth or "",
            }
        )

    sleeping_rows.sort(
        key=lambda r: (
            0 if r.get("risk_level") == "critical" else (1 if r.get("risk_level") == "never_visited" else 2),
            -(int(r["days_since_last_visit"]) if str(r.get("days_since_last_visit") or "").isdigit() else 0),
        )
    )
    truncated = len(sleeping_rows) > lim
    sleeping_rows = sleeping_rows[:lim]

    risk_counts: Dict[str, int] = {"warning": 0, "critical": 0, "never_visited": 0}
    for r in sleeping_rows:
        rk = str(r.get("risk_level") or "warning")
        risk_counts[rk] = risk_counts.get(rk, 0) + 1

    return {
        "criteria": {
            "inactive_days": inactive_d,
            "critical_days": critical_d,
            "cutoff_vsdate": cutoff,
            "viptype": vt,
            "min_lifetime_amount": min_amt,
            "ecode": adv,
            "company": company,
            "storecode": storecode,
        },
        "summary": {
            "total_vip_checked": total_checked,
            "sleeping_count": len(sleeping_rows),
            "truncated": truncated,
            "risk_breakdown": risk_counts,
        },
        "sleeping_vips": sleeping_rows,
    }


def fetch_store_vips_for_export(
    company: str,
    storecode: str,
    limit: int = BATCH_EXPORT_MAX,
    viptype: str = "",
) -> List[Dict[str, Any]]:
    """批量导出门店会员列表（行数上限高于对话工具）。"""
    lim = _batch_lim(limit)
    qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    vt = (viptype or "").strip()
    if vt:
        qs = qs.filter(viptype=vt)
    qs = qs.order_by("-last_modified")[:lim]
    rows_out: List[Dict[str, Any]] = []
    ecode_set: set[str] = set()
    vip_list = list(qs)
    for v in vip_list:
        if v.ecode:
            ecode_set.add((v.ecode or "").strip())
        if v.ecode2:
            ecode_set.add((v.ecode2 or "").strip())
    empl_map = _resolve_empl_names(company, list(ecode_set))
    for v in vip_list:
        rows_out.append(
            {
                "vipuuid": str(v.uuid),
                "vcode": v.vcode or "",
                "vname": v.vname or "",
                "mtcode": v.mtcode or "",
                "telph": v.telph or "",
                "viptype": v.viptype or "",
                "status": v.status or "",
                "viplevel": v.viplevel or "",
                "ecode": v.ecode or "",
                "adviser_name": empl_map.get((v.ecode or "").strip(), ""),
                "ecode2": v.ecode2 or "",
                "therapist_name": empl_map.get((v.ecode2 or "").strip(), ""),
                "indate": str(v.indate) if v.indate else "",
                "source": v.source or "",
                "create_time": v.create_time.strftime("%Y-%m-%d %H:%M:%S") if v.create_time else "",
            }
        )
    return rows_out


def fetch_sleeping_vips_for_export(
    company: str,
    storecode: str,
    limit: int = BATCH_EXPORT_MAX,
    **kwargs,
) -> Dict[str, Any]:
    """批量导出沉睡会员（提高行数上限）。"""
    return tool_vip_sleeping_alert(
        company=company,
        storecode=storecode,
        limit=_batch_lim(limit),
        **kwargs,
    )


def _vip_top_consumption_ranking(
    company: str,
    storecode: str,
    *,
    metric: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
) -> Dict[str, Any]:
    """会员消费 TOP 排行（已结账有效交易；按 metric 口径聚合 expense 行）。"""
    from assistant.data_tools import _expvstoll_base_queryset

    specs: Dict[str, Dict[str, Any]] = {
        "cash": {
            "amount_field": "cash_amount",
            "metric_desc": "sum(expense.s_mount * expense.cashratio) on valiflag='Y' transactions",
            "annotate": _sum_expense_ratio_amount("cashratio"),
            "ttype": None,
        },
        "card": {
            "amount_field": "card_amount",
            "metric_desc": "sum(expense.s_mount * expense.cardratio) on valiflag='Y' transactions",
            "annotate": _sum_expense_ratio_amount("cardratio"),
            "ttype": None,
        },
        "send": {
            "amount_field": "send_amount",
            "metric_desc": "sum(expense.s_mount * expense.sendratio) on valiflag='Y' transactions",
            "annotate": _sum_expense_ratio_amount("sendratio"),
            "ttype": None,
        },
        "service": {
            "amount_field": "service_amount",
            "metric_desc": (
                "sum(expense.s_mount * (cashratio+cardratio)) where expense.ttype='S' "
                "on valiflag='Y' transactions (excludes sendratio)"
            ),
            "annotate": _sum_expense_ratio_amount("cashratio", "cardratio"),
            "ttype": "S",
        },
        "goods": {
            "amount_field": "goods_amount",
            "metric_desc": (
                "sum(expense.s_mount * (cashratio+cardratio)) where expense.ttype='G' "
                "on valiflag='Y' transactions (excludes sendratio)"
            ),
            "annotate": _sum_expense_ratio_amount("cashratio", "cardratio"),
            "ttype": "G",
        },
    }
    spec = specs.get((metric or "").strip().lower())
    if not spec:
        return {"error": f"不支持的 metric: {metric!r}，可选 cash/card/send/service/goods"}

    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    n = max(1, min(int(top_n or 30), 100))
    base_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=date_field)
    amount_field = spec["amount_field"]

    expense_filter: Dict[str, Any] = {
        "company": company,
        "storecode": storecode,
        "flag": "Y",
        "transuuid__in": base_qs.filter(vipuuid__isnull=False),
    }
    ttype_filter = spec.get("ttype")
    if ttype_filter:
        expense_filter["ttype"] = ttype_filter

    rows_qs = (
        Expense.objects.filter(**expense_filter)
        .values(
            "transuuid__vipuuid",
            "transuuid__vcode",
            "transuuid__vipuuid__vname",
            "transuuid__vipuuid__mtcode",
            "transuuid__vipuuid__telph",
            "transuuid__vipuuid__ecode",
            "transuuid__vipuuid__ecode2",
            "transuuid__vipuuid__indate",
            "transuuid__vipuuid__birth",
            "transuuid__vipuuid__viplevel",
        )
        .annotate(
            rank_amount=spec["annotate"],
            sale_amount=Sum("s_mount", output_field=_DECIMAL_AMOUNT_FIELD),
            line_count=Count("uuid"),
        )
        .order_by("-rank_amount")[:n]
    )

    rows_list = list(rows_qs)
    ecode_set: set[str] = set()
    for r in rows_list:
        for key in ("transuuid__vipuuid__ecode", "transuuid__vipuuid__ecode2"):
            ec = (r.get(key) or "").strip()
            if ec:
                ecode_set.add(ec)
    empl_map = _resolve_empl_names(company, list(ecode_set))
    vip_uuids = [str(r.get("transuuid__vipuuid") or "") for r in rows_list]
    last_visit_map = _fetch_last_vsdate_map(company, storecode, vip_uuids)

    top_vips: List[Dict[str, Any]] = []
    for r in rows_list:
        rank_amt = _safe_float(r.get("rank_amount"))
        vu = str(r.get("transuuid__vipuuid") or "")
        last_raw = last_visit_map.get(vu, "")
        profile = _vip_basic_info_fields(
            ecode=r.get("transuuid__vipuuid__ecode") or "",
            ecode2=r.get("transuuid__vipuuid__ecode2") or "",
            indate=r.get("transuuid__vipuuid__indate"),
            birth=r.get("transuuid__vipuuid__birth") or "",
            viplevel=r.get("transuuid__vipuuid__viplevel") or "",
            empl_map=empl_map,
        )
        top_vips.append(
            {
                "vipuuid": vu,
                "vcode": r.get("transuuid__vcode") or "",
                "vname": r.get("transuuid__vipuuid__vname") or "",
                "mtcode": r.get("transuuid__vipuuid__mtcode") or "",
                "telph": r.get("transuuid__vipuuid__telph") or "",
                **profile,
                "last_vsdate": last_raw,
                "last_visit_date": _format_vsdate(last_raw),
                amount_field: round(rank_amt, 2),
                "sale_amount": round(_safe_float(r.get("sale_amount")), 2),
                "expense_line_count": int(r.get("line_count") or 0),
            }
        )

    return {
        "range": {
            "from": df,
            "to": dt,
            "company": company,
            "storecode": storecode,
            "date_field": used_date_field,
            "days": days,
        },
        "metric": spec["metric_desc"],
        "ranking_type": metric,
        "summary": {"top_n": n, "result_count": len(top_vips)},
        "top_vips": top_vips,
    }


def tool_vip_top_cash_consumption(
    company: str,
    storecode: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
    **_kwargs,
) -> Dict[str, Any]:
    """
    会员现金消费 TOP（已结账有效交易；口径：Sum(expense.s_mount * expense.cashratio)）。
    优先于 readonly_sql 用于「现金消费最高/前 N 名会员」类问题。
    """
    return _vip_top_consumption_ranking(
        company,
        storecode,
        metric="cash",
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
    )


def tool_vip_top_card_consumption(
    company: str,
    storecode: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
    **_kwargs,
) -> Dict[str, Any]:
    """会员卡付消费 TOP（Sum(expense.s_mount * expense.cardratio)）。"""
    return _vip_top_consumption_ranking(
        company,
        storecode,
        metric="card",
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
    )


def tool_vip_top_send_consumption(
    company: str,
    storecode: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
    **_kwargs,
) -> Dict[str, Any]:
    """会员赠送类消费 TOP（Sum(expense.s_mount * expense.sendratio)）。"""
    return _vip_top_consumption_ranking(
        company,
        storecode,
        metric="send",
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
    )


def tool_vip_top_service_consumption(
    company: str,
    storecode: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
    **_kwargs,
) -> Dict[str, Any]:
    """会员服务类消费 TOP（expense.ttype='S'，Sum(s_mount*(cashratio+cardratio))，不含赠送）。"""
    return _vip_top_consumption_ranking(
        company,
        storecode,
        metric="service",
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
    )


def tool_vip_top_goods_consumption(
    company: str,
    storecode: str,
    days: int = 180,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 30,
    **_kwargs,
) -> Dict[str, Any]:
    """会员商品类消费 TOP（expense.ttype='G'，Sum(s_mount*(cashratio+cardratio))，不含赠送）。"""
    return _vip_top_consumption_ranking(
        company,
        storecode,
        metric="goods",
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
    )


def _resolve_vip(
    company: str,
    storecode: str,
    *,
    telph: str = "",
    vipuuid: str = "",
    vcode: str = "",
) -> Optional[Vip]:
    """按手机号、vipuuid 或 vcode 定位会员（只读）。"""
    qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    vu = (vipuuid or "").strip()
    vc = (vcode or "").strip()
    tp = (telph or "").strip()
    if vu:
        return qs.filter(uuid=vu).first()
    if vc:
        return qs.filter(vcode=vc).first()
    if tp:
        exact = qs.filter(telph=tp).first()
        if exact:
            return exact
        partial = qs.filter(telph__icontains=tp).order_by("-last_modified").first()
        if partial:
            return partial
        return qs.filter(mtcode__icontains=tp).order_by("-last_modified").first()
    return None


def _vip_visit_stats(company: str, storecode: str, vipuuid: str) -> Dict[str, Any]:
    """会员有效到店统计（valiflag='Y'，按 vsdate 去重计次）。"""
    rows = (
        Expvstoll.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            valiflag="Y",
            vipuuid_id=vipuuid,
        )
        .values("vsdate")
        .annotate(trans_count=Count("uuid"), amount=Sum("totmount"))
        .order_by("vsdate")
    )
    visit_dates: List[pydatetime.date] = []
    lifetime_amount = 0.0
    lifetime_trans = 0
    for r in rows:
        vd = _parse_yyyymmdd_date(r.get("vsdate"))
        if vd:
            visit_dates.append(vd)
        lifetime_trans += int(r.get("trans_count") or 0)
        lifetime_amount += _safe_float(r.get("amount"))

    avg_interval: Optional[float] = None
    if len(visit_dates) >= 2:
        gaps = [(visit_dates[i + 1] - visit_dates[i]).days for i in range(len(visit_dates) - 1)]
        avg_interval = round(sum(gaps) / len(gaps), 1)

    last_vsdate = ""
    last_visit_date = ""
    days_since: Optional[int] = None
    if visit_dates:
        last_d = visit_dates[-1]
        last_vsdate = last_d.strftime("%Y%m%d")
        last_visit_date = last_d.strftime("%Y-%m-%d")
        days_since = _days_between(last_d, pydatetime.date.today())

    return {
        "visit_count": len(visit_dates),
        "lifetime_trans_count": lifetime_trans,
        "lifetime_amount": round(lifetime_amount, 2),
        "first_visit_date": visit_dates[0].strftime("%Y-%m-%d") if visit_dates else "",
        "last_vsdate": last_vsdate,
        "last_visit_date": last_visit_date,
        "days_since_last_visit": days_since,
        "avg_days_between_visits": avg_interval,
    }


def _vip_preferred_items(
    company: str,
    storecode: str,
    vipuuid: str,
    *,
    days: int = 365,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """会员偏好项目（按 expense 金额 TOP）。"""
    from assistant.data_tools import _enrich_expense_items, _expvstoll_base_queryset

    df, dt = _date_window(days=days)
    n = max(1, min(int(top_n or 5), 20))
    base_qs, _used = _expvstoll_base_queryset(company, storecode, df, dt)
    trans_qs = base_qs.filter(vipuuid_id=vipuuid)
    iqs = (
        Expense.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            transuuid__in=trans_qs,
        )
        .values("srvcode", "ttype")
        .annotate(
            line_count=Count("uuid"),
            total_qty=Sum("s_qty"),
            total_amount=Sum("s_mount"),
        )
        .order_by("-total_amount")[:n]
    )
    raw = [
        {
            "srvcode": r.get("srvcode") or "",
            "ttype": r.get("ttype") or "",
            "line_count": int(r.get("line_count") or 0),
            "total_qty": round(_safe_float(r.get("total_qty")), 2),
            "total_amount": round(_safe_float(r.get("total_amount")), 2),
        }
        for r in iqs
    ]
    return _enrich_expense_items(company, storecode, raw)


def _period_consumption(
    company: str,
    storecode: str,
    vipuuid: str,
    *,
    days: int,
    offset_days: int = 0,
) -> Dict[str, Any]:
    """某会员在 [today-offset-days, today-offset-days+days] 区间内的消费。"""
    today = pydatetime.date.today()
    end_d = today - pydatetime.timedelta(days=offset_days)
    start_d = end_d - pydatetime.timedelta(days=max(1, days) - 1)
    df = start_d.strftime("%Y%m%d")
    dt = end_d.strftime("%Y%m%d")
    qs = Expvstoll.objects.filter(
        company=company,
        storecode=storecode,
        flag="Y",
        valiflag="Y",
        vipuuid_id=vipuuid,
        vsdate__gte=df,
        vsdate__lte=dt,
    )
    agg = qs.aggregate(trans_count=Count("uuid"), total_amount=Sum("totmount"))
    visit_days = qs.values("vsdate").distinct().count()
    return {
        "from": df,
        "to": dt,
        "visit_days": int(visit_days or 0),
        "trans_count": int(agg.get("trans_count") or 0),
        "total_amount": round(_safe_float(agg.get("total_amount")), 2),
    }


def tool_vip_profile(
    company: str,
    storecode: str,
    telph: str = "",
    vipuuid: str = "",
    vcode: str = "",
    days: int = 365,
    top_n: int = 5,
    **_kwargs,
) -> Dict[str, Any]:
    """
    客户画像：消费总额、到店频次、偏好项目、上次到店时间。
    输入 telph（手机号）、vipuuid 或 vcode 之一。
    """
    v = _resolve_vip(company, storecode, telph=telph, vipuuid=vipuuid, vcode=vcode)
    if not v:
        return {
            "error": "未找到会员",
            "telph": (telph or "").strip(),
            "vipuuid": (vipuuid or "").strip(),
            "vcode": (vcode or "").strip(),
        }

    vu = str(v.uuid)
    empl_map = _resolve_empl_names(company, [v.ecode or "", v.ecode2 or ""])
    visit = _vip_visit_stats(company, storecode, vu)
    preferred = _vip_preferred_items(company, storecode, vu, days=days, top_n=top_n)

    profile_basic = {
        "vipuuid": vu,
        "vcode": v.vcode or "",
        "vname": v.vname or "",
        "telph": v.telph or "",
        "mtcode": v.mtcode or "",
        "viptype": v.viptype or "",
        "viplevel": v.viplevel or "",
        "status": v.status or "",
        "indate": _format_indate(v.indate),
        "ecode": (v.ecode or "").strip(),
        "adviser_name": empl_map.get((v.ecode or "").strip(), ""),
        "ecode2": (v.ecode2 or "").strip(),
        "therapist_name": empl_map.get((v.ecode2 or "").strip(), ""),
    }

    return {
        "profile": profile_basic,
        "consumption": {
            "lifetime_amount": visit["lifetime_amount"],
            "lifetime_trans_count": visit["lifetime_trans_count"],
            "visit_count": visit["visit_count"],
            "avg_days_between_visits": visit["avg_days_between_visits"],
            "first_visit_date": visit["first_visit_date"],
            "last_visit_date": visit["last_visit_date"],
            "days_since_last_visit": visit["days_since_last_visit"],
        },
        "preferred_items": {
            "window_days": max(1, min(int(days or 365), 3650)),
            "items": preferred,
        },
    }


def _churn_trend_label(recent: float, prior: float) -> str:
    if prior <= 0 and recent <= 0:
        return "no_activity"
    if prior <= 0:
        return "increasing"
    ratio = recent / prior
    if ratio >= 1.1:
        return "increasing"
    if ratio <= 0.7:
        return "declining"
    return "stable"


def _churn_risk_level(
    *,
    days_since: Optional[int],
    never_visited: bool,
    inactive_days: int,
    critical_days: int,
    amount_trend: str,
    visit_trend: str,
) -> str:
    if never_visited:
        return "never_visited"
    if days_since is None:
        return "unknown"
    declining = amount_trend == "declining" or visit_trend == "declining"
    if days_since >= critical_days or (days_since >= inactive_days and declining):
        return "high"
    if days_since >= inactive_days or declining:
        return "medium"
    if days_since >= max(30, inactive_days // 2):
        return "low"
    return "active"


def tool_vip_churn_risk(
    company: str,
    storecode: str,
    telph: str = "",
    vipuuid: str = "",
    vcode: str = "",
    inactive_days: int = 90,
    critical_days: int = 180,
    trend_days: int = 90,
    **_kwargs,
) -> Dict[str, Any]:
    """
    单客流失风险：超 N 天未到店、近/前段消费与到店频次对比。
    输入 telph、vipuuid 或 vcode 之一。
    """
    try:
        inactive_d = max(30, min(int(inactive_days or 90), 3650))
    except (TypeError, ValueError):
        inactive_d = 90
    try:
        critical_d = max(inactive_d, min(int(critical_days or 180), 3650))
    except (TypeError, ValueError):
        critical_d = max(180, inactive_d)
    try:
        trend_d = max(30, min(int(trend_days or 90), 365))
    except (TypeError, ValueError):
        trend_d = 90

    v = _resolve_vip(company, storecode, telph=telph, vipuuid=vipuuid, vcode=vcode)
    if not v:
        return {
            "error": "未找到会员",
            "telph": (telph or "").strip(),
            "vipuuid": (vipuuid or "").strip(),
            "vcode": (vcode or "").strip(),
        }

    vu = str(v.uuid)
    visit = _vip_visit_stats(company, storecode, vu)
    recent = _period_consumption(company, storecode, vu, days=trend_d, offset_days=0)
    prior = _period_consumption(company, storecode, vu, days=trend_d, offset_days=trend_d)

    never_visited = visit["visit_count"] == 0
    days_since = visit["days_since_last_visit"]
    amount_trend = _churn_trend_label(recent["total_amount"], prior["total_amount"])
    visit_trend = _churn_trend_label(float(recent["visit_days"]), float(prior["visit_days"]))
    risk = _churn_risk_level(
        days_since=days_since if isinstance(days_since, int) else None,
        never_visited=never_visited,
        inactive_days=inactive_d,
        critical_days=critical_d,
        amount_trend=amount_trend,
        visit_trend=visit_trend,
    )

    amount_change_pct: Optional[float] = None
    if prior["total_amount"] > 0:
        amount_change_pct = round(
            (recent["total_amount"] - prior["total_amount"]) / prior["total_amount"] * 100,
            1,
        )

    visit_change_pct: Optional[float] = None
    if prior["visit_days"] > 0:
        visit_change_pct = round(
            (recent["visit_days"] - prior["visit_days"]) / prior["visit_days"] * 100,
            1,
        )

    risk_factors: List[str] = []
    if never_visited:
        risk_factors.append("从未有效消费")
    elif isinstance(days_since, int) and days_since >= inactive_d:
        risk_factors.append(f"已 {days_since} 天未到店（阈值 {inactive_d} 天）")
    if amount_trend == "declining":
        risk_factors.append(f"近 {trend_d} 天消费较前一周期下降")
    if visit_trend == "declining":
        risk_factors.append(f"近 {trend_d} 天到店频次较前一周期下降")

    return {
        "vipuuid": vu,
        "vcode": v.vcode or "",
        "vname": v.vname or "",
        "telph": v.telph or "",
        "risk_level": risk,
        "risk_factors": risk_factors,
        "criteria": {
            "inactive_days": inactive_d,
            "critical_days": critical_d,
            "trend_window_days": trend_d,
        },
        "last_visit": {
            "last_visit_date": visit["last_visit_date"],
            "days_since_last_visit": days_since,
        },
        "trend": {
            "recent_period": recent,
            "prior_period": prior,
            "amount_trend": amount_trend,
            "visit_trend": visit_trend,
            "amount_change_pct": amount_change_pct,
            "visit_change_pct": visit_change_pct,
        },
        "lifetime": {
            "lifetime_amount": visit["lifetime_amount"],
            "visit_count": visit["visit_count"],
        },
    }


VIP_ONLY_REGISTRY = {
    "vip_top_cash_consumption": tool_vip_top_cash_consumption,
    "vip_top_card_consumption": tool_vip_top_card_consumption,
    "vip_top_send_consumption": tool_vip_top_send_consumption,
    "vip_top_service_consumption": tool_vip_top_service_consumption,
    "vip_top_goods_consumption": tool_vip_top_goods_consumption,
    "vip_sleeping_alert": tool_vip_sleeping_alert,
    "get_vip_detail": tool_get_vip_detail,
    "list_vip_transactions": tool_list_vip_transactions,
    "list_vip_crm_cases": tool_list_vip_crm_cases,
    "list_vip_communications": tool_list_vip_communications,
    "vip_consumption_summary": tool_vip_consumption_summary,
    "vip_profile": tool_vip_profile,
    "vip_churn_risk": tool_vip_churn_risk,
}

VIP_ONLY_CATALOG_TEXT = """
- vip_top_cash_consumption：会员现金消费 TOP（已结账；Sum(expense.s_mount*cashratio)）。args: {"days":180}，可加 {"top_n":30} 等。结果含 indate（入会日期）、last_visit_date（末次到店，valiflag=Y 的 max vsdate）及顾问/护理师等档案字段。
- vip_top_card_consumption：会员卡付消费 TOP（Sum(expense.s_mount*cardratio)）。args 同上。用户问「卡付/刷卡/储值卡消费最高」时用本工具。
- vip_top_send_consumption：会员赠送类消费 TOP（Sum(expense.s_mount*sendratio)）。args 同上。用户问「赠送/赠金消费最高」时用本工具。
- vip_top_service_consumption：会员服务类消费 TOP（ttype='S'，Sum(s_mount*(cashratio+cardratio))，不含赠送）。args 同上。
- vip_top_goods_consumption：会员商品类消费 TOP（ttype='G'，Sum(s_mount*(cashratio+cardratio))，不含赠送）。args 同上。
- 以上排行工具均仅统计已结账 valiflag='Y' 交易，不要用 readonly_sql 替代。
- vip_sleeping_alert：沉睡会员预警（N 天内无有效消费）。args: {"inactive_days":90}，可加 {"critical_days":180}、{"viptype":"10"}（仅会员）、{"min_lifetime_amount":0}、{"ecode":"顾问工号"}、{"limit":80}。
- get_vip_detail：会员档案详情。args: {"vipuuid":"uuid"} 或 {"vcode":"会员号"}。
- list_vip_transactions：某会员消费/成交记录（仅 valiflag='Y'）。args: {"vipuuid":"uuid"}，可加 {"days":365}、{"date_field":"vsdate|cdate"}。
- vip_consumption_summary：某会员消费汇总（笔数/总额/最近一笔）。args: 同上。
- list_vip_crm_cases：某会员 CRM 服务案例。args: {"vipuuid":"uuid"}。
- list_vip_communications：某会员沟通/回访记录（vipcasedetail）。args: {"vipuuid":"uuid"}。
- vip_profile：客户画像（消费总额、到店频次、偏好项目、上次到店）。args: {"telph":"138..."} 或 {"vipuuid":"..."} / {"vcode":"..."}；可加 {"days":365}、{"top_n":5} 控制偏好项目窗口。
- vip_churn_risk：单客流失风险（超 N 天未到店、消费/到店频次下降趋势）。args: 同上；可加 {"inactive_days":90}、{"critical_days":180}、{"trend_days":90}。
""".strip()
