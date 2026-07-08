# coding=utf-8

import pytest

from assistant.plan_heuristic import _extract_days, _extract_top_n, heuristic_plan
from assistant.vip_tools import VIP_ONLY_REGISTRY


def _vip_tools_set():
    return set(VIP_ONLY_REGISTRY.keys()) | {"search_vips"}


def test_heuristic_vip_profile_and_churn_for_phone_question():
    plan = heuristic_plan(
        "vip_crm",
        "13812345678这个客户怎么样",
        _vip_tools_set(),
    )
    assert plan is not None
    names = [t["name"] for t in plan["tools"]]
    assert "vip_profile" in names
    assert "vip_churn_risk" in names
    profile_args = next(t["args"] for t in plan["tools"] if t["name"] == "vip_profile")
    assert profile_args.get("telph") == "13812345678"


def test_heuristic_sleeping_alert():
    plan = heuristic_plan(
        "vip_crm",
        "沉睡会员列表",
        _vip_tools_set(),
    )
    assert plan is not None
    assert any(t["name"] == "vip_sleeping_alert" for t in plan["tools"])


def test_heuristic_cash_ranking():
    plan = heuristic_plan(
        "vip_crm",
        "会员现金消费前10名",
        _vip_tools_set(),
    )
    assert plan is not None
    assert any(t["name"] == "vip_top_cash_consumption" for t in plan["tools"])


def test_heuristic_chitchat_returns_none():
    plan = heuristic_plan("vip_crm", "你好", _vip_tools_set())
    assert plan is None


def test_extract_days_three_months():
    assert _extract_days("最近3个月消费") == 90


def test_extract_top_n():
    assert _extract_top_n("前20名会员") == 20
