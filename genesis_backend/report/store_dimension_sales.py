# coding=utf-8
"""
门店营业按管理属性维度汇总（与 cashier.expense + 有效 expvstoll 口径一致）。

供 `report` HTTP 接口与 `assistant.data_tools` 共用，避免重复实现。
"""
from __future__ import annotations

import datetime as pydatetime
from collections import defaultdict
from typing import Any, Dict, List

from django.db.models import Count, Sum

from adviser.models import Cardinfo
from baseinfo.models import (
    Appoption,
    Cardtype,
    Goods,
    ITEM_APPOPTION_FIELD_NAMES,
    ItemModel,
    Serviece,
)
from cashier.models import Expense, Expvstoll

STORE_DIM_ANALYSIS_ALLOWED = frozenset(ITEM_APPOPTION_FIELD_NAMES) | {"ttype"}


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


def _appoption_dim_label(company: str, model_key: str, base_seg: str, code: str) -> str:
    c = (code or "").strip()
    if not c:
        return ""
    spec = ItemModel.specialized_appoption_seg(model_key, base_seg)
    for seg in (spec, base_seg) if spec != base_seg else (spec,):
        lab = (
            Appoption.objects.filter(company=company, flag="Y", seg=seg, itemname=c)
            .values_list("itemvalues", flat=True)
            .first()
        )
        if lab:
            return (str(lab) or "").strip()
    if base_seg == "brand":
        lab = (
            Appoption.objects.filter(flag="Y", seg="brand", itemname=c)
            .values_list("itemvalues", flat=True)
            .first()
        )
        if lab:
            return (str(lab) or "").strip()
    return c


def _resolve_dim_label(company: str, dim_field: str, dim_value: str) -> str:
    c = (dim_value or "").strip()
    if not c:
        return "(空)"
    if dim_field == "ttype":
        return c
    for mk in ("serviece", "goods", "cardtype"):
        lab = _appoption_dim_label(company, mk, dim_field, c)
        if lab and lab != c:
            return lab
    return c


def compute_store_dimension_sales_summary(
    company: str,
    storecode: str,
    dimension: str = "",
    *,
    days: int = 90,
    date_from: str = "",
    date_to: str = "",
    date_field: str = "vsdate",
    top_n: int = 50,
    include_blank: bool = True,
    max_lines: int = 150000,
) -> Dict[str, Any]:
    """
    门店有效交易内，按 expense 行汇总到某一管理属性维度（ItemModel / Appoption 字段 + ttype）。

    行映射：S→serviece；G→goods；C/I→cardinfo→cardtype。
    """
    dim = (dimension or "").strip()
    if dim not in STORE_DIM_ANALYSIS_ALLOWED:
        return {
            "error": "dimension 无效或不在白名单",
            "dimension": dim,
            "allowed_dimensions": sorted(STORE_DIM_ANALYSIS_ALLOWED),
        }

    df, dt = _date_window(days=days, date_from=date_from, date_to=date_to)
    n = max(1, min(int(top_n or 50), 200))
    cap = max(1000, min(int(max_lines or 150000), 500000))
    trans_qs, used_date_field = _expvstoll_base_queryset(
        company, storecode, df, dt, date_field=date_field
    )
    exp_base = Expense.objects.filter(
        company=company,
        storecode=storecode,
        flag="Y",
        transuuid__in=trans_qs,
    )
    exp_iter = exp_base.only(
        "ttype", "srvcode", "s_mount", "s_qty", "cashratio", "cardratio", "sendratio"
    )

    dim_fields = list(ITEM_APPOPTION_FIELD_NAMES)
    codes_s = {
        str(x).strip()
        for x in exp_base.filter(ttype="S")
        .exclude(srvcode__isnull=True)
        .exclude(srvcode="")
        .values_list("srvcode", flat=True)
        .distinct()
        if str(x).strip()
    }
    codes_g = {
        str(x).strip()
        for x in exp_base.filter(ttype="G")
        .exclude(srvcode__isnull=True)
        .exclude(srvcode="")
        .values_list("srvcode", flat=True)
        .distinct()
        if str(x).strip()
    }
    codes_c = {
        str(x).strip()
        for x in exp_base.filter(ttype__in=("C", "I"))
        .exclude(srvcode__isnull=True)
        .exclude(srvcode="")
        .values_list("srvcode", flat=True)
        .distinct()
        if str(x).strip()
    }

    srv_map: Dict[str, Dict[str, Any]] = {}
    if codes_s:
        for row in Serviece.objects.filter(
            company=company, storecode=storecode, flag="Y", svrcdoe__in=list(codes_s)
        ).values("svrcdoe", *dim_fields):
            srv_map[str(row.get("svrcdoe") or "").strip()] = row

    goods_map: Dict[str, Dict[str, Any]] = {}
    if codes_g:
        for row in Goods.objects.filter(
            company=company, storecode=storecode, flag="Y", gcode__in=list(codes_g)
        ).values("gcode", *dim_fields):
            goods_map[str(row.get("gcode") or "").strip()] = row

    ccode_to_ct: Dict[str, str] = {}
    ct_types: set[str] = set()
    if codes_c:
        for row in Cardinfo.objects.filter(
            company=company, storecode=storecode, flag="Y", ccode__in=list(codes_c)
        ).values("ccode", "cardtype"):
            ct = str(row.get("cardtype") or "").strip()
            ccode_to_ct[str(row.get("ccode") or "").strip()] = ct
            if ct:
                ct_types.add(ct)

    ct_map: Dict[str, Dict[str, Any]] = {}
    if ct_types:
        for row in Cardtype.objects.filter(
            company=company, storecode=storecode, cardtype__in=list(ct_types)
        ).values("cardtype", *dim_fields):
            ct_map[str(row.get("cardtype") or "").strip()] = row

    agg: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "line_count": 0,
            "qty": 0.0,
            "total_amount": 0.0,
            "cash_amount": 0.0,
            "card_amount": 0.0,
            "send_amount": 0.0,
        }
    )

    def resolve_dim_raw(e) -> str:
        t = (e.ttype or "").strip().upper()
        code = str(e.srvcode or "").strip()
        if dim == "ttype":
            return t or ""

        master: Dict[str, Any] = {}
        if t == "S" and code:
            master = srv_map.get(code, {})
        elif t == "G" and code:
            master = goods_map.get(code, {})
        elif t in {"C", "I"} and code:
            ct = ccode_to_ct.get(code, "")
            master = ct_map.get(ct, {}) if ct else {}

        if dim in ITEM_APPOPTION_FIELD_NAMES:
            raw = master.get(dim) if master else None
            if raw is not None:
                return str(raw).strip()
        return ""

    scanned2 = 0
    truncated = False
    for e in exp_iter.iterator(chunk_size=2000):
        scanned2 += 1
        if scanned2 > cap:
            truncated = True
            break
        dk = resolve_dim_raw(e)
        if not dk and not include_blank:
            continue
        bucket = dk if dk else "(空)"
        a = agg[bucket]
        a["line_count"] += 1
        a["qty"] += _safe_float(e.s_qty)
        sm = _safe_float(e.s_mount)
        a["total_amount"] += sm
        a["cash_amount"] += sm * _safe_float(e.cashratio)
        a["card_amount"] += sm * _safe_float(e.cardratio)
        a["send_amount"] += sm * _safe_float(e.sendratio)

    rows_out: List[Dict[str, Any]] = []
    for bucket, a in agg.items():
        dim_value = "" if bucket == "(空)" else bucket
        dim_label = _resolve_dim_label(company, dim, dim_value) if dim_value else "(空)"
        rows_out.append(
            {
                "dim_value": dim_value,
                "dim_label": dim_label,
                "line_count": int(a["line_count"]),
                "qty": round(a["qty"], 4),
                "total_amount": round(a["total_amount"], 2),
                "cash_amount": round(a["cash_amount"], 2),
                "card_amount": round(a["card_amount"], 2),
                "send_amount": round(a["send_amount"], 2),
            }
        )

    rows_out.sort(key=lambda r: r["total_amount"], reverse=True)
    rows_out = rows_out[:n]

    gtot = exp_base.aggregate(
        line_count=Count("uuid"),
        total_amount=Sum("s_mount"),
        total_qty=Sum("s_qty"),
    )

    out: Dict[str, Any] = {
        "range": {
            "from": df,
            "to": dt,
            "company": company,
            "storecode": storecode,
            "date_field": used_date_field,
        },
        "dimension": dim,
        "aggregated_expense_lines": scanned2,
        "aggregation_truncated": truncated,
        "max_lines": cap,
        "summary": {
            "line_count": int(gtot.get("line_count") or 0),
            "total_qty": float(gtot.get("total_qty") or 0),
            "total_amount": float(gtot.get("total_amount") or 0),
        },
        "rows": rows_out,
    }
    if truncated:
        out["note"] = (
            "仅前 max_lines 条 expense 参与分组汇总，rows 小计之和可能小于全量 summary；"
            "需要全量维度分布时可缩小日期范围或提高 max_lines。"
        )
    return out
