# coding=utf-8

import datetime as pydatetime
import uuid

import pytest

from assistant.data_tools import run_tool_plan
from assistant.tests.factories import (
    TEST_COMPANY,
    TEST_STORECODE,
    make_expvstoll,
    make_vip,
)
from assistant.vip_tools import VIP_ONLY_REGISTRY, tool_vip_profile


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


@pytest.mark.django_db
def test_run_tool_plan_vip_profile_and_churn():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    vsdate = pydatetime.date.today().strftime("%Y%m%d")
    make_expvstoll(vip, vsdate=vsdate, totmount="120.00")

    tools = [
        {"name": "vip_profile", "args": {"telph": telph}},
        {"name": "vip_churn_risk", "args": {"telph": telph}},
    ]
    results, errors = run_tool_plan(
        TEST_COMPANY, TEST_STORECODE, tools, registry=VIP_ONLY_REGISTRY
    )

    assert errors == []
    assert len(results) == 2
    assert all(r["ok"] for r in results)
    assert results[0]["data"]["profile"]["telph"] == telph
    assert results[1]["data"]["risk_level"] in {
        "active",
        "low",
        "medium",
        "high",
        "never_visited",
    }


def test_run_tool_plan_unknown_tool():
    results, errors = run_tool_plan(
        TEST_COMPANY,
        TEST_STORECODE,
        [{"name": "not_a_real_tool", "args": {}}],
        registry=VIP_ONLY_REGISTRY,
    )
    assert len(errors) == 1
    assert results[0]["ok"] is False


@pytest.mark.django_db
def test_vip_profile_registry_direct():
    """Smoke: tool registered and callable without DB when member missing."""
    out = tool_vip_profile(TEST_COMPANY, TEST_STORECODE, telph="19900000000")
    assert out.get("error") == "未找到会员"
