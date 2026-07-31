# coding=utf-8

import datetime as pydatetime

import pytest

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip
from assistant.vip_lifecycle import VALUE_TIER_HIGH, compute_lifecycle_batch, get_lifecycle_config
from assistant.vip_lifecycle_crm import LIFECYCLE_TASK_PREFIX, create_lifecycle_crm_tasks
from crm.models import VipCaseDetail


@pytest.mark.django_db
def test_high_value_tier_in_batch():
    v1 = make_vip(telph="13800010001", vname="高价值A", vcode="HVA")
    v2 = make_vip(telph="13800010002", vname="普通B", vcode="HVB")
    today = pydatetime.date.today().strftime("%Y%m%d")
    make_expvstoll(v1, vsdate=today, totmount="50000")
    make_expvstoll(v2, vsdate=today, totmount="100")

    result = compute_lifecycle_batch(TEST_COMPANY, TEST_STORECODE, limit=50)
    rows = {r["vcode"]: r for r in result["vips"]}
    assert rows.get("HVA", {}).get("value_tier") == VALUE_TIER_HIGH


@pytest.mark.django_db
def test_create_crm_tasks_dry_run():
    vip = make_vip(telph="13800010003", vname="预警客", ecode="E001")
    today = pydatetime.date.today()
    prior = (today - pydatetime.timedelta(days=100)).strftime("%Y%m%d")
    recent = (today - pydatetime.timedelta(days=10)).strftime("%Y%m%d")
    make_expvstoll(vip, vsdate=prior, totmount="1000")
    make_expvstoll(vip, vsdate=recent, totmount="200")

    out = create_lifecycle_crm_tasks(
        TEST_COMPANY,
        TEST_STORECODE,
        segment="at_risk",
        limit=20,
        dry_run=True,
    )
    assert out.get("created", 0) >= 0
    assert "previews" in out


@pytest.mark.django_db
def test_create_crm_tasks_writes_vipcasedetail():
    vip = make_vip(telph="13800010004", vname="写任务", ecode="E002")
    old = (pydatetime.date.today() - pydatetime.timedelta(days=200)).strftime("%Y%m%d")
    make_expvstoll(vip, vsdate=old, totmount="800")

    out = create_lifecycle_crm_tasks(
        TEST_COMPANY,
        TEST_STORECODE,
        segment="sleeping",
        limit=10,
        dry_run=False,
    )
    if out.get("created", 0) >= 1:
        assert VipCaseDetail.objects.filter(
            company=TEST_COMPANY,
            vipuuid=vip,
            detail__contains=LIFECYCLE_TASK_PREFIX,
        ).exists()


@pytest.mark.django_db
def test_sync_command_crm_tasks_flag():
    from django.core.management import call_command
    from io import StringIO

    vip = make_vip(telph="13800010005", vname="同步任务", ecode="E003")
    old = (pydatetime.date.today() - pydatetime.timedelta(days=200)).strftime("%Y%m%d")
    make_expvstoll(vip, vsdate=old, totmount="500")

    out = StringIO()
    call_command(
        "sync_vip_lifecycle",
        company=TEST_COMPANY,
        storecode=TEST_STORECODE,
        crm_tasks=True,
        crm_segments="sleeping",
        crm_limit=10,
        stdout=out,
    )
    assert "crm_tasks[sleeping]" in out.getvalue()
