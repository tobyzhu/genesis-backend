# coding=utf-8

from assistant.vip_tools import (
    _churn_risk_level,
    _churn_trend_label,
    _days_between,
    _parse_yyyymmdd_date,
    _risk_level,
)


def test_parse_yyyymmdd_date():
    d = _parse_yyyymmdd_date("20240115")
    assert d is not None
    assert d.year == 2024 and d.month == 1 and d.day == 15


def test_days_between():
    a = _parse_yyyymmdd_date("20240101")
    b = _parse_yyyymmdd_date("20240111")
    assert _days_between(a, b) == 10


def test_churn_trend_label():
    assert _churn_trend_label(100, 200) == "declining"
    assert _churn_trend_label(200, 100) == "increasing"
    assert _churn_trend_label(100, 100) == "stable"
    assert _churn_trend_label(0, 0) == "no_activity"


def test_churn_risk_level_high_when_inactive_and_declining():
    level = _churn_risk_level(
        days_since=100,
        never_visited=False,
        inactive_days=90,
        critical_days=180,
        amount_trend="declining",
        visit_trend="stable",
    )
    assert level == "high"


def test_churn_risk_level_never_visited():
    assert (
        _churn_risk_level(
            days_since=None,
            never_visited=True,
            inactive_days=90,
            critical_days=180,
            amount_trend="no_activity",
            visit_trend="no_activity",
        )
        == "never_visited"
    )


def test_sleeping_risk_level_critical():
    assert _risk_level(200, False, 180) == "critical"
    assert _risk_level(50, True, 180) == "never_visited"
