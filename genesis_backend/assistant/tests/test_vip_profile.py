# coding=utf-8

import datetime as pydatetime
import uuid

import pytest

from assistant.tests.factories import (
    TEST_COMPANY,
    TEST_STORECODE,
    make_expense,
    make_expvstoll,
    make_vip,
)
from assistant.vip_tools import tool_vip_profile


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


def _days_ago(n: int) -> str:
    return (pydatetime.date.today() - pydatetime.timedelta(days=n)).strftime("%Y%m%d")


@pytest.mark.django_db
def test_vip_profile_by_telph_returns_consumption_and_preferred_items():
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="画像测试")
    recent_vsdate = _days_ago(10)
    t1 = make_expvstoll(vip, vsdate=_days_ago(60), totmount="200.00")
    t2 = make_expvstoll(vip, vsdate=recent_vsdate, totmount="300.00")
    make_expense(t1, srvcode="SVC_A", s_mount="200.00")
    make_expense(t2, srvcode="SVC_B", s_mount="300.00")

    result = tool_vip_profile(TEST_COMPANY, TEST_STORECODE, telph=telph)

    assert "error" not in result
    assert result["profile"]["vname"] == "画像测试"
    assert result["profile"]["telph"] == telph
    assert result["consumption"]["lifetime_amount"] == 500.0
    assert result["consumption"]["visit_count"] == 2
    expected_last = f"{recent_vsdate[:4]}-{recent_vsdate[4:6]}-{recent_vsdate[6:8]}"
    assert result["consumption"]["last_visit_date"] == expected_last
    items = result["preferred_items"]["items"]
    assert len(items) >= 1
    assert items[0]["srvcode"] in {"SVC_A", "SVC_B"}
    assert items[0]["total_amount"] >= 200.0


@pytest.mark.django_db
def test_vip_profile_not_found():
    result = tool_vip_profile(TEST_COMPANY, TEST_STORECODE, telph="19900009999")
    assert result.get("error") == "未找到会员"


@pytest.mark.django_db
def test_vip_profile_store_isolation():
    telph = _unique_telph()
    make_vip(telph=telph, storecode=TEST_STORECODE)
    result = tool_vip_profile(TEST_COMPANY, "88", telph=telph)
    assert result.get("error") == "未找到会员"
