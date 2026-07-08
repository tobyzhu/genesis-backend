# coding=utf-8

import datetime as pydatetime
import uuid

import pytest

from assistant.tests.factories import (
    TEST_COMPANY,
    TEST_STORECODE,
    make_expvstoll,
    make_vip,
)
from assistant.vip_tools import tool_vip_sleeping_alert


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


def _days_ago(n: int) -> str:
    return (pydatetime.date.today() - pydatetime.timedelta(days=n)).strftime("%Y%m%d")


@pytest.mark.django_db
def test_sleeping_alert_includes_inactive_vip():
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="沉睡测试")
    make_expvstoll(vip, vsdate=_days_ago(120), totmount="88.00")

    result = tool_vip_sleeping_alert(
        TEST_COMPANY,
        TEST_STORECODE,
        inactive_days=90,
        critical_days=180,
        limit=500,
    )

    matches = [r for r in result["sleeping_vips"] if r["vipuuid"] == str(vip.uuid)]
    assert len(matches) == 1
    assert matches[0]["vname"] == "沉睡测试"
    assert matches[0]["days_since_last_visit"] >= 90


@pytest.mark.django_db
def test_sleeping_alert_excludes_recent_visitor():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    make_expvstoll(vip, vsdate=_days_ago(5), totmount="100.00")

    result = tool_vip_sleeping_alert(
        TEST_COMPANY,
        TEST_STORECODE,
        inactive_days=90,
        limit=500,
    )

    matches = [r for r in result["sleeping_vips"] if r["vipuuid"] == str(vip.uuid)]
    assert matches == []
