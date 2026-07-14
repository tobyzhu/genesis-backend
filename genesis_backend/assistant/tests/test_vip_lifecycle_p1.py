# coding=utf-8

import datetime as pydatetime

import pytest

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip
from assistant.vip_lifecycle import (
    personalize_recommended_actions,
    playbook_goals_for_segment,
    get_lifecycle_config,
    tool_vip_lifecycle_one,
)


@pytest.mark.django_db
def test_personalize_actions_with_template():
    vip = make_vip(telph="13800004444", vname="张小姐", ecode="E001")
    cfg = get_lifecycle_config(TEST_COMPANY)
    row = {
        "segment": "at_risk",
        "days_since_last_visit": 45,
        "lifetime_amount": 6000,
        "recent_amount": 500,
        "adviser_name": "李顾问",
    }
    actions = personalize_recommended_actions("at_risk", vip, row, cfg)
    assert actions
    assert actions[0].get("priority") == 1
    scripts = [a.get("suggested_script") for a in actions if a.get("suggested_script")]
    assert any("张小姐" in s for s in scripts)
    high_value = [a for a in actions if a.get("title") == "高价值专属关怀"]
    assert len(high_value) == 1


@pytest.mark.django_db
def test_playbook_goals_for_at_risk():
    goals = playbook_goals_for_segment("at_risk")
    assert goals
    assert any("唤醒" in g for g in goals)


@pytest.mark.django_db
def test_lifecycle_one_has_personalized_script():
    vip = make_vip(telph="13800005555", vname="王姐")
    make_expvstoll(
        vip,
        vsdate=(pydatetime.date.today() - pydatetime.timedelta(days=7)).strftime("%Y%m%d"),
        totmount="800",
    )
    row = tool_vip_lifecycle_one(TEST_COMPANY, TEST_STORECODE, telph=vip.telph)
    assert row.get("playbook_goals")
    actions = row.get("recommended_actions") or []
    assert actions
    assert actions[0].get("priority") == 1
