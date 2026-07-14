# coding=utf-8
"""
客户生命周期分级：活跃 / 流失预警（趋势下降）/ 休眠。
公司级统一参数（Appoption seg=vip_lifecycle 或环境变量），休眠客自动回写 vip.status。
"""

from __future__ import annotations

import datetime as pydatetime
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction

from assistant.data_tools import MAX_ROWS, _lim, _safe_float
from assistant.vip_tools import (
    _churn_risk_level,
    _churn_trend_label,
    _days_between,
    _fetch_trans_stats_map,
    _parse_yyyymmdd_date,
    _period_consumption,
    _resolve_empl_names,
    _resolve_vip,
    _vip_visit_stats,
)
from baseinfo.models import Appoption, Vip

from cashier.models import Expvstoll
from django.db.models import Sum

SEGMENT_ACTIVE = "active"
SEGMENT_AT_RISK = "at_risk"
SEGMENT_SLEEPING = "sleeping"
SEGMENT_NEVER_VISITED = "never_visited"
VALUE_TIER_HIGH = "high_value"

DEFAULT_INACTIVE_DAYS = 90
DEFAULT_CRITICAL_DAYS = 180
DEFAULT_TREND_DAYS = 90
DEFAULT_HIGH_VALUE_PERCENT = 20
DEFAULT_HIGH_VALUE_DAYS = 365

DEFAULT_STATUS_ACTIVE = "10"
DEFAULT_STATUS_SLEEPING = "20"
DEFAULT_STATUS_LOST = "30"

_PLAYBOOK_PATH = Path(__file__).resolve().parent / "playbooks" / "vip_lifecycle.json"


@dataclass(frozen=True)
class LifecycleConfig:
    inactive_days: int = DEFAULT_INACTIVE_DAYS
    critical_days: int = DEFAULT_CRITICAL_DAYS
    trend_days: int = DEFAULT_TREND_DAYS
    status_active: str = DEFAULT_STATUS_ACTIVE
    status_sleeping: str = DEFAULT_STATUS_SLEEPING
    status_lost: str = DEFAULT_STATUS_LOST
    high_value_percent: int = DEFAULT_HIGH_VALUE_PERCENT
    high_value_days: int = DEFAULT_HIGH_VALUE_DAYS


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _appoption_int(company: str, seg: str, itemname: str) -> Optional[int]:
    row = (
        Appoption.objects.filter(
            flag="Y",
            company=company,
            seg=seg,
            itemname=itemname,
        )
        .values_list("itemvalues", flat=True)
        .first()
    )
    if not row:
        return None
    try:
        return int(str(row).strip())
    except ValueError:
        return None


def _resolve_status_code(company: str, keyword: str, default: str) -> str:
    """按 Appoption vipstatus 的 itemvalues 文案匹配（活跃/休眠/流失）。"""
    qs = Appoption.objects.filter(flag="Y", seg="vipstatus", company=company).values_list(
        "itemname", "itemvalues"
    )
    if not qs.exists():
        qs = Appoption.objects.filter(flag="Y", seg="vipstatus", company="common").values_list(
            "itemname", "itemvalues"
        )
    for itemname, itemvalues in qs:
        lab = (itemvalues or "").strip()
        if keyword in lab:
            return (itemname or "").strip() or default
    return default


def get_lifecycle_config(company: str) -> LifecycleConfig:
    """公司级统一参数（全部门店一致）。"""
    company = (company or "").strip()
    inactive = _appoption_int(company, "vip_lifecycle", "inactive_days")
    if inactive is None:
        inactive = _int_env("VIP_LIFECYCLE_INACTIVE_DAYS", DEFAULT_INACTIVE_DAYS)
    critical = _appoption_int(company, "vip_lifecycle", "critical_days")
    if critical is None:
        critical = _int_env("VIP_LIFECYCLE_CRITICAL_DAYS", DEFAULT_CRITICAL_DAYS)
    trend = _appoption_int(company, "vip_lifecycle", "trend_days")
    if trend is None:
        trend = _int_env("VIP_LIFECYCLE_TREND_DAYS", DEFAULT_TREND_DAYS)
    hv_pct = _appoption_int(company, "vip_lifecycle", "high_value_percent")
    if hv_pct is None:
        hv_pct = _int_env("VIP_LIFECYCLE_HIGH_VALUE_PERCENT", DEFAULT_HIGH_VALUE_PERCENT)
    hv_days = _appoption_int(company, "vip_lifecycle", "high_value_days")
    if hv_days is None:
        hv_days = _int_env("VIP_LIFECYCLE_HIGH_VALUE_DAYS", DEFAULT_HIGH_VALUE_DAYS)

    inactive = max(30, min(int(inactive), 3650))
    critical = max(inactive, min(int(critical), 3650))
    trend = max(30, min(int(trend), 365))
    hv_pct = max(5, min(int(hv_pct), 50))
    hv_days = max(90, min(int(hv_days), 730))

    return LifecycleConfig(
        inactive_days=inactive,
        critical_days=critical,
        trend_days=trend,
        high_value_percent=hv_pct,
        high_value_days=hv_days,
        status_active=_resolve_status_code(company, "活跃", DEFAULT_STATUS_ACTIVE),
        status_sleeping=_resolve_status_code(company, "休眠", DEFAULT_STATUS_SLEEPING),
        status_lost=_resolve_status_code(company, "流失", DEFAULT_STATUS_LOST),
    )


def _load_playbooks() -> Dict[str, Any]:
    try:
        with open(_PLAYBOOK_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def recommended_actions_for_segment(segment: str) -> List[Dict[str, Any]]:
    data = _load_playbooks()
    seg = (segment or "").strip().lower()
    block = data.get(seg) or data.get("default") or {}
    actions = block.get("actions") or []
    return [a for a in actions if isinstance(a, dict)]


def playbook_goals_for_segment(segment: str) -> List[str]:
    data = _load_playbooks()
    seg = (segment or "").strip().lower()
    block = data.get(seg) or data.get("default") or {}
    goals = block.get("goals") or []
    return [g for g in goals if isinstance(g, str) and g.strip()]


def _mask_telph(telph: str) -> str:
    t = (telph or "").strip()
    if len(t) >= 11:
        return t[:3] + "****" + t[-4:]
    return t


def _build_personalization_context(
    vip: Vip,
    row: Dict[str, Any],
    cfg: LifecycleConfig,
) -> Dict[str, Any]:
    days = row.get("days_since_last_visit")
    return {
        "vname": ((vip.vname or "").strip() or "会员"),
        "vcode": vip.vcode or "",
        "telph_mask": _mask_telph(vip.telph or ""),
        "days_since": days if days != "" else "—",
        "inactive_days": cfg.inactive_days,
        "trend_days": cfg.trend_days,
        "lifetime_amount": int(_safe_float(row.get("lifetime_amount"))),
        "recent_amount": int(_safe_float(row.get("recent_amount"))),
        "recent_year_amount": int(_safe_float(row.get("recent_year_amount"))),
        "high_value_days": cfg.high_value_days,
        "adviser_name": (row.get("adviser_name") or "您的专属顾问").strip() or "您的专属顾问",
        "segment": row.get("segment") or "",
    }


def _action_matches_when(action: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    when = action.get("when")
    if not when or not isinstance(when, dict):
        return True
    lifetime = _safe_float(ctx.get("lifetime_amount"))
    days_raw = ctx.get("days_since")
    days_i: Optional[int] = None
    if isinstance(days_raw, int):
        days_i = days_raw
    elif str(days_raw).isdigit():
        days_i = int(days_raw)
    if "lifetime_amount_gte" in when and lifetime < _safe_float(when["lifetime_amount_gte"]):
        return False
    if "lifetime_amount_lt" in when and lifetime >= _safe_float(when["lifetime_amount_lt"]):
        return False
    if "days_since_gte" in when:
        need = int(when["days_since_gte"])
        if days_i is None or days_i < need:
            return False
    return True


def _render_template(template: str, ctx: Dict[str, Any]) -> str:
    out = template
    for key, val in ctx.items():
        out = out.replace("{" + key + "}", str(val))
    return out


def personalize_recommended_actions(
    segment: str,
    vip: Vip,
    row: Dict[str, Any],
    cfg: LifecycleConfig,
) -> List[Dict[str, Any]]:
    """按 playbook 规则过滤并填充话术模板。"""
    base_actions = recommended_actions_for_segment(segment)
    ctx = _build_personalization_context(vip, row, cfg)
    personalized: List[Dict[str, Any]] = []
    priority = 1
    for action in base_actions:
        if not _action_matches_when(action, ctx):
            continue
        item = {k: v for k, v in action.items() if k != "when"}
        item["priority"] = priority
        priority += 1
        template = (action.get("template") or "").strip()
        if template:
            item["suggested_script"] = _render_template(template, ctx)
        personalized.append(item)
    if personalized:
        return personalized
    fallback = recommended_actions_for_segment("default")
    return [{**a, "priority": i + 1} for i, a in enumerate(fallback[:2])]


def _attach_playbook(row: Dict[str, Any], vip: Vip, cfg: LifecycleConfig) -> None:
    seg = (row.get("segment") or "").strip()
    playbook_seg = seg
    if row.get("value_tier") == VALUE_TIER_HIGH and seg == SEGMENT_ACTIVE:
        playbook_seg = VALUE_TIER_HIGH
    row["playbook_goals"] = playbook_goals_for_segment(playbook_seg)
    row["recommended_actions"] = personalize_recommended_actions(playbook_seg, vip, row, cfg)


def _fetch_recent_amount_map(company: str, storecode: str, days: int) -> Dict[str, float]:
    cutoff = (pydatetime.date.today() - pydatetime.timedelta(days=days)).strftime("%Y%m%d")
    rows = (
        Expvstoll.objects.filter(
            company=company,
            storecode=storecode,
            flag="Y",
            valiflag="Y",
            vipuuid__isnull=False,
            vsdate__gte=cutoff,
        )
        .values("vipuuid")
        .annotate(recent_amount=Sum("totmount"))
    )
    return {str(r["vipuuid"]): _safe_float(r.get("recent_amount")) for r in rows}


def _apply_high_value_tiers(
    rows: List[Dict[str, Any]],
    recent_map: Dict[str, float],
    cfg: LifecycleConfig,
) -> None:
    """活跃客中近 N 天消费 Top X% 标记 value_tier=high_value。"""
    active_pairs: List[Tuple[str, float]] = []
    for row in rows:
        if row.get("segment") != SEGMENT_ACTIVE:
            row.setdefault("value_tier", "")
            continue
        vu = (row.get("vipuuid") or "").strip()
        amt = recent_map.get(vu, 0.0)
        row["recent_year_amount"] = amt
        row.setdefault("value_tier", "")
        if amt > 0:
            active_pairs.append((vu, amt))
    if not active_pairs:
        return
    active_pairs.sort(key=lambda x: x[1], reverse=True)
    top_n = max(1, int(len(active_pairs) * cfg.high_value_percent / 100))
    threshold = active_pairs[min(top_n, len(active_pairs)) - 1][1]
    high_set = {vu for vu, amt in active_pairs if amt >= threshold}
    for row in rows:
        vu = (row.get("vipuuid") or "").strip()
        if row.get("segment") == SEGMENT_ACTIVE and vu in high_set:
            row["value_tier"] = VALUE_TIER_HIGH


def compute_vip_segment(
    *,
    company: str,
    storecode: str,
    vip: Vip,
    trans_stats: Optional[Dict[str, Any]],
    cfg: LifecycleConfig,
    trend_stats: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """单客分级（确定性规则）。"""
    today = pydatetime.date.today()
    vu = str(vip.uuid)
    stats = trans_stats or {}
    last_vsdate = (stats.get("last_vsdate") or "").strip()
    trans_count = int(stats.get("trans_count") or 0)
    lifetime_amount = _safe_float(stats.get("lifetime_amount"))

    never_visited = trans_count == 0 or not last_vsdate
    days_since: Optional[int] = None
    sleeping_grade = ""
    segment = SEGMENT_ACTIVE

    if never_visited:
        base_date = vip.indate or (vip.create_time.date() if vip.create_time else None)
        if base_date:
            days_since = _days_between(base_date, today)
        if days_since is None or days_since >= cfg.inactive_days:
            segment = SEGMENT_SLEEPING
            sleeping_grade = "never_visited"
        else:
            segment = SEGMENT_NEVER_VISITED
    else:
        last_d = _parse_yyyymmdd_date(last_vsdate)
        if last_d:
            days_since = _days_between(last_d, today)
        cutoff = (today - pydatetime.timedelta(days=cfg.inactive_days)).strftime("%Y%m%d")
        if last_vsdate < cutoff:
            segment = SEGMENT_SLEEPING
            sleeping_grade = (
                "critical" if (days_since or 0) >= cfg.critical_days else "warning"
            )
        else:
            segment = SEGMENT_ACTIVE

    amount_trend = "stable"
    visit_trend = "stable"
    recent_amount = 0.0
    prior_amount = 0.0

    if trend_stats:
        amount_trend = trend_stats.get("amount_trend") or "stable"
        visit_trend = trend_stats.get("visit_trend") or "stable"
        recent_amount = _safe_float(trend_stats.get("recent_amount"))
        prior_amount = _safe_float(trend_stats.get("prior_amount"))
    elif not never_visited and segment == SEGMENT_ACTIVE:
        recent = _period_consumption(
            company, storecode, vu, days=cfg.trend_days, offset_days=0
        )
        prior = _period_consumption(
            company, storecode, vu, days=cfg.trend_days, offset_days=cfg.trend_days
        )
        recent_amount = recent["total_amount"]
        prior_amount = prior["total_amount"]
        amount_trend = _churn_trend_label(recent_amount, prior_amount)
        visit_trend = _churn_trend_label(
            float(recent["visit_days"]), float(prior["visit_days"])
        )

    if segment == SEGMENT_ACTIVE and (
        amount_trend == "declining" or visit_trend == "declining"
    ):
        segment = SEGMENT_AT_RISK

    risk_level = _churn_risk_level(
        days_since=days_since if isinstance(days_since, int) else None,
        never_visited=never_visited,
        inactive_days=cfg.inactive_days,
        critical_days=cfg.critical_days,
        amount_trend=amount_trend,
        visit_trend=visit_trend,
    )

    risk_factors: List[str] = []
    if segment == SEGMENT_AT_RISK:
        if amount_trend == "declining":
            risk_factors.append(f"近 {cfg.trend_days} 天消费较前一周期下降")
        if visit_trend == "declining":
            risk_factors.append(f"近 {cfg.trend_days} 天到店频次较前一周期下降")
    if segment == SEGMENT_SLEEPING:
        if sleeping_grade == "never_visited" or never_visited:
            risk_factors.append("从未有效消费且已超过休眠阈值")
        elif isinstance(days_since, int):
            risk_factors.append(f"已 {days_since} 天无有效消费（阈值 {cfg.inactive_days} 天）")

    actions = recommended_actions_for_segment(segment)

    return {
        "vipuuid": vu,
        "vcode": vip.vcode or "",
        "vname": vip.vname or "",
        "mtcode": vip.mtcode or "",
        "telph": vip.telph or "",
        "viptype": vip.viptype or "",
        "status": vip.status or "",
        "viplevel": vip.viplevel or "",
        "segment": segment,
        "sleeping_grade": sleeping_grade,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "days_since_last_visit": days_since if days_since is not None else "",
        "last_vsdate": last_vsdate,
        "lifetime_trans_count": trans_count,
        "lifetime_amount": lifetime_amount,
        "amount_trend": amount_trend,
        "visit_trend": visit_trend,
        "recent_amount": recent_amount,
        "prior_amount": prior_amount,
        "recommended_actions": actions,
        "playbook_goals": playbook_goals_for_segment(segment),
        "target_status": _target_status_for_segment(segment, sleeping_grade, cfg),
        "target_status_kind": (
            "lost"
            if segment == SEGMENT_SLEEPING and sleeping_grade == "critical"
            else "sleeping"
            if segment == SEGMENT_SLEEPING
            else "active"
        ),
    }


def _target_status_for_segment(
    segment: str,
    sleeping_grade: str,
    cfg: LifecycleConfig,
) -> str:
    if segment == SEGMENT_SLEEPING:
        if sleeping_grade == "critical" and cfg.status_lost:
            return cfg.status_lost
        return cfg.status_sleeping
    return cfg.status_active


def resolve_vipstatus_labels(company: str) -> Dict[str, str]:
    """vip.status 编码 → 文案（Appoption vipstatus）。"""
    company = (company or "").strip()
    out: Dict[str, str] = {}
    for itemname, itemvalues in Appoption.objects.filter(
        flag="Y", seg="vipstatus", company=company
    ).values_list("itemname", "itemvalues"):
        code = (itemname or "").strip()
        if code:
            out[code] = (itemvalues or "").strip() or code
    if not out:
        for itemname, itemvalues in Appoption.objects.filter(
            flag="Y", seg="vipstatus", company="common"
        ).values_list("itemname", "itemvalues"):
            code = (itemname or "").strip()
            if code:
                out[code] = (itemvalues or "").strip() or code
    return out


def _vip_row_base(v: Vip, empl_map: Dict[str, str]) -> Dict[str, str]:
    return {
        "ecode": v.ecode or "",
        "adviser_name": empl_map.get((v.ecode or "").strip(), ""),
        "ecode2": v.ecode2 or "",
        "therapist_name": empl_map.get((v.ecode2 or "").strip(), ""),
    }


def compute_lifecycle_batch(
    company: str,
    storecode: str,
    *,
    segment: str = "",
    viptype: str = "",
    ecode: str = "",
    limit: int = MAX_ROWS,
    include_trend: bool = True,
) -> Dict[str, Any]:
    company = (company or "").strip()
    storecode = (storecode or "").strip()
    cfg = get_lifecycle_config(company)
    lim = _lim(limit)
    seg_filter = (segment or "").strip().lower()

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

    counts: Dict[str, int] = {
        SEGMENT_ACTIVE: 0,
        SEGMENT_AT_RISK: 0,
        SEGMENT_SLEEPING: 0,
        SEGMENT_NEVER_VISITED: 0,
        VALUE_TIER_HIGH: 0,
    }
    rows: List[Dict[str, Any]] = []
    pending: List[Tuple[Vip, Dict[str, Any]]] = []
    total_checked = 0

    for v in vip_qs.iterator(chunk_size=500):
        total_checked += 1
        vu = str(v.uuid)
        trend_stats = None
        if include_trend and vu in trans_map:
            recent = _period_consumption(
                company, storecode, vu, days=cfg.trend_days, offset_days=0
            )
            prior = _period_consumption(
                company, storecode, vu, days=cfg.trend_days, offset_days=cfg.trend_days
            )
            trend_stats = {
                "amount_trend": _churn_trend_label(recent["total_amount"], prior["total_amount"]),
                "visit_trend": _churn_trend_label(
                    float(recent["visit_days"]), float(prior["visit_days"])
                ),
                "recent_amount": recent["total_amount"],
                "prior_amount": prior["total_amount"],
            }

        row = compute_vip_segment(
            company=company,
            storecode=storecode,
            vip=v,
            trans_stats=trans_map.get(vu),
            cfg=cfg,
            trend_stats=trend_stats,
        )
        row.update(_vip_row_base(v, empl_map))
        sk = row["segment"]
        counts[sk] = counts.get(sk, 0) + 1
        pending.append((v, row))

    recent_map = _fetch_recent_amount_map(company, storecode, cfg.high_value_days)
    _apply_high_value_tiers([r for _v, r in pending], recent_map, cfg)
    for v, row in pending:
        if row.get("value_tier") == VALUE_TIER_HIGH:
            counts[VALUE_TIER_HIGH] = counts.get(VALUE_TIER_HIGH, 0) + 1
        _attach_playbook(row, v, cfg)
        sk = row["segment"]
        if seg_filter == VALUE_TIER_HIGH:
            if row.get("value_tier") != VALUE_TIER_HIGH:
                continue
        elif seg_filter and sk != seg_filter:
            continue
        rows.append(row)

    rows.sort(
        key=lambda r: (
            0 if r.get("segment") == SEGMENT_AT_RISK else 1,
            0 if r.get("segment") == SEGMENT_SLEEPING else 1,
            -(int(r["days_since_last_visit"]) if str(r.get("days_since_last_visit") or "").isdigit() else 0),
        )
    )
    truncated = len(rows) > lim
    rows = rows[:lim]

    return {
        "criteria": {
            "company": company,
            "storecode": storecode,
            "inactive_days": cfg.inactive_days,
            "critical_days": cfg.critical_days,
            "trend_days": cfg.trend_days,
            "high_value_percent": cfg.high_value_percent,
            "high_value_days": cfg.high_value_days,
            "segment_filter": seg_filter,
            "viptype": vt,
            "ecode": adv,
            "at_risk_rule": "消费或到店频次较前一周期下降（趋势 declining）",
            "sleeping_rule": f">= {cfg.inactive_days} 天无 valiflag=Y 有效消费",
        },
        "summary": {
            "total_vip_checked": total_checked,
            "segment_counts": counts,
            "returned_count": len(rows),
            "truncated": truncated,
        },
        "vips": rows,
    }


def sync_sleeping_vip_status(
    company: str,
    storecode: str = "",
    *,
    dry_run: bool = False,
    batch_size: int = 500,
) -> Dict[str, Any]:
    """
    休眠客写 vip.status=休眠码；恢复活跃客写回活跃码。
    storecode 为空则处理该公司全部门店。
    """
    company = (company or "").strip()
    cfg = get_lifecycle_config(company)
    qs = Vip.objects.filter(company=company, flag="Y")
    sc = (storecode or "").strip()
    if sc:
        qs = qs.filter(storecode=sc)

    updated_sleeping = 0
    updated_lost = 0
    updated_active = 0
    skipped = 0
    errors: List[str] = []

    storecodes = list(qs.values_list("storecode", flat=True).distinct())
    if sc:
        storecodes = [sc]

    for store in storecodes:
        trans_map = _fetch_trans_stats_map(company, store)
        store_qs = qs.filter(storecode=store)
        to_update: List[Vip] = []

        for v in store_qs.iterator(chunk_size=batch_size):
            vu = str(v.uuid)
            row = compute_vip_segment(
                company=company,
                storecode=store,
                vip=v,
                trans_stats=trans_map.get(vu),
                cfg=cfg,
                trend_stats=None,
            )
            target = (row.get("target_status") or "").strip()
            current = (v.status or "").strip()
            kind = row.get("target_status_kind") or ""
            if row["segment"] == SEGMENT_SLEEPING:
                if target and current != target:
                    if not dry_run:
                        v.status = target
                        to_update.append(v)
                    if kind == "lost":
                        updated_lost += 1
                    else:
                        updated_sleeping += 1
                else:
                    skipped += 1
            elif row["segment"] in (SEGMENT_ACTIVE, SEGMENT_AT_RISK, SEGMENT_NEVER_VISITED):
                inactive_codes = {c for c in (cfg.status_sleeping, cfg.status_lost) if c}
                if current in inactive_codes and cfg.status_active:
                    if not dry_run:
                        v.status = cfg.status_active
                        to_update.append(v)
                    updated_active += 1
                else:
                    skipped += 1

        if to_update and not dry_run:
            try:
                with transaction.atomic():
                    Vip.objects.bulk_update(to_update, ["status"], batch_size=200)
            except Exception as exc:
                errors.append(f"{store}: {exc}")

    return {
        "company": company,
        "storecode": sc or "*",
        "dry_run": dry_run,
        "status_sleeping_code": cfg.status_sleeping,
        "status_lost_code": cfg.status_lost,
        "status_active_code": cfg.status_active,
        "updated_sleeping": updated_sleeping,
        "updated_lost": updated_lost,
        "updated_active": updated_active,
        "skipped": skipped,
        "errors": errors,
    }


def tool_vip_lifecycle_batch(
    company: str,
    storecode: str,
    segment: str = "",
    viptype: str = "",
    ecode: str = "",
    limit: int = MAX_ROWS,
    **_kwargs,
) -> Dict[str, Any]:
    """门店客户生命周期分级（活跃/预警/休眠）+ 运营建议。参数由公司级 vip_lifecycle 配置统一决定。"""
    return compute_lifecycle_batch(
        company,
        storecode,
        segment=segment,
        viptype=viptype,
        ecode=ecode,
        limit=limit,
    )


def tool_vip_lifecycle_one(
    company: str,
    storecode: str,
    telph: str = "",
    vipuuid: str = "",
    vcode: str = "",
    **_kwargs,
) -> Dict[str, Any]:
    """单客生命周期分级 + 建议方案。"""
    v = _resolve_vip(company, storecode, telph=telph, vipuuid=vipuuid, vcode=vcode)
    if not v:
        return {"error": "未找到会员", "telph": telph, "vipuuid": vipuuid, "vcode": vcode}
    cfg = get_lifecycle_config(company)
    trans_map = _fetch_trans_stats_map(company, storecode)
    vu = str(v.uuid)
    recent = _period_consumption(company, storecode, vu, days=cfg.trend_days, offset_days=0)
    prior = _period_consumption(
        company, storecode, vu, days=cfg.trend_days, offset_days=cfg.trend_days
    )
    trend_stats = {
        "amount_trend": _churn_trend_label(recent["total_amount"], prior["total_amount"]),
        "visit_trend": _churn_trend_label(float(recent["visit_days"]), float(prior["visit_days"])),
        "recent_amount": recent["total_amount"],
        "prior_amount": prior["total_amount"],
    }
    empl_map = _resolve_empl_names(company, [v.ecode or "", v.ecode2 or ""])
    row = compute_vip_segment(
        company=company,
        storecode=storecode,
        vip=v,
        trans_stats=trans_map.get(vu),
        cfg=cfg,
        trend_stats=trend_stats,
    )
    row.update(_vip_row_base(v, empl_map))
    recent_map = _fetch_recent_amount_map(company, storecode, cfg.high_value_days)
    _apply_high_value_tiers([row], recent_map, cfg)
    _attach_playbook(row, v, cfg)
    row["config"] = {
        "inactive_days": cfg.inactive_days,
        "critical_days": cfg.critical_days,
        "trend_days": cfg.trend_days,
    }
    labels = resolve_vipstatus_labels(company)
    row["status_label"] = labels.get((v.status or "").strip(), v.status or "")
    row["target_status_label"] = labels.get(
        (row.get("target_status") or "").strip(), row.get("target_status") or ""
    )
    return row


def _latest_snapshot_date(
    company: str,
    storecode: str,
    *,
    on_or_before: Optional[pydatetime.date] = None,
) -> Optional[pydatetime.date]:
    from assistant.models import VipLifecycleSnapshotSummary

    qs = VipLifecycleSnapshotSummary.objects.filter(company=company, storecode=storecode)
    if on_or_before:
        qs = qs.filter(snapshot_date__lte=on_or_before)
    return qs.order_by("-snapshot_date").values_list("snapshot_date", flat=True).first()


def save_lifecycle_snapshot(
    company: str,
    storecode: str = "",
    *,
    snapshot_date: Optional[pydatetime.date] = None,
    dry_run: bool = False,
    batch_size: int = 500,
) -> Dict[str, Any]:
    """保存当日全店生命周期快照（幂等：同日复写）。"""
    from assistant.models import VipLifecycleSnapshot, VipLifecycleSnapshotSummary

    company = (company or "").strip()
    sc = (storecode or "").strip()
    snap = snapshot_date or pydatetime.date.today()
    cfg = get_lifecycle_config(company)

    qs = Vip.objects.filter(company=company, flag="Y")
    if sc:
        qs = qs.filter(storecode=sc)
    storecodes = [sc] if sc else list(qs.values_list("storecode", flat=True).distinct())

    total_saved = 0
    summaries: List[Dict[str, Any]] = []

    for store in storecodes:
        if not store:
            continue
        if not dry_run:
            VipLifecycleSnapshot.objects.filter(
                company=company, storecode=store, snapshot_date=snap
            ).delete()
            VipLifecycleSnapshotSummary.objects.filter(
                company=company, storecode=store, snapshot_date=snap
            ).delete()

        trans_map = _fetch_trans_stats_map(company, store)
        store_qs = qs.filter(storecode=store)
        counts: Dict[str, int] = {
            SEGMENT_ACTIVE: 0,
            SEGMENT_AT_RISK: 0,
            SEGMENT_SLEEPING: 0,
            SEGMENT_NEVER_VISITED: 0,
        }
        batch: List[VipLifecycleSnapshot] = []

        for v in store_qs.iterator(chunk_size=batch_size):
            vu = str(v.uuid)
            row = compute_vip_segment(
                company=company,
                storecode=store,
                vip=v,
                trans_stats=trans_map.get(vu),
                cfg=cfg,
                trend_stats=None,
            )
            seg = row["segment"]
            counts[seg] = counts.get(seg, 0) + 1
            days = row.get("days_since_last_visit")
            days_i = int(days) if str(days).isdigit() else None
            batch.append(
                VipLifecycleSnapshot(
                    company=company,
                    storecode=store,
                    snapshot_date=snap,
                    vipuuid=vu,
                    segment=seg,
                    sleeping_grade=row.get("sleeping_grade") or "",
                    days_since_last_visit=days_i,
                    vip_status=(v.status or "").strip(),
                )
            )
            if len(batch) >= batch_size:
                if not dry_run:
                    VipLifecycleSnapshot.objects.bulk_create(batch, batch_size=200)
                total_saved += len(batch)
                batch = []

        if batch:
            if not dry_run:
                VipLifecycleSnapshot.objects.bulk_create(batch, batch_size=200)
            total_saved += len(batch)

        summary_row = {
            "company": company,
            "storecode": store,
            "snapshot_date": snap.isoformat(),
            "segment_counts": counts,
            "total_vips": sum(counts.values()),
        }
        summaries.append(summary_row)
        if not dry_run:
            VipLifecycleSnapshotSummary.objects.create(
                company=company,
                storecode=store,
                snapshot_date=snap,
                segment_counts=counts,
                total_vips=sum(counts.values()),
            )

    return {
        "company": company,
        "storecode": sc or "*",
        "snapshot_date": snap.isoformat(),
        "dry_run": dry_run,
        "saved_rows": total_saved,
        "stores": summaries,
    }


def compute_lifecycle_migrations(
    company: str,
    storecode: str,
    *,
    days_back: int = 7,
    transition: str = "",
    limit: int = 200,
) -> Dict[str, Any]:
    """对比两个快照日期的分级迁移。"""
    from assistant.models import VipLifecycleSnapshot

    company = (company or "").strip()
    storecode = (storecode or "").strip()
    days_back = max(1, min(int(days_back), 365))
    lim = _lim(limit)
    today = pydatetime.date.today()
    to_date = _latest_snapshot_date(company, storecode) or today
    from_date = _latest_snapshot_date(company, storecode, on_or_before=to_date - pydatetime.timedelta(days=days_back))
    if not from_date or from_date >= to_date:
        return {
            "company": company,
            "storecode": storecode,
            "from_date": from_date.isoformat() if from_date else "",
            "to_date": to_date.isoformat(),
            "error": "缺少可对比的历史快照，请先执行 snapshot_vip_lifecycle",
            "migrations": [],
            "summary": {},
        }

    prev_qs = VipLifecycleSnapshot.objects.filter(
        company=company, storecode=storecode, snapshot_date=from_date
    )
    curr_qs = VipLifecycleSnapshot.objects.filter(
        company=company, storecode=storecode, snapshot_date=to_date
    )
    prev_map = {r.vipuuid: r for r in prev_qs}
    curr_map = {r.vipuuid: r for r in curr_qs}

    vip_meta: Dict[str, Vip] = {}
    if prev_map or curr_map:
        uuids = set(prev_map.keys()) | set(curr_map.keys())
        for v in Vip.objects.filter(company=company, storecode=storecode, uuid__in=uuids):
            vip_meta[str(v.uuid)] = v

    transition_filter = (transition or "").strip().lower()
    summary_counts: Dict[str, int] = {}
    rows: List[Dict[str, Any]] = []

    for vu, cur in curr_map.items():
        prev = prev_map.get(vu)
        if not prev:
            continue
        if prev.segment == cur.segment:
            continue
        key = f"{prev.segment}->{cur.segment}"
        summary_counts[key] = summary_counts.get(key, 0) + 1
        if transition_filter and transition_filter not in key:
            continue
        v = vip_meta.get(vu)
        rows.append(
            {
                "vipuuid": vu,
                "vcode": v.vcode if v else "",
                "vname": v.vname if v else "",
                "from_segment": prev.segment,
                "to_segment": cur.segment,
                "transition": key,
                "from_status": prev.vip_status,
                "to_status": cur.vip_status,
                "days_since_last_visit": cur.days_since_last_visit,
            }
        )

    rows.sort(key=lambda r: (r["to_segment"] != SEGMENT_AT_RISK, r["to_segment"] != SEGMENT_SLEEPING))
    truncated = len(rows) > lim
    rows = rows[:lim]

    return {
        "company": company,
        "storecode": storecode,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "days_back": days_back,
        "summary": summary_counts,
        "returned_count": len(rows),
        "truncated": truncated,
        "migrations": rows,
    }
