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
from assistant.vip_tools import tool_vip_churn_risk


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


def _days_ago(n: int) -> str:
    return (pydatetime.date.today() - pydatetime.timedelta(days=n)).strftime("%Y%m%d")


@pytest.mark.django_db
def test_churn_risk_active_customer():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    make_expvstoll(vip, vsdate=_days_ago(7), totmount="150.00")

    result = tool_vip_churn_risk(TEST_COMPANY, TEST_STORECODE, telph=telph, inactive_days=90)

    assert result["risk_level"] == "active"
    assert result["last_visit"]["days_since_last_visit"] == 7


@pytest.mark.django_db
def test_churn_risk_never_visited():
    telph = _unique_telph()
    make_vip(telph=telph)

    result = tool_vip_churn_risk(TEST_COMPANY, TEST_STORECODE, telph=telph)

    assert result["risk_level"] == "never_visited"
    assert "从未有效消费" in result["risk_factors"]


@pytest.mark.django_db
def test_churn_risk_inactive_customer():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    make_expvstoll(vip, vsdate=_days_ago(120), totmount="100.00")

    result = tool_vip_churn_risk(
        TEST_COMPANY, TEST_STORECODE, telph=telph, inactive_days=90, critical_days=180
    )

    assert result["risk_level"] in {"medium", "high"}
    assert any("未到店" in f for f in result["risk_factors"])


@pytest.mark.django_db
def test_churn_risk_declining_spending_trend():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    make_expvstoll(vip, vsdate=_days_ago(150), totmount="800.00")
    make_expvstoll(vip, vsdate=_days_ago(140), totmount="200.00")
    make_expvstoll(vip, vsdate=_days_ago(20), totmount="50.00")

    result = tool_vip_churn_risk(
        TEST_COMPANY, TEST_STORECODE, telph=telph, trend_days=90, inactive_days=90
    )

    assert result["trend"]["amount_trend"] == "declining"
    assert result["risk_level"] == "medium"
    assert any("下降" in f for f in result["risk_factors"])
