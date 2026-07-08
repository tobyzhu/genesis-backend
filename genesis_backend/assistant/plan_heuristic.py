#coding = utf-8
"""规划失败时的启发式工具选择（关键词 → tools JSON）。"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set


def _extract_days(message: str, default: int = 90) -> int:
    m = re.search(r"(\d+)\s*个?月", message)
    if m:
        try:
            return max(30, min(int(m.group(1)) * 30, 3650))
        except (TypeError, ValueError):
            pass
    m = re.search(r"(\d+)\s*天", message)
    if m:
        try:
            return max(1, min(int(m.group(1)), 3650))
        except (TypeError, ValueError):
            pass
    if re.search(r"半年", message):
        return 180
    if re.search(r"一年|12\s*个?月", message):
        return 365
    return default


def _extract_top_n(message: str, default: int = 20) -> int:
    for pat in (r"前\s*(\d+)\s*名", r"前\s*(\d+)", r"top\s*(\d+)", r"TOP\s*(\d+)"):
        m = re.search(pat, message, flags=re.IGNORECASE)
        if m:
            try:
                return max(1, min(int(m.group(1)), 100))
            except (TypeError, ValueError):
                continue
    return default


def _is_vip_ranking_query(msg: str) -> bool:
    if "会员" not in msg and "客户" not in msg:
        return False
    return bool(re.search(r"前\s*\d+|最高|top|TOP|排名|排行", msg, re.IGNORECASE))


def _ranking_tool_args(msg: str, default_days: int = 180, default_top_n: int = 30) -> Dict[str, Any]:
    return {
        "days": _extract_days(msg, default=default_days),
        "top_n": _extract_top_n(msg, default=default_top_n),
    }


def _detect_vip_ranking_tools(msg: str, allowed_tools: Set[str]) -> List[Dict[str, Any]]:
    """识别会员消费排行类问题，可返回多个工具（如同时问现金+卡付）。"""
    if not _is_vip_ranking_query(msg):
        return []

    specs = [
        (
            "vip_top_cash_consumption",
            lambda m: ("现金" in m) and not re.search(r"卡付|刷卡|储值卡", m),
        ),
        (
            "vip_top_card_consumption",
            lambda m: bool(re.search(r"卡付|刷卡|储值卡|卡类消费|卡消费", m)),
        ),
        (
            "vip_top_send_consumption",
            lambda m: bool(re.search(r"赠送|赠金", m)),
        ),
        (
            "vip_top_service_consumption",
            lambda m: bool(re.search(r"服务类|服务消费|服务项目", m))
            or ("服务" in m and "商品" not in m and "CRM" not in m.upper()),
        ),
        (
            "vip_top_goods_consumption",
            lambda m: bool(re.search(r"商品类|商品消费|产品消费|货品", m)) or ("商品" in m),
        ),
    ]

    matched: List[Dict[str, Any]] = []
    for tool_name, pred in specs:
        if tool_name not in allowed_tools:
            continue
        if pred(msg):
            matched.append({"name": tool_name, "args": _ranking_tool_args(msg)})

    if matched:
        return matched

    if re.search(r"各类|分别|五种|全部|多种", msg) and re.search(r"消费", msg):
        all_rank_tools = [name for name, _ in specs if name in allowed_tools]
        if all_rank_tools:
            args = _ranking_tool_args(msg)
            return [{"name": name, "args": dict(args)} for name in all_rank_tools]

    return []


def heuristic_plan(
    profile_id: str,
    message: str,
    allowed_tools: Set[str],
) -> Optional[Dict[str, Any]]:
    """根据用户问题猜测 tools 列表；仅返回 allowed_tools 内的工具。"""
    msg = (message or "").strip()
    if not msg:
        return None

    tools: List[Dict[str, Any]] = []

    ranking_tools = _detect_vip_ranking_tools(msg, allowed_tools)
    if ranking_tools:
        tools.extend(ranking_tools)

    if "vip_sleeping_alert" in allowed_tools and not tools:
        if ("沉睡" in msg or "流失" in msg) and ("会员" in msg or "客户" in msg):
            tools.append(
                {
                    "name": "vip_sleeping_alert",
                    "args": {
                        "inactive_days": _extract_days(msg, default=90),
                        "top_n": _extract_top_n(msg, default=50),
                    },
                }
            )

    if "list_unsettled_guests" in allowed_tools and not tools:
        if "未结账" in msg or "挂单" in msg:
            tools.append({"name": "list_unsettled_guests", "args": {}})

    if "search_vips" in allowed_tools and not tools:
        m = re.search(r"(?:手机|电话)[号\s]*[为是]?\s*(\d{7,15})", msg)
        if m:
            tools.append({"name": "search_vips", "args": {"keyword": m.group(1)}})
        elif re.search(r"查.{0,6}会员|会员.{0,4}是谁|谁的手机", msg):
            m2 = re.search(r"[\u4e00-\u9fff]{2,8}", msg)
            if m2:
                tools.append({"name": "search_vips", "args": {"keyword": m2.group(0)}})

    if not tools and profile_id == "vip_crm":
        phone_m = re.search(r"1[3-9]\d{9}", msg)
        profile_intent = bool(
            re.search(r"怎么样|如何|画像|分析|概况|情况|流失|风险|还回来|会来", msg)
        )
        if phone_m and profile_intent:
            telph = phone_m.group(0)
            if "vip_profile" in allowed_tools:
                tools.append({"name": "vip_profile", "args": {"telph": telph}})
            if "vip_churn_risk" in allowed_tools and re.search(r"流失|风险|还会|回来", msg):
                tools.append(
                    {
                        "name": "vip_churn_risk",
                        "args": {
                            "telph": telph,
                            "inactive_days": _extract_days(msg, default=90),
                        },
                    }
                )
            elif "vip_churn_risk" in allowed_tools and "vip_profile" in allowed_tools:
                tools.append({"name": "vip_churn_risk", "args": {"telph": telph}})

    if "vip_maintenance_summary" in allowed_tools and not tools:
        if ("会员" in msg or "客户" in msg) and re.search(r"维护|新增|活跃|沉睡|复购", msg):
            tools.append(
                {
                    "name": "vip_maintenance_summary",
                    "args": {"days": _extract_days(msg, default=90)},
                }
            )

    if not tools:
        return None

    brief_parts = [t["name"] for t in tools]
    return {"tools": tools, "brief": "启发式规划: " + ", ".join(brief_parts)}
