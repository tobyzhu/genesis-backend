# coding=utf-8

import datetime as pydatetime

import pytest

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip
from assistant.vip_lifecycle import (
    SEGMENT_AT_RISK,
    SEGMENT_SLEEPING,
    compute_lifecycle_batch,
    get_lifecycle_config,
    sync_sleeping_vip_status,
    tool_vip_lifecycle_one,
)
from baseinfo.models import Appoption, Vip


@pytest.mark.django_db
def test_lifecycle_sleeping_vip():
    vip = make_vip(telph="13800001111", vname="休眠客")
    make_expvstoll(vip, vsdate="20200101", totmount="100")

    result = compute_lifecycle_batch(TEST_COMPANY, TEST_STORECODE, segment=SEGMENT_SLEEPING, limit=50)
    uuids = {r["vipuuid"] for r in result["vips"]}
    assert str(vip.uuid) in uuids
    assert result["summary"]["segment_counts"].get(SEGMENT_SLEEPING, 0) >= 1


@pytest.mark.django_db
def test_sync_sleeping_updates_status():
    Appoption.objects.get_or_create(
        company=TEST_COMPANY,
        seg="vipstatus",
        itemname="10",
        defaults={"itemvalues": "活跃", "flag": "Y"},
    )
    Appoption.objects.get_or_create(
        company=TEST_COMPANY,
        seg="vipstatus",
        itemname="20",
        defaults={"itemvalues": "休眠", "flag": "Y"},
    )
    vip = make_vip(telph="13800002222", vname="待休眠", status="10")
    make_expvstoll(vip, vsdate="20200101", totmount="50")

    cfg = get_lifecycle_config(TEST_COMPANY)
    out = sync_sleeping_vip_status(TEST_COMPANY, TEST_STORECODE, dry_run=False)

    vip.refresh_from_db()
    assert vip.status in (cfg.status_sleeping, cfg.status_lost)


@pytest.mark.django_db
def test_lifecycle_one_returns_actions():
    vip = make_vip(telph="13800003333", vname="单客")
    make_expvstoll(
        vip,
        vsdate=( pydatetime.date.today() - pydatetime.timedelta(days=7) ).strftime("%Y%m%d"),
        totmount="200",
    )
    row = tool_vip_lifecycle_one(TEST_COMPANY, TEST_STORECODE, telph=vip.telph)
    assert row.get("segment")
    assert isinstance(row.get("recommended_actions"), list)
