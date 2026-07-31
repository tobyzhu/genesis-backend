# coding=utf-8

import json
import random
import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from assistant.models import AssistantMessage, AssistantThread
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_vip
from common.models import GenesisUserProfile


def _unique_telph() -> str:
    return "138" + "".join(str(random.randint(0, 9)) for _ in range(8))


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
def test_mp_chat_requires_ecode(client):
    resp = client.post(
        "/assistant/mp/api/chat/",
        data=json.dumps(
            {
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "message": "你好",
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


@pytest.mark.django_db
@patch("assistant.views.chat_completion")
def test_mp_chat_api_heuristic_search_vips(mock_chat, client, mp_user):
    _user, _profile, ecode = mp_user
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="小程序助手搜索")

    mock_chat.side_effect = [
        ("这不是 JSON", "mock-plan"),
        ("仍然不是 JSON", "mock-plan-retry"),
        ("已找到会员。", "mock-answer"),
    ]

    resp = client.post(
        "/assistant/mp/api/chat/",
        data=json.dumps(
            {
                "message": f"手机号{telph}的会员是谁",
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "ecode": ecode,
                "profile": "general",
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["ok"] is True
    assert body["answer"]
    assert body["thread_id"]

    detail = client.get(
        f"/assistant/mp/api/threads/{body['thread_id']}/"
        f"?company={TEST_COMPANY}&storecode={TEST_STORECODE}&ecode={ecode}"
    )
    assert detail.status_code == 200
    detail_body = detail.json()
    assert len(detail_body["messages"]) >= 2
    roles = {m["role"] for m in detail_body["messages"]}
    assert "user" in roles
    assert "assistant" in roles

    assert AssistantThread.objects.filter(pk=body["thread_id"]).exists()
    assert AssistantMessage.objects.filter(thread_id=body["thread_id"]).count() >= 2
