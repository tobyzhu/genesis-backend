# coding=utf-8

import json
import random
import uuid

import pytest
from django.contrib.auth import get_user_model

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip
from common.models import GenesisUserProfile


@pytest.fixture
def mp_user(db):
    user_model = get_user_model()
    ecode = f"mp_{uuid.uuid4().hex[:6]}"
    user = user_model.objects.create_user(username=ecode, password="testpass")
    profile = GenesisUserProfile.objects.create(
        user=user,
        company=TEST_COMPANY,
        default_storecode=TEST_STORECODE,
        storelist=TEST_STORECODE,
        employee_code=ecode,
    )
    return user, profile, ecode


@pytest.mark.django_db
def test_mp_lifecycle_batch_api(client, mp_user):
    _user, _profile, ecode = mp_user
    vip = make_vip(telph="13800006666", vname="预警客")
    make_expvstoll(vip, vsdate="20200101", totmount="100")

    resp = client.post(
        "/assistant/mp/api/vip/lifecycle/",
        data=json.dumps(
            {
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "ecode": ecode,
                "segment": "sleeping",
                "limit": 20,
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["ok"] is True
    assert body["data"]["summary"]["returned_count"] >= 1


@pytest.mark.django_db
def test_mp_lifecycle_one_api(client, mp_user):
    _user, _profile, ecode = mp_user
    vip = make_vip(telph="13800007777", vname="方案客")
    make_expvstoll(
        vip,
        vsdate="20240101",
        totmount="3000",
    )

    resp = client.post(
        "/assistant/mp/api/vip/lifecycle/one/",
        data=json.dumps(
            {
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "ecode": ecode,
                "vipuuid": str(vip.uuid),
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["ok"] is True
    assert body["data"]["recommended_actions"]
    assert body["data"].get("playbook_goals")


@pytest.mark.django_db
def test_mp_lifecycle_crm_tasks_api(client, mp_user):
    _user, _profile, ecode = mp_user
    vip = make_vip(telph="13800008888", vname="任务客", ecode=ecode)
    old = "20200101"
    make_expvstoll(vip, vsdate=old, totmount="600")

    resp = client.post(
        "/assistant/mp/api/vip/lifecycle/crm-tasks/",
        data=json.dumps(
            {
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "ecode": ecode,
                "segment": "sleeping",
                "dry_run": True,
                "limit": 10,
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["ok"] is True
    assert "result" in body
