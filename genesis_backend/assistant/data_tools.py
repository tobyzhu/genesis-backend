#coding = utf-8
"""Read-only data access for the assistant. Keep queries bounded and explicit."""

from __future__ import annotations

import datetime as pydatetime
import json
from typing import Any, Callable, Dict, List, Tuple

from django.apps import apps
from django.db.models import Count, Q, Sum

from adviser.models import Cardinfo, ExpvstollHung
from baseinfo.models import Cardtype, Empl, Goods, Paymode, Serviece, Vip
from cashier.models import Expense, Expvstoll, Toll

from report.store_dimension_sales import compute_store_dimension_sales_summary

from assistant.sql_readonly import run_readonly_select

MAX_ROWS = 80
MAX_CATALOG = 400

_TABLE_SQL_HINTS: Dict[str, List[str]] = {
    "vip": [
        "主键列 uuid（vip 表上没有 vipuuid 列）",
        "会员号 vcode；手机 mtcode / telph",
        "其它表的外键列 vipuuid 指向本表 uuid",
    ],
    "expvstoll": [
        "主键 uuid；外键 vipuuid → vip.uuid",
        "已结账正式成交；有效交易 valiflag='Y'；日期 vsdate / cdate",
        "成交总金额 totmount 在本表；无 s_mount/cashratio（勿用 e.s_mount）",
        "付款在 toll（transuuid → 本表 uuid）",
    ],
    "expvstoll_hung": [
        "开单未结账挂单主表；仍在 hung 表即未结账",
        "服务流程状态 psstatus_hung（与结账无直接对应）",
        "明细见 expense_hung",
    ],
    "expense_hung": [
        "开单未结账明细；外键关联 expvstoll_hung",
        "未结账场景勿与 expense 混用",
    ],
    "expense": [
        "已结账成交明细；transuuid → expvstoll.uuid",
        "项目金额 S_MOUNT（模型 s_mount）；cashratio/cardratio/sendratio 仅在本表",
        "按会员/现金折算统计须 JOIN expvstoll（取 vsdate/vipuuid）再 JOIN vip",
    ],
    "toll": [
        "主键 uuid；外键 transuuid → expvstoll.uuid（不是 expvstolluuid）",
        "付款 pcode、金额 totmount",
    ],
    "cardinfo": ["外键 vipuuid → vip.uuid；卡号 ccode"],
    "paymode": ["付款方式 pcode；iscash='1' 现金类"],
    "crmcase": ["外键 vipuuid → vip.uuid"],
    "vipcasedetail": ["外键 vipuuid → vip.uuid"],
}


def _describe_table_sql_hints(db_table: str, model: Any) -> List[str]:
    hints = list(_TABLE_SQL_HINTS.get(db_table.lower(), []))
    pk = model._meta.pk
    if pk is not None:
        col = getattr(pk, "column", None) or pk.name
        hints.insert(0, f"主键列 {col}")
    return hints


def _format_hung_order_time(h: ExpvstollHung) -> str:
    vd = (h.vsdate_hung or "").strip()
    vt = (h.vstime_hung or "").strip()
    if len(vd) == 8 and vt:
        vt_norm = vt.ljust(6, "0")[:6]
        try:
            dt = pydatetime.datetime.strptime(vd + vt_norm, "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            try:
                dt = pydatetime.datetime.strptime(vd + vt_norm[:4] + "00", "%Y%m%d%H%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass
    if getattr(h, "create_time", None):
        return h.create_time.strftime("%Y-%m-%d %H:%M")
    return vd or ""


def _lim(n: Any, default: int = MAX_ROWS) -> int:
    try:
        return max(1, min(int(n or default), MAX_ROWS))
    except (TypeError, ValueError):
        return default


def _norm_yyyymmdd(s: Any) -> str:
    t = str(s or "").strip().replace("-", "")
    if len(t) == 8 and t.isdigit():
        return t
    return ""


def _date_window(days: int = 90, date_from: str = "", date_to: str = "") -> tuple[str, str]:
    df = _norm_yyyymmdd(date_from)
    dt = _norm_yyyymmdd(date_to)
    if df and dt and df <= dt:
        return df, dt
    if df and not dt:
        return df, pydatetime.datetime.now().strftime("%Y%m%d")
    if dt and not df:
        return "19000101", dt
    try:
        d = max(1, min(int(days or 90), 3650))
    except (TypeError, ValueError):
        d = 90
    to_dt = pydatetime.datetime.now()
    from_dt = to_dt - pydatetime.timedelta(days=d)
    return from_dt.strftime("%Y%m%d"), to_dt.strftime("%Y%m%d")


def _safe_float(v: Any) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_vsdate_to_date(vsdate: str):
    t = _norm_yyyymmdd(vsdate)
    if not t:
        return None
    try:
        return pydatetime.datetime.strptime(t, "%Y%m%d").date()
    except ValueError:
        return None


def _group_key_by_granularity(vsdate: str, granularity: str) -> str:
    d = _parse_vsdate_to_date(vsdate)
    if not d:
        return ""
    g = (granularity or "day").strip().lower()
    if g == "month":
        return d.strftime("%Y-%m")
    if g == "week":
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    return d.strftime("%Y-%m-%d")


def _expvstoll_base_queryset(
    company: str,
    storecode: str,
    df: str,
    dt: str,
    date_field: str = "vsdate",
):
    field = (date_field or "vsdate").strip().lower()
    if field not in {"vsdate", "cdate"}:
        field = "vsdate"
    kwargs = {
        "company": company,
        "storecode": storecode,
        "flag": "Y",
        "valiflag": "Y",
        f"{field}__gte": df,
        f"{field}__lte": dt,
    }
    return Expvstoll.objects.filter(**kwargs), field


def _enrich_expense_items(company: str, storecode: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    s_codes = {str(r.get("srvcode") or "").strip() for r in rows if (r.get("ttype") or "") == "S" and (r.get("srvcode") or "")}
    g_codes = {str(r.get("srvcode") or "").strip() for r in rows if (r.get("ttype") or "") == "G" and (r.get("srvcode") or "")}
    c_codes = {str(r.get("srvcode") or "").strip() for r in rows if (r.get("ttype") or "") in {"C", "I"} and (r.get("srvcode") or "")}

    s_map = {}
    if s_codes:
        for x in Serviece.objects.filter(company=company, storecode=storecode, flag="Y", svrcdoe__in=list(s_codes)).only("svrcdoe", "svrname"):
            s_map[x.svrcdoe] = x.svrname or x.svrcdoe

    g_map = {}
    if g_codes:
        for x in Goods.objects.filter(company=company, storecode=storecode, flag="Y", gcode__in=list(g_codes)).only("gcode", "gname"):
            g_map[x.gcode] = x.gname or x.gcode

    c_map = {}
    cardtype_codes = set()
    if c_codes:
        for x in Cardinfo.objects.filter(company=company, storecode=storecode, flag="Y", ccode__in=list(c_codes)).only("ccode", "cardtype"):
            c_map[x.ccode] = x.cardtype or ""
            if x.cardtype:
                cardtype_codes.add(x.cardtype)

    ct_map = {}
    if cardtype_codes:
        for x in Cardtype.objects.filter(company=company, storecode=storecode, cardtype__in=list(cardtype_codes)).only("cardtype", "cardname"):
            ct_map[x.cardtype] = x.cardname or x.cardtype

    out = []
    for r in rows:
        t = (r.get("ttype") or "").strip()
        code = str(r.get("srvcode") or "").strip()
        rr = dict(r)
        if t == "S":
            rr["source_table"] = "serviece"
            rr["item_name"] = s_map.get(code) or code
        elif t == "G":
            rr["source_table"] = "goods"
            rr["item_name"] = g_map.get(code) or code
        elif t in {"C", "I"}:
            rr["source_table"] = "cardinfo"
            rr["card_code"] = code
            ct = c_map.get(code) or ""
            rr["cardtype"] = ct
            rr["cardtype_name"] = ct_map.get(ct) or ct
            rr["item_name"] = rr.get("cardtype_name") or ct or code
        else:
            rr["source_table"] = ""
            rr["item_name"] = code
        out.append(rr)
    return out


def tool_list_unsettled_guests(company: str, storecode: str, **_kwargs) -> List[Dict[str, Any]]:
    """当前门店开单未结账（expvstoll_hung 有效挂单）列表。"""
    qs = (
        ExpvstollHung.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            valiflag_hung="Y",
        )
        .select_related("vipuuid")
        .annotate(item_count=Count("expensehung", filter=Q(expensehung__flag="Y")))
        .order_by("-create_time")[:MAX_ROWS]
    )
    ecodes = []
    for h in qs:
        e = (h.ecode_hung or "").strip()
        if e:
            ecodes.append(e)
    empl_by_ecode = {}
    if ecodes:
        for em in Empl.objects.filter(company=company, ecode__in=list(set(ecodes))).only(
            "ecode", "ename", "cname"
        ):
            empl_by_ecode[em.ecode] = (em.ename or em.cname or em.ecode or "").strip()
    rows = []
    for h in qs:
        vip = h.vipuuid
        tm = h.totmount_hung
        try:
            tot = float(tm) if tm is not None else 0
        except (TypeError, ValueError):
            tot = 0
        ecode = (h.ecode_hung or "").strip()
        empl_name = empl_by_ecode.get(ecode) if ecode else ""
        if ecode and not empl_name:
            empl_name = ecode
        ic = getattr(h, "item_count", 0) or 0
        rows.append(
            {
                "hunguuid": str(h.uuid),
                "exptxserno": h.exptxserno_hung or "",
                "psstatus_hung": h.psstatus_hung or "",
                "vsdate": h.vsdate_hung or "",
                "totmount": tot,
                "ttype": h.ttype_hung or "",
                "vipuuid": str(vip.uuid) if vip else "",
                "vname": (vip.vname if vip else "") or "",
                "vcode": (vip.vcode if vip else "") or "",
                "mtcode": (vip.mtcode if vip else "") or "",
                "item_count": int(ic),
                "order_time": _format_hung_order_time(h),
                "ecode_hung": ecode,
                "order_empl": empl_name,
            }
        )
    return rows


def tool_search_vips(
    company: str, storecode: str, keyword: str = "", limit: int = MAX_ROWS, **_kwargs
) -> List[Dict[str, Any]]:
    kw = (keyword or "").strip()
    if not kw:
        return []
    lim = _lim(limit)
    q = Q(vname__icontains=kw) | Q(vcode__icontains=kw) | Q(mtcode__icontains=kw) | Q(telph__icontains=kw)
    qs = (
        Vip.objects.filter(company=company, storecode=storecode, flag="Y")
        .filter(q)
        .order_by("-last_modified")[:lim]
    )
    return [
        {
            "vipuuid": str(v.uuid),
            "vname": v.vname or "",
            "vcode": v.vcode or "",
            "mtcode": v.mtcode or "",
            "telph": v.telph or "",
            "storecode": v.storecode or "",
        }
        for v in qs
    ]


def tool_list_vip_cards(
    company: str, storecode: str, vipuuid: str = "", limit: int = MAX_ROWS, **_kwargs
) -> List[Dict[str, Any]]:
    vu = (vipuuid or "").strip()
    if not vu:
        return []
    lim = _lim(limit)
    qs = (
        Cardinfo.objects.filter(company=company, storecode=storecode, flag="Y", vipuuid_id=vu)
        .select_related("cardtypeuuid")
        .order_by("-create_time")[:lim]
    )
    rows = []
    for c in qs:
        ct_name = ""
        if c.cardtypeuuid_id:
            ct = c.cardtypeuuid
            ct_name = (getattr(ct, "cardname", None) or getattr(ct, "cardtype", None) or "") or ""
        rows.append(
            {
                "ccode": c.ccode or "",
                "cardtype": c.cardtype or "",
                "cardtype_name": ct_name,
                "leftmoney": str(c.leftmoney) if c.leftmoney is not None else "",
                "leftqty": str(c.leftqty) if c.leftqty is not None else "",
                "status": c.status or "",
                "storecode": c.storecode or "",
            }
        )
    return rows


def tool_search_cards(
    company: str,
    storecode: str,
    keyword: str = "",
    exact_ccode: str = "",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> List[Dict[str, Any]]:
    ex = (exact_ccode or "").strip()
    kw = (keyword or "").strip()
    if not ex and not kw:
        return []
    lim = _lim(limit)
    qs = Cardinfo.objects.filter(company=company, storecode=storecode, flag="Y")
    if ex:
        qs = qs.filter(ccode=ex)
    else:
        qs = qs.filter(ccode__icontains=kw)
    qs = qs.select_related("vipuuid", "cardtypeuuid").order_by("-create_time")[:lim]
    rows = []
    for c in qs:
        vip = c.vipuuid
        ct_name = ""
        if c.cardtypeuuid_id:
            ct = c.cardtypeuuid
            ct_name = (getattr(ct, "cardname", None) or getattr(ct, "cardtype", None) or "") or ""
        rows.append(
            {
                "ccode": c.ccode or "",
                "cardtype": c.cardtype or "",
                "cardtype_name": ct_name,
                "leftmoney": str(c.leftmoney) if c.leftmoney is not None else "",
                "leftqty": str(c.leftqty) if c.leftqty is not None else "",
                "status": c.status or "",
                "storecode": c.storecode or "",
                "vipuuid": str(vip.uuid) if vip else "",
                "vname": (vip.vname if vip else "") or "",
                "vcode": (vip.vcode if vip else "") or "",
            }
        )
    return rows


def tool_list_store_vips(
    company: str, storecode: str, limit: int = MAX_ROWS, **_kwargs
) -> List[Dict[str, Any]]:
    lim = _lim(limit)
    qs = (
        Vip.objects.filter(company=company, storecode=storecode, flag="Y")
        .order_by("-last_modified")[:lim]
    )
    return [
        {
            "vipuuid": str(v.uuid),
            "vname": v.vname or "",
            "vcode": v.vcode or "",
            "mtcode": v.mtcode or "",
            "telph": v.telph or "",
        }
        for v in qs
    ]


def tool_list_employees(
    company: str, storecode: str = "", limit: int = MAX_ROWS, **_kwargs
) -> List[Dict[str, Any]]:
    lim = _lim(limit)
    qs = Empl.objects.filter(company=company, flag="Y")
    sc = (storecode or "").strip()
    if sc:
        qs = qs.filter(storecode=sc)
    qs = qs.order_by("ecode")[:lim]
    return [
        {
            "ecode": e.ecode or "",
            "ename": e.ename or "",
            "cname": e.cname or "",
            "storecode": e.storecode or "",
            "status": e.status or "",
        }
        for e in qs
    ]


def tool_list_recent_expvstoll(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> List[Dict[str, Any]]:
    lim = _lim(limit)
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    base_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=date_field)
    qs = base_qs.select_related("vipuuid").order_by("-create_time")[:lim]
    rows = []
    for x in qs:
        vip = x.vipuuid
        rows.append(
            {
                "uuid": str(x.uuid),
                "exptxserno": x.exptxserno or "",
                "vcode": x.vcode or "",
                "vipuuid": str(vip.uuid) if vip else "",
                "vname": (vip.vname if vip else "") or "",
                "totmount": str(x.totmount) if x.totmount is not None else "",
                "vsdate": x.vsdate or "",
                "ttype": x.ttype or "",
                "status": x.status or "",
                "valiflag": x.valiflag or "",
                "date_field": used_date_field,
                "create_time": x.create_time.strftime("%Y-%m-%d %H:%M:%S") if x.create_time else "",
            }
        )
    return rows


def tool_cashier_trade_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    **_kwargs,
) -> Dict[str, Any]:
    """按 company/storecode 统计交易主表（expvstoll）概览。"""
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=_kwargs.get("date_field", "vsdate"))
    agg = qs.aggregate(
        trans_count=Count("uuid"),
        total_mount=Sum("totmount"),
    )
    trans_count = int(agg.get("trans_count") or 0)
    total_mount = float(agg.get("total_mount") or 0)
    avg_mount = round(total_mount / trans_count, 2) if trans_count else 0

    by_ttype = []
    tqs = (
        qs.values("ttype")
        .annotate(cnt=Count("uuid"), amt=Sum("totmount"))
        .order_by("-amt")[:20]
    )
    for r in tqs:
        by_ttype.append(
            {
                "ttype": r.get("ttype") or "",
                "count": int(r.get("cnt") or 0),
                "amount": float(r.get("amt") or 0),
            }
        )

    by_empl = []
    eqs = (
        qs.values("ecode")
        .annotate(cnt=Count("uuid"), amt=Sum("totmount"))
        .order_by("-amt")[:20]
    )
    for r in eqs:
        by_empl.append(
            {
                "ecode": r.get("ecode") or "",
                "count": int(r.get("cnt") or 0),
                "amount": float(r.get("amt") or 0),
            }
        )

    return {
        "range": {"from": df, "to": dt, "company": company, "storecode": storecode, "date_field": used_date_field},
        "summary": {
            "trans_count": trans_count,
            "total_mount": round(total_mount, 2),
            "avg_mount": avg_mount,
        },
        "by_ttype": by_ttype,
        "by_empl": by_empl,
    }


def tool_cashier_paymode_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    **_kwargs,
) -> Dict[str, Any]:
    """按付款方式统计 toll（金额/笔数），并补齐 paymode 名称与 iscash。"""
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    trans_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=_kwargs.get("date_field", "vsdate"))
    qs = Toll.objects.filter(
        company=company,
        storecode=storecode,
        flag="Y",
        transuuid__in=trans_qs,
    )
    pm_map = {}
    for p in Paymode.objects.filter(company=company, flag="Y").only("pcode", "pname", "iscash"):
        pm_map[p.pcode] = {"pname": p.pname or "", "iscash": p.iscash or ""}

    rows = []
    gqs = (
        qs.values("pcode")
        .annotate(cnt=Count("uuid"), amt=Sum("totmount"))
        .order_by("-amt")[:50]
    )
    total_amount = 0.0
    for r in gqs:
        pcode = r.get("pcode") or ""
        amt = float(r.get("amt") or 0)
        total_amount += amt
        meta = pm_map.get(pcode, {"pname": "", "iscash": ""})
        rows.append(
            {
                "pcode": pcode,
                "pname": meta.get("pname") or "",
                "iscash": meta.get("iscash") or "",
                "count": int(r.get("cnt") or 0),
                "amount": round(amt, 2),
            }
        )
    return {
        "range": {"from": df, "to": dt, "company": company, "storecode": storecode, "date_field": used_date_field},
        "summary": {
            "line_count": len(rows),
            "total_amount": round(total_amount, 2),
        },
        "rows": rows,
    }


def tool_cashier_item_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    top_n: int = 20,
    **_kwargs,
) -> Dict[str, Any]:
    """按交易明细 expense 统计项目（srvcode）销售额/数量。"""
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    n = max(1, min(int(top_n or 20), 100))
    trans_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=_kwargs.get("date_field", "vsdate"))
    qs = Expense.objects.filter(
        company=company,
        storecode=storecode,
        flag="Y",
        transuuid__in=trans_qs,
    )

    by_ttype = []
    tqs = (
        qs.values("ttype")
        .annotate(cnt=Count("uuid"), amount=Sum("s_mount"), qty=Sum("s_qty"))
        .order_by("-amount")[:20]
    )
    for r in tqs:
        by_ttype.append(
            {
                "ttype": r.get("ttype") or "",
                "count": int(r.get("cnt") or 0),
                "qty": float(r.get("qty") or 0),
                "amount": float(r.get("amount") or 0),
            }
        )

    top_items = []
    iqs = (
        qs.values("srvcode", "ttype")
        .annotate(cnt=Count("uuid"), amount=Sum("s_mount"), qty=Sum("s_qty"))
        .order_by("-amount")[:n]
    )
    for r in iqs:
        top_items.append(
            {
                "srvcode": r.get("srvcode") or "",
                "ttype": r.get("ttype") or "",
                "count": int(r.get("cnt") or 0),
                "qty": float(r.get("qty") or 0),
                "amount": float(r.get("amount") or 0),
            }
        )

    total = qs.aggregate(total_amount=Sum("s_mount"), total_qty=Sum("s_qty"), line_count=Count("uuid"))
    top_items = _enrich_expense_items(company, storecode, top_items)
    return {
        "range": {"from": df, "to": dt, "company": company, "storecode": storecode, "date_field": used_date_field},
        "summary": {
            "line_count": int(total.get("line_count") or 0),
            "total_qty": float(total.get("total_qty") or 0),
            "total_amount": float(total.get("total_amount") or 0),
        },
        "by_ttype": by_ttype,
        "top_items": top_items,
    }


def tool_store_dimension_sales_summary(
    company: str,
    storecode: str,
    dimension: str = "",
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    top_n: int = 50,
    include_blank: bool = True,
    max_lines: int = 150000,
    **_kwargs,
) -> Dict[str, Any]:
    """门店营业按管理属性维度汇总；实现见 report.store_dimension_sales。"""
    return compute_store_dimension_sales_summary(
        company,
        storecode,
        dimension,
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=_kwargs.get("date_field", "vsdate"),
        top_n=top_n,
        include_blank=include_blank,
        max_lines=max_lines,
    )


def tool_cashier_archievement_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    top_n: int = 20,
    include_details: bool = True,
    detail_limit: int = 500,
    ecode: str = "",
    **_kwargs,
) -> Dict[str, Any]:
    """
    业绩口径：按交易明细中的员工业绩字段汇总（pm/sec/thr）。
    - 汇总口径：公司+门店+有效交易（expvstoll.valiflag='Y'）
    - 明细口径：按员工分组，逐条列出员工在时间范围内的业绩明细，并给出员工小计
    """
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    n = max(1, min(int(top_n or 20), 100))
    dl = max(1, min(int(detail_limit or 500), 2000))
    trans_qs, used_date_field = _expvstoll_base_queryset(
        company,
        storecode,
        df,
        dt,
        date_field=_kwargs.get("date_field", "vsdate"),
    )
    qs = Expense.objects.filter(
        company=company,
        storecode=storecode,
        flag="Y",
        transuuid__in=trans_qs,
    )

    e = (ecode or "").strip()
    if e:
        qs = qs.filter(Q(pmcode=e) | Q(asscode1=e) | Q(asscode2=e))

    agg = qs.aggregate(
        line_count=Count("uuid"),
        sale_amount=Sum("s_mount"),
        pm_amount=Sum("pmamount"),
        sec_amount=Sum("secamount"),
        thr_amount=Sum("thramount"),
    )

    pm_rows = []
    for r in (
        qs.values("pmcode")
        .annotate(cnt=Count("uuid"), sale_amt=Sum("s_mount"), arch_amt=Sum("pmamount"))
        .order_by("-arch_amt")[:n]
    ):
        pm_rows.append(
            {
                "ecode": r.get("pmcode") or "",
                "line_count": int(r.get("cnt") or 0),
                "sale_amount": _safe_float(r.get("sale_amt")),
                "arch_amount": _safe_float(r.get("arch_amt")),
            }
        )

    ass_rows = []
    for r in (
        qs.values("asscode1")
        .annotate(cnt=Count("uuid"), sale_amt=Sum("s_mount"), arch_amt=Sum("secamount"))
        .order_by("-arch_amt")[:n]
    ):
        ass_rows.append(
            {
                "ecode": r.get("asscode1") or "",
                "line_count": int(r.get("cnt") or 0),
                "sale_amount": _safe_float(r.get("sale_amt")),
                "arch_amount": _safe_float(r.get("arch_amt")),
            }
        )

    by_employee_details: List[Dict[str, Any]] = []
    if include_details:
        detail_qs = (
            qs.select_related("transuuid", "transuuid__vipuuid")
            .only(
                "uuid",
                "ttype",
                "srvcode",
                "s_qty",
                "s_mount",
                "pmcode",
                "pmamount",
                "asscode1",
                "secamount",
                "asscode2",
                "thramount",
                "cashratio",
                "cardratio",
                "sendratio",
                "transuuid__uuid",
                "transuuid__exptxserno",
                "transuuid__vsdate",
                "transuuid__cdate",
                "transuuid__vcode",
                "transuuid__vipuuid__vname",
            )
            .order_by("pmcode", "asscode1", "asscode2", "transuuid__vsdate", "transuuid__exptxserno")[:dl]
        )

        # 以“员工在该行承担的角色”为分组键，兼容顾问/美疗师/美疗师2三个口径。
        groups: Dict[str, Dict[str, Any]] = {}
        for row in detail_qs:
            trans = row.transuuid
            if not trans:
                continue
            roles = []
            if row.pmcode:
                roles.append((row.pmcode, "pm", _safe_float(row.pmamount)))
            if row.asscode1:
                roles.append((row.asscode1, "ass1", _safe_float(row.secamount)))
            if row.asscode2:
                roles.append((row.asscode2, "ass2", _safe_float(row.thramount)))
            if e:
                roles = [x for x in roles if x[0] == e]
            for ecode_i, role_i, arch_amt in roles:
                key = f"{ecode_i}::{role_i}"
                g = groups.setdefault(
                    key,
                    {
                        "ecode": ecode_i,
                        "role": role_i,
                        "items": [],
                        "summary": {
                            "line_count": 0,
                            "sale_amount": 0.0,
                            "arch_amount": 0.0,
                            "qty": 0.0,
                        },
                    },
                )
                sale_amt = _safe_float(row.s_mount)
                qty = _safe_float(row.s_qty)
                cash_ratio = _safe_float(getattr(row, "cashratio", None))
                card_ratio = _safe_float(getattr(row, "cardratio", None))
                send_ratio = _safe_float(getattr(row, "sendratio", None))
                g["items"].append(
                    {
                        "expense_uuid": str(row.uuid),
                        "trans_uuid": str(trans.uuid),
                        "exptxserno": trans.exptxserno or "",
                        "vsdate": trans.vsdate or "",
                        "cdate": trans.cdate or "",
                        "vcode": trans.vcode or "",
                        "vname": (trans.vipuuid.vname if getattr(trans, "vipuuid", None) else "") or "",
                        "ttype": row.ttype or "",
                        "srvcode": row.srvcode or "",
                        "qty": qty,
                        "sale_amount": sale_amt,
                        "cash_ratio": cash_ratio,
                        "card_ratio": card_ratio,
                        "send_ratio": send_ratio,
                        "cash_amount": round(sale_amt * cash_ratio, 2),
                        "card_amount": round(sale_amt * card_ratio, 2),
                        "send_amount": round(sale_amt * send_ratio, 2),
                        "arch_amount": arch_amt,
                    }
                )
                g["summary"]["line_count"] += 1
                g["summary"]["sale_amount"] = round(g["summary"]["sale_amount"] + sale_amt, 2)
                g["summary"]["arch_amount"] = round(g["summary"]["arch_amount"] + arch_amt, 2)
                g["summary"]["qty"] = round(g["summary"]["qty"] + qty, 2)

        by_employee_details = sorted(groups.values(), key=lambda x: (x["ecode"], x["role"]))

    return {
        "range": {
            "from": df,
            "to": dt,
            "company": company,
            "storecode": storecode,
            "date_field": used_date_field,
        },
        "summary": {
            "line_count": int(agg.get("line_count") or 0),
            "sale_amount": _safe_float(agg.get("sale_amount")),
            "pm_arch_amount": _safe_float(agg.get("pm_amount")),
            "sec_arch_amount": _safe_float(agg.get("sec_amount")),
            "thr_arch_amount": _safe_float(agg.get("thr_amount")),
        },
        "pm_top": pm_rows,
        "assistant_top": ass_rows,
        "details": {
            "enabled": bool(include_details),
            "detail_limit": dl,
            "grouped_by_employee": by_employee_details,
        },
    }


def tool_vip_maintenance_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    top_n: int = 20,
    **_kwargs,
) -> Dict[str, Any]:
    """会员维护口径：新增、活跃、沉睡、复购会员与TOP会员。"""
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    n = max(1, min(int(top_n or 20), 100))

    vip_qs = Vip.objects.filter(company=company, storecode=storecode, flag="Y")
    trans_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=_kwargs.get("date_field", "vsdate"))

    total_vip = vip_qs.count()
    new_vip = vip_qs.filter(create_time__date__gte=pydatetime.datetime.strptime(df, "%Y%m%d").date(), create_time__date__lte=pydatetime.datetime.strptime(dt, "%Y%m%d").date()).count()
    active_vip = trans_qs.filter(vipuuid__isnull=False).values("vipuuid").distinct().count()
    repeat_vip = trans_qs.filter(vipuuid__isnull=False).values("vipuuid").annotate(c=Count("uuid")).filter(c__gte=2).count()
    sleeping_vip = max(total_vip - active_vip, 0)

    top_vips = []
    for r in (
        trans_qs.filter(vipuuid__isnull=False)
        .values("vipuuid", "vcode", "vipuuid__vname")
        .annotate(trans_count=Count("uuid"), amount=Sum("totmount"))
        .order_by("-amount")[:n]
    ):
        top_vips.append(
            {
                "vipuuid": str(r.get("vipuuid") or ""),
                "vcode": r.get("vcode") or "",
                "vname": r.get("vipuuid__vname") or "",
                "trans_count": int(r.get("trans_count") or 0),
                "amount": _safe_float(r.get("amount")),
            }
        )

    return {
        "range": {"from": df, "to": dt, "company": company, "storecode": storecode, "date_field": used_date_field},
        "summary": {
            "total_vip": int(total_vip),
            "new_vip": int(new_vip),
            "active_vip": int(active_vip),
            "repeat_vip": int(repeat_vip),
            "sleeping_vip": int(sleeping_vip),
        },
        "top_vips": top_vips,
    }


def tool_time_dimension_summary(
    company: str,
    storecode: str,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    granularity: str = "day",
    date_field: str = "vsdate",
    **_kwargs,
) -> Dict[str, Any]:
    """时间维度趋势：按日/周/月统计交易笔数、金额、活跃会员数。"""
    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    g = (granularity or "day").strip().lower()
    if g not in {"day", "week", "month"}:
        g = "day"

    trans_qs, used_date_field = _expvstoll_base_queryset(company, storecode, df, dt, date_field=date_field)
    qs = trans_qs.values("vsdate", "cdate", "totmount", "vipuuid")

    buckets: Dict[str, Dict[str, Any]] = {}
    for row in qs:
        base_date = row.get("cdate") if used_date_field == "cdate" else row.get("vsdate")
        key = _group_key_by_granularity(base_date or "", g)
        if not key:
            continue
        b = buckets.setdefault(key, {"period": key, "trans_count": 0, "amount": 0.0, "vip_set": set()})
        b["trans_count"] += 1
        b["amount"] += _safe_float(row.get("totmount"))
        if row.get("vipuuid"):
            b["vip_set"].add(str(row.get("vipuuid")))

    series = []
    for key in sorted(buckets.keys()):
        b = buckets[key]
        cnt = int(b["trans_count"])
        amt = round(float(b["amount"]), 2)
        uv = len(b["vip_set"])
        series.append(
            {
                "period": key,
                "trans_count": cnt,
                "amount": amt,
                "active_vip": uv,
                "avg_ticket": round(amt / cnt, 2) if cnt else 0,
            }
        )

    return {
        "range": {"from": df, "to": dt, "company": company, "storecode": storecode, "date_field": used_date_field},
        "granularity": g,
        "summary": {
            "period_count": len(series),
            "total_trans_count": sum(x["trans_count"] for x in series),
            "total_amount": round(sum(x["amount"] for x in series), 2),
        },
        "series": series,
    }


def tool_list_table_catalog(company: str, storecode: str, **_kwargs) -> List[Dict[str, Any]]:
    skip = frozenset(
        {"admin", "auth", "contenttypes", "sessions", "sites"},
    )
    out: List[Dict[str, Any]] = []
    for model in apps.get_models():
        if model._meta.app_label in skip:
            continue
        out.append(
            {
                "app": model._meta.app_label,
                "model": model.__name__,
                "db_table": model._meta.db_table,
                "verbose": str(model._meta.verbose_name or ""),
            }
        )
    out.sort(key=lambda x: x["db_table"])
    return out[:MAX_CATALOG]


def tool_describe_table(
    company: str, storecode: str, db_table: str = "", **_kwargs
) -> Dict[str, Any]:
    t = (db_table or "").strip().lower()
    if "." in t:
        t = t.rsplit(".", 1)[-1]
    if not t:
        return {"error": "缺少 db_table"}
    skip = frozenset(
        {"admin", "auth", "contenttypes", "sessions", "sites"},
    )
    for model in apps.get_models():
        if model._meta.app_label in skip:
            continue
        if model._meta.db_table.lower() != t:
            continue
        fields: List[Dict[str, Any]] = []
        for f in model._meta.fields:
            try:
                fields.append(
                    {
                        "name": f.name,
                        "column": f.column,
                        "internal_type": f.get_internal_type(),
                    }
                )
            except Exception:
                continue
            if len(fields) >= 120:
                break
        pk_col = ""
        if model._meta.pk is not None:
            pk_col = getattr(model._meta.pk, "column", None) or model._meta.pk.name
        return {
            "db_table": model._meta.db_table,
            "model": model.__name__,
            "app": model._meta.app_label,
            "primary_key_column": pk_col,
            "sql_hints": _describe_table_sql_hints(t, model),
            "fields": fields,
        }
    return {"error": "未找到表", "db_table": db_table}


def tool_readonly_sql(
    company: str,
    storecode: str,
    sql: str = "",
    max_rows: int | None = None,
    **_kwargs,
) -> Dict[str, Any]:
    """
    执行单条只读 SQL。表必须在业务模型白名单内；自动加/收紧 LIMIT。
    建议在 SQL 中自行加上 company / storecode 条件以缩小范围。
    """
    raw = (sql or "").strip()
    if not raw:
        return {"error": "sql 不能为空", "rows": [], "meta": {}}
    cap = None
    if max_rows is not None:
        try:
            cap = max(1, min(int(max_rows), 500))
        except (TypeError, ValueError):
            cap = None
    rows, meta = run_readonly_select(raw, max_rows=cap)
    return {"rows": rows, "meta": meta}


TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {
    "list_unsettled_guests": tool_list_unsettled_guests,
    "search_vips": tool_search_vips,
    "list_vip_cards": tool_list_vip_cards,
    "search_cards": tool_search_cards,
    "list_store_vips": tool_list_store_vips,
    "list_employees": tool_list_employees,
    "list_recent_expvstoll": tool_list_recent_expvstoll,
    "cashier_trade_summary": tool_cashier_trade_summary,
    "cashier_paymode_summary": tool_cashier_paymode_summary,
    "cashier_item_summary": tool_cashier_item_summary,
    "store_dimension_sales_summary": tool_store_dimension_sales_summary,
    "cashier_archievement_summary": tool_cashier_archievement_summary,
    "vip_maintenance_summary": tool_vip_maintenance_summary,
    "time_dimension_summary": tool_time_dimension_summary,
    "list_table_catalog": tool_list_table_catalog,
    "describe_table": tool_describe_table,
    "readonly_sql": tool_readonly_sql,
}

TOOL_CATALOG_TEXT = """
可用工具（name 必须与下列完全一致）：
- list_unsettled_guests：当前门店开单未结账列表（查 expvstoll_hung，valiflag_hung='Y'）。args: {}。返回 psstatus_hung 为服务流程状态，不是结账状态。
- search_vips：按姓名/手机/会员号模糊查会员。args: {"keyword":"..."}。
- list_vip_cards：某会员的卡列表。args: {"vipuuid":"uuid"}。
- search_cards：按卡号模糊或精确查卡。args: {"keyword":"..."} 或 {"exact_ccode":"..."}。
- list_store_vips：当前门店下会员列表（简要）。args: {}。
- list_employees：员工列表，可按门店筛。args: {} 或 {"storecode":"88"}（与页面门店一致时可省略由系统传入）。
- list_recent_expvstoll：最近成交主表 expvstoll 明细（仅 valiflag='Y' 有效交易）。args: {"days":90}，可选 {"date_field":"vsdate|cdate"}。
- cashier_trade_summary：交易主表聚合（金额/笔数/均单，含 ttype、员工分布；仅 valiflag='Y'）。args: {"days":90}，可选 {"date_field":"vsdate|cdate"}。
- cashier_paymode_summary：付款方式统计（toll + paymode，仅关联有效交易 valiflag='Y'）。args: 同上。
- cashier_item_summary：交易明细项目统计（expense，含 top srvcode；汇总额为 Sum(s_mount)）。映射规则：ttype=S→serviece；G→goods；C/I→cardinfo→cardtype。若需按现金/卡/赠送拆分金额，见系统字典 expense.cashratio/cardratio/sendratio（行级：s_mount*ratio）。args: 同上，可加 {"top_n":20}、{"date_field":"vsdate|cdate"}。
- store_dimension_sales_summary：门店营业按「管理属性」维度汇总（仅 valiflag='Y' 有效交易对应的 expense 行）。dimension 必填，白名单与 ItemModel 一致：displayclass1/2、marketclass1–4、financeclass1/2、archivementclass1/2、bodyparts1、tags、brand、discountclass，以及 ttype（项目大类）。每行按 ttype 解析主数据后取该字段分组，输出金额/数量/笔数及 cash/card/send 拆分（s_mount*各 ratio）。args: {"dimension":"displayclass1"}，可加 {"days":90}、{"date_field":"vsdate|cdate"}、{"top_n":50}、{"include_blank":true}、{"max_lines":150000}。
- cashier_archievement_summary：业绩口径统计（expense 的 pmamount/secamount/thramount，含顾问/美疗师TOP；仅有效交易）。支持按员工分组逐条明细 + 分组汇总；明细中 cash_ratio 等为模型 cashratio/cardratio/sendratio 的导出名，cash_amount=s_mount*cashratio 等同理。args: 同上，可加 {"top_n":20}、{"date_field":"vsdate|cdate"}、{"ecode":"员工编号"}、{"include_details":true}。
- vip_maintenance_summary：会员维护统计（会员总量/新增/活跃/复购/沉睡，含TOP会员；交易口径仅有效交易）。args: 同上，可加 {"top_n":20}、{"date_field":"vsdate|cdate"}。
- time_dimension_summary：时间维度趋势（日/周/月），支持按 vsdate（发生日）或 cdate（记账日）统计。args: 同上，可加 {"granularity":"day|week|month"}、{"date_field":"vsdate|cdate"}。
- list_table_catalog：列出业务库表名（模型映射）；写 SQL 时用返回的 db_table 物理表名，不要用 app 前缀。args: {}。
- describe_table：某张表的字段概览。args: {"db_table":"vip"}（小写物理表名，可带 app 前缀如 cashier.expvstoll 会自动取 expvstoll）。
- readonly_sql：执行单条只读 SELECT/WITH 查询，直接连 MySQL；仅能访问业务模型对应表；禁止写操作。
  args: {"sql":"SELECT ...", "max_rows":100 可选}。表名用物理名（expvstoll、vip、toll），禁止 cashier.expvstoll 等形式；务必在条件中包含 company（及必要的 storecode）。
""".strip()


def run_tool_plan(
    company: str,
    storecode: str,
    tools_payload: List[Dict[str, Any]],
    registry: Dict[str, Callable[..., Any]] | None = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    reg = registry or TOOL_REGISTRY
    results: List[Dict[str, Any]] = []
    errors: List[str] = []
    for spec in tools_payload or []:
        name = (spec.get("name") or "").strip()
        args = spec.get("args") if isinstance(spec.get("args"), dict) else {}
        fn = reg.get(name)
        if not fn:
            msg = f"未知工具: {name}"
            errors.append(msg)
            results.append({"tool": name, "ok": False, "data": None, "error": msg})
            continue
        try:
            data = fn(company=company, storecode=storecode, **args)
            results.append({"tool": name, "ok": True, "data": data, "error": None})
        except Exception as e:
            msg = f"{name}: {e}"
            errors.append(msg)
            results.append({"tool": name, "ok": False, "data": None, "error": str(e)})
    return results, errors


def planner_system_prompt() -> str:
    return f"""你是 Genesis 美业后台的「查询规划」模块。用户用中文描述需求。
（同一条 system 消息后半段会自动附带「系统编码字典」：ttype、挂单状态、paymode 等，规划时请严格对照。）

【重要】你处于「规划阶段」，不是回答阶段。禁止输出自然语言结论、禁止 markdown 表格、禁止列举查询结果。
你必须只输出一个 JSON 对象，不要 markdown，不要代码块，不要其它文字。
JSON 格式：
{{"tools":[{{"name":"工具名","args":{{...}}}}],"brief":"一句话说明将要查什么"}}

{TOOL_CATALOG_TEXT}

规则：
- 若用户只是闲聊、与业务数据无关，tools 设为 []。
- 需要多种数据时可以并列多个工具，按依赖顺序排列。
- 所有统计默认必须严格以当前 company + storecode 口径查询，不跨门店混算。
- 交易日期口径：vsdate=发生交易日期；cdate=记账日期。未指定时默认按 vsdate。
- 需要灵活统计、联表、复杂条件时：先用 list_table_catalog / describe_table 确认表与字段，再用 readonly_sql 写一条 SELECT；SQL 中应包含 company='…'（及必要的 storecode='…'），值从用户或上下文中推断，不要编造。
- 未结账/挂单：查 expvstoll_hung、expense_hung；已结账/营业/付款：查 expvstoll、expense、toll。两套表不要混用。
- psstatus/psstatus_hung 表示服务配料等流程节点，不能单独用来判断已结账；结账以数据是否在 expvstoll/toll 为准。
- readonly_sql 的 FROM/JOIN 必须使用物理表名（db_table），例如 expvstoll、expense、toll、expvstoll_hung、vip；不要写 cashier.expvstoll 等 Django app 限定名。
- readonly_sql 列名以 describe_table 返回的 column 为准：vip 表主键是 uuid（无 vipuuid 列）；expvstoll/cardinfo 等表的 vipuuid 才是外键列；expense/toll 用 transuuid 关联 expvstoll.uuid。
- expense 行上 s_mount（列 S_MOUNT）与 cashratio/cardratio/sendratio 仅在 expense 表；expvstoll 只有 totmount。按会员现金消费须 JOIN expense→expvstoll→vip，不可写 e.s_mount。
- 用户问「按显示分类/营销分类/财务分类/业绩分类/品牌/标签/卡类管理属性统计门店营业额、营业构成」等：用 store_dimension_sales_summary，每次传一个 dimension；需要多维度时并列多个该工具调用。
- 不要用 uuid 瞎猜；需要会员时先用 search_vips。
- readonly_sql 只能 SELECT，单条语句，不要分号拼接；不要注释。
"""


def answer_system_prompt() -> str:
    return """你是 Genesis 美业系统的业务助手。根据「用户问题」和「系统查询结果」用中文回答：
（同一条 system 消息后半段会自动附带「系统编码字典」，解释 ttype、psstatus_hung、paymode.iscash 等编码时必须按字典含义说明。）
- 简洁、有条理；金额、次数、日期如实引用查询结果。
- 若结果为空，说明未查到并给出可行建议。
- 不要编造数据库中没有的字段或记录。
- 若使用了 readonly_sql，说明这是数据库直接查询结果，勿臆测未返回的列。
- 解释 psstatus_hung 时说明其为服务/配料流程状态，勿与结账混为一谈。
- 若 SQL 报错 Unknown column，检查是否混淆了 uuid 与 vipuuid、transuuid 与 expvstolluuid；先 describe_table 再重写 SQL。"""


def safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
