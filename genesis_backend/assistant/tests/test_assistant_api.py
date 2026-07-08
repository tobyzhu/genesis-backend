# coding=utf-8

import json
import random
import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from assistant.models import AssistantMessage, AssistantThread
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_expvstoll, make_vip


def _unique_telph() -> str:
    """11 位纯数字手机号（启发式 search_vips 依赖 \\d 匹配）。"""
    return "138" + "".join(str(random.randint(0, 9)) for _ in range(8))


@pytest.fixture
def staff_client(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username=f"staff_{uuid.uuid4().hex[:8]}",
        password="testpass",
        is_staff=True,
    )
    client = Client()
    client.force_login(user)
    return client, user


@pytest.mark.django_db
def test_sleeping_alert_api_returns_json(staff_client):
    client, _user = staff_client
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="API沉睡")
    make_expvstoll(vip, vsdate="20200101", totmount="50.00")

    resp = client.post(
        "/assistant/api/vip/sleeping-alert/",
        data=json.dumps(
            {
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "inactive_days": 90,
                "limit": 500,
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    sleeping = body["data"]["sleeping_vips"]
    assert any(r["vipuuid"] == str(vip.uuid) for r in sleeping)


@pytest.mark.django_db
def test_agents_and_profiles_api_smoke(staff_client):
    client, _user = staff_client

    agents = client.get("/assistant/api/agents/")
    assert agents.status_code == 200
    agents_body = agents.json()
    assert agents_body["ok"] is True
    assert isinstance(agents_body["agents"], list)
    assert len(agents_body["agents"]) >= 1

    profiles = client.get("/assistant/api/profiles/")
    assert profiles.status_code == 200
    profiles_body = profiles.json()
    assert profiles_body["ok"] is True
    ids = {p["id"] for p in profiles_body["profiles"]}
    assert "general" in ids
    assert "vip_crm" in ids


@pytest.mark.django_db
@patch("assistant.views.chat_completion")
def test_chat_api_heuristic_search_vips(mock_chat, staff_client):
    client, user = staff_client
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="聊天搜索")

    mock_chat.side_effect = [
        ("这不是 JSON", "mock-plan"),
        ("仍然不是 JSON", "mock-plan-retry"),
        ("已找到会员。", "mock-answer"),
    ]

    resp = client.post(
        "/assistant/api/chat/",
        data=json.dumps(
            {
                "message": f"手机号{telph}的会员是谁",
                "company": TEST_COMPANY,
                "storecode": TEST_STORECODE,
                "profile": "general",
                "agent": "deepseek",
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["ok"] is True
    assert body["answer"]
    parsed_tools = [t["name"] for t in body["plan"]["parsed"]["tools"]]
    assert "search_vips" in parsed_tools
    tool_names = [t["tool"] for t in body["tool_results"]]
    assert "search_vips" in tool_names
    search_result = next(t for t in body["tool_results"] if t["tool"] == "search_vips")
    assert search_result["ok"] is True
    assert any(r["vipuuid"] == str(vip.uuid) for r in search_result["data"])

    thread_id = body["thread_id"]
    thread = AssistantThread.objects.get(pk=thread_id, user=user)
    assert thread.company == TEST_COMPANY
    assert AssistantMessage.objects.filter(thread=thread).count() == 2


@pytest.mark.django_db
def test_export_datasets_api_from_tool_results(staff_client):
    client, _user = staff_client
    tool_results = [
        {
            "tool": "search_vips",
            "ok": True,
            "data": [
                {
                    "vipuuid": "uuid-001",
                    "vname": "导出测试",
                    "telph": "13800001111",
                }
            ],
        }
    ]

    resp = client.post(
        "/assistant/api/export/datasets/",
        data=json.dumps({"tool_results": tool_results}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["sheet_count"] >= 1
    assert isinstance(body["datasets"], list)
    assert len(body["datasets"][0]["rows"]) >= 1
    assert body["datasets"][0]["rows"][0]["vname"] == "导出测试"


@pytest.mark.django_db
def test_export_xlsx_api_returns_workbook(staff_client):
    client, _user = staff_client
    tool_results = [
        {
            "tool": "search_vips",
            "ok": True,
            "data": [{"vipuuid": "uuid-002", "vname": "XLSX测试", "telph": "13800002222"}],
        }
    ]

    resp = client.post(
        "/assistant/api/export/",
        data=json.dumps(
            {
                "format": "xlsx",
                "tool_results": tool_results,
                "filename": "ci-export.xlsx",
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200
    assert resp["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(resp.content) > 100
    assert resp.content[:2] == b"PK"


@pytest.mark.django_db
def test_export_api_rejects_empty_payload(staff_client):
    client, _user = staff_client

    resp = client.post(
        "/assistant/api/export/datasets/",
        data=json.dumps({"tool_results": []}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert resp.json()["ok"] is False
