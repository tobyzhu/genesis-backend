# coding=utf-8
"""小程序端客户关怀 API 测试：员工个人视角。"""
from __future__ import annotations

import datetime
import json
from unittest import mock

import pytest
from rest_framework.test import APIClient

from baseinfo.models import Empl, Vip
from crm.models import CrmCase, CrmCaseDetail, CrmRule, VipCaseDetail

COMPANY = "testco"
STORECODE = "99"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def data():
    Empl.objects.filter(company=COMPANY).delete()
    Vip.objects.filter(company=COMPANY).delete()
    CrmCase.objects.filter(company=COMPANY).delete()
    CrmRule.objects.filter(company=COMPANY).delete()
    VipCaseDetail.objects.filter(company=COMPANY).delete()
    emp1 = Empl.objects.create(company=COMPANY, storecode=STORECODE, flag="Y", ecode="1001", ename="顾问甲")
    emp2 = Empl.objects.create(company=COMPANY, storecode=STORECODE, flag="Y", ecode="1002", ename="顾问乙")
    vip = Vip.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        flag="Y",
        vcode="0100594",
        vname="骨朵月客户",
        mtcode="13800000001",
        birth="19920901",
        ecode="1001",
    )
    today = datetime.date.today()
    task1 = CrmCase.objects.create(
        company=COMPANY, storecode=STORECODE, vipuuid=vip,
        casetype="10", casedesc="我的回访", status="10",
        planbegindate=today, planfinishdate=today, ecode="1001", empl=emp1,
    )
    task2 = CrmCase.objects.create(
        company=COMPANY, storecode=STORECODE, vipuuid=vip,
        casetype="10", casedesc="他人回访", status="10",
        planbegindate=today, planfinishdate=today, ecode="1002", empl=emp2,
    )
    return {"emp1": emp1, "emp2": emp2, "vip": vip, "task1": task1, "task2": task2}


@pytest.mark.django_db
class TestMpTaskScope:
    def test_list_requires_ecode(self, client, data):
        resp = client.get("/crm/mp/tasks/", {"company": COMPANY, "storecode": STORECODE})
        assert resp.status_code == 400

    def test_list_only_own_tasks(self, client, data):
        resp = client.get(
            "/crm/mp/tasks/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001"},
        )
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["casedesc"] == "我的回访"

    def test_summary_scoped(self, client, data):
        resp = client.get(
            "/crm/mp/tasks/summary/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001"},
        )
        assert resp.status_code == 200
        counts = resp.json()["data"]["counts"]
        assert counts["total"] == 1
        assert counts["today"] == 1

    def test_cannot_open_other_task(self, client, data):
        resp = client.get(
            f"/crm/mp/tasks/{data['task2'].uuid}/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001"},
        )
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMpTaskExecution:
    def test_attempt_defaults_to_self(self, client, data):
        resp = client.post(
            f"/crm/mp/tasks/{data['task1'].uuid}/attempt/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "detail": "微信联系成功"},
            format="json",
        )
        assert resp.status_code == 201, resp.content
        detail = CrmCaseDetail.objects.get(caseid_id=data["task1"].uuid)
        assert detail.ecode.ecode == "1001"
        assert detail.creater == "1001"
        log = VipCaseDetail.objects.get(vipuuid=data["vip"])
        assert log.ecode == "1001"
        data["task1"].refresh_from_db()
        assert data["task1"].status == "20"

    def test_complete_and_pause(self, client, data):
        resp = client.post(
            f"/crm/mp/tasks/{data['task1'].uuid}/complete/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "note": "已完成回访"},
            format="json",
        )
        assert resp.status_code == 200
        data["task1"].refresh_from_db()
        assert data["task1"].status == "30"
        assert data["task1"].finishedate == datetime.date.today()

        resp = client.post(
            f"/crm/mp/tasks/{data['task1'].uuid}/status/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "status": "40"},
            format="json",
        )
        assert resp.status_code == 200
        data["task1"].refresh_from_db()
        assert data["task1"].status == "40"

    def test_delete_attempt_scoped_to_self(self, client, data):
        resp = client.post(
            f"/crm/mp/tasks/{data['task1'].uuid}/attempt/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "detail": "删除我自己的触达"},
            format="json",
        )
        assert resp.status_code == 201
        attempt_uuid = resp.json()["data"]["uuid"]

        resp = client.delete(
            f"/crm/mp/tasks/{data['task1'].uuid}/attempt/{attempt_uuid}/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001"},
        )
        assert resp.status_code == 200
        assert not CrmCaseDetail.objects.filter(uuid=attempt_uuid, flag="Y").exists()
        assert not VipCaseDetail.objects.filter(caseid=data["task1"].uuid, flag="Y").exists()

        resp = client.post(
            f"/crm/mp/tasks/{data['task2'].uuid}/attempt/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1002", "detail": "别人的触达"},
            format="json",
        )
        assert resp.status_code == 201
        other_attempt = resp.json()["data"]["uuid"]
        resp = client.delete(
            f"/crm/mp/tasks/{data['task2'].uuid}/attempt/{other_attempt}/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001"},
        )
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMpSuggest:
    def test_suggest_includes_employee_name_and_variants(self, client, data):
        def fake_chat_completion(agent_id, messages, **kwargs):
            payload = {
                "opening": "我是顾问甲，来关心您。",
                "care_points": ["关怀点"],
                "invitation": "这周到店护理吗？",
                "closing": "好的。",
                "avoid": ["不要重复"],
            }
            return json.dumps({"items": [payload, payload, payload]}, ensure_ascii=False), "deepseek-chat"

        with mock.patch("assistant.agents.chat_completion", side_effect=fake_chat_completion):
            resp = client.post(
                f"/crm/mp/tasks/{data['task1'].uuid}/suggest/",
                {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "channel": "20", "variants": 3},
                format="json",
            )
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["count"] == 3
        assert result["variants"][0]["opening"].startswith("我是顾问甲")


@pytest.mark.django_db
class TestMpTimelineAndSearch:
    def test_timeline_quick_log_defaults_self(self, client, data):
        resp = client.post(
            "/crm/mp/timeline/",
            {
                "company": COMPANY,
                "storecode": STORECODE,
                "ecode": "1001",
                "vipuuid": str(data["vip"].uuid),
                "detail": "随手记一条",
            },
            format="json",
        )
        assert resp.status_code == 201
        log = VipCaseDetail.objects.get(vipuuid=data["vip"])
        assert log.ecode == "1001"
        assert log.creater == "1001"

    def test_vip_search_scoped(self, client, data):
        resp = client.get(
            "/crm/mp/vip-search/",
            {"company": COMPANY, "storecode": STORECODE, "ecode": "1001", "keyword": "骨朵"},
        )
        assert resp.status_code == 200
        rows = resp.json()["data"]
        assert any(r["vcode"] == "0100594" for r in rows)
