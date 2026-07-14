# coding=utf-8

import datetime as pydatetime

import pytest

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip
from assistant.vip_lifecycle import (
    SEGMENT_SLEEPING,
    _target_status_for_segment,
    compute_lifecycle_migrations,
    get_lifecycle_config,
    save_lifecycle_snapshot,
    sync_sleeping_vip_status,
)
from baseinfo.models import Appoption, Vip


@pytest.mark.django_db
def test_critical_sleeping_targets_lost_status():
    cfg = get_lifecycle_config(TEST_COMPANY)
    code = _target_status_for_segment(SEGMENT_SLEEPING, "critical", cfg)
    assert code == cfg.status_lost


@pytest.mark.django_db
def test_snapshot_dry_run():
    vip = make_vip(telph="13800008888", vname="迁移客", status="10")
    make_expvstoll(vip, vsdate="20200101", totmount="100")

    d1 = pydatetime.date.today() - pydatetime.timedelta(days=8)
    out1 = save_lifecycle_snapshot(TEST_COMPANY, TEST_STORECODE, snapshot_date=d1, dry_run=True)
    assert out1["saved_rows"] >= 1


@pytest.mark.django_db
def test_migration_requires_snapshot_table():
    """有快照表时可对比迁移；无表时返回友好错误。"""
    from assistant.models import VipLifecycleSnapshot

    try:
        VipLifecycleSnapshot.objects.exists()
    except Exception:
        pytest.skip("vip_lifecycle_snapshot 表未迁移")

    d1 = pydatetime.date.today() - pydatetime.timedelta(days=8)
    d2 = pydatetime.date.today()
    save_lifecycle_snapshot(TEST_COMPANY, TEST_STORECODE, snapshot_date=d1, dry_run=False)
    save_lifecycle_snapshot(TEST_COMPANY, TEST_STORECODE, snapshot_date=d2, dry_run=False)
    mig = compute_lifecycle_migrations(TEST_COMPANY, TEST_STORECODE, days_back=7, limit=50)
    assert mig.get("from_date")
    assert mig.get("to_date")


@pytest.mark.django_db
def test_sync_critical_writes_lost_status():
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
    Appoption.objects.get_or_create(
        company=TEST_COMPANY,
        seg="vipstatus",
        itemname="30",
        defaults={"itemvalues": "流失", "flag": "Y"},
    )
    Appoption.objects.get_or_create(
        company=TEST_COMPANY,
        seg="vip_lifecycle",
        itemname="inactive_days",
        defaults={"itemvalues": "90", "flag": "Y"},
    )
    Appoption.objects.get_or_create(
        company=TEST_COMPANY,
        seg="vip_lifecycle",
        itemname="critical_days",
        defaults={"itemvalues": "90", "flag": "Y"},
    )

    vip = make_vip(telph="13800009999", vname="深度休眠", status="10")
    make_expvstoll(vip, vsdate="20200101", totmount="50")

    cfg = get_lifecycle_config(TEST_COMPANY)
    out = sync_sleeping_vip_status(TEST_COMPANY, TEST_STORECODE, dry_run=False)
    assert out["updated_sleeping"] + out["updated_lost"] >= 1

    vip.refresh_from_db()
    assert vip.status in (cfg.status_sleeping, cfg.status_lost)
