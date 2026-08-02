# coding=utf-8
"""AI 回访话术建议接口测试。"""
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
def vip():
    return Vip.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        flag="Y",
        vcode="0100594",
        vname="骨朵月客户",
        mtcode="13800000001",
        birth="19920901",
        viptype="10",
        ecode="1001",
    )


@pytest.fixture
def empl():
    return Empl.objects.create(company=COMPANY, flag="Y", ecode="1001", ename="顾问甲")


@pytest.fixture
def task(vip, empl):
    rule = CrmRule.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        rule_name="骨朵月回访",
        rule_type="custom",
        casetype="10",
        enabled="Y",
    )
    t = CrmCase.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        vipuuid=vip,
        rule=rule,
        casetype="10",
        casedesc="骨朵月专属回访，邀约到店体验",
        planbegindate=datetime.date.today(),
        planfinishdate=datetime.date.today(),
        status="10",
        ecode="1001",
        empl=empl,
    )
    VipCaseDetail.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        vipuuid=vip,
        casetype="10",
        detail="客户反馈上次骨朵月护理后皮肤变滑，最近忙没空到店",
        ecode="1001",
    )
    CrmCaseDetail.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        caseid=t,
        channel="20",
        outcome="30",
        detail="微信联系，客户说下周看看时间",
        detaildescription="微信联系，客户说下周看看时间",
        ecode=empl,
    )
    return t


def _mock_llm(calls):
    def fake_chat_completion(agent_id, messages, **kwargs):
        calls.append({"agent_id": agent_id, "messages": messages, "kwargs": kwargs})
        payload_1 = {
            "opening": "您好，我是负责您的顾问。",
            "care_points": ["先关心最近皮肤状态", "结合骨朵月护理反馈"],
            "invitation": "这周方便到店再做一次骨朵月护理吗？",
            "closing": "那先这样，祝您生活愉快。",
            "avoid": ["不要重复询问历史问题"],
        }
        payload_2 = {
            "opening": "上次骨朵月护理后感觉怎么样？",
            "care_points": ["关心护理后恢复", "顺势提一句老客户回馈"],
            "invitation": "这周帮您留了时间段，方便过来聊聊吗？",
            "closing": "那等您回复，我再帮您安排。",
            "avoid": ["不要催促", "不要承诺疗效"],
        }
        payload_3 = {
            "opening": "您好，我是您的顾问，想跟您确认下最近是否方便到店。",
            "care_points": ["简短问候近况"],
            "invitation": "方便的话我直接帮您安排到店护理。",
            "closing": "收到，我按您方便的时间安排。",
            "avoid": ["不要重复历史已答问题"],
        }
        return json.dumps(
            {"items": [payload_1, payload_2, payload_3]},
            ensure_ascii=False,
        ), "deepseek-chat"

    return fake_chat_completion


@pytest.mark.django_db
class TestTouchSuggestionApi:
    def test_suggest_returns_structured_script(self, client, task):
        calls = []
        with mock.patch("assistant.agents.chat_completion", side_effect=_mock_llm(calls)):
            resp = client.post(
                f"/crm/pc/tasks/{task.uuid}/suggest/",
                {"company": COMPANY, "channel": "20", "outcome": "50"},
                format="json",
            )
        assert resp.status_code == 200, resp.content
        data = resp.json()["data"]
        assert data["source"] == "llm"
        assert data["count"] == 3
        assert len(data["variants"]) == 3
        assert data["variants"][0]["opening"].startswith("您好")
        assert "骨朵月" in data["variants"][0]["invitation"]
        assert data["variants"][1]["opening"] != data["variants"][0]["opening"]
        assert len(calls) == 1
        assert calls[0]["agent_id"] == "deepseek"
        messages = calls[0]["messages"]
        joined = json.dumps(messages, ensure_ascii=False)
        assert "骨朵月专属回访，邀约到店体验" in joined
        assert "客户反馈上次骨朵月护理后皮肤变滑" in joined
        assert "微信联系，客户说下周看看时间" in joined
        assert "13800000001" not in joined
        assert "138****0001" in joined
        assert "3 个不同语气" in joined

    def test_suggest_falls_back_when_llm_fails(self, client, task):
        with mock.patch(
            "assistant.agents.chat_completion",
            side_effect=RuntimeError("llm down"),
        ):
            resp = client.post(
                f"/crm/pc/tasks/{task.uuid}/suggest/",
                {"company": COMPANY, "channel": "10"},
                format="json",
            )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["source"] == "fallback"
        assert data["count"] == 3
        assert len(data["variants"]) == 3
        for variant in data["variants"]:
            assert variant["opening"]
            assert variant["invitation"]
            assert len(variant["care_points"]) >= 1

    def test_suggest_scoped_by_company(self, client, vip):
        other_vip = Vip.objects.create(
            company="otherco",
            storecode="99",
            flag="Y",
            vcode="V999",
            vname="其他公司",
        )
        other_task = CrmCase.objects.create(
            company="otherco",
            storecode="99",
            vipuuid=other_vip,
            casetype="10",
            casedesc="他人任务",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
        )
        resp = client.post(
            f"/crm/pc/tasks/{other_task.uuid}/suggest/",
            {"company": COMPANY, "channel": "10"},
            format="json",
        )
        assert resp.status_code == 404

    def test_suggest_single_variant(self, client, task):
        calls = []
        with mock.patch("assistant.agents.chat_completion", side_effect=_mock_llm(calls)):
            resp = client.post(
                f"/crm/pc/tasks/{task.uuid}/suggest/",
                {"company": COMPANY, "channel": "10", "variants": 1},
                format="json",
            )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["count"] == 1
        assert len(data["variants"]) == 1


@pytest.mark.django_db
class TestStaticFallback:
    def test_sms_fallback_mentions_reply(self, vip, empl):
        task = CrmCase.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            vipuuid=vip,
            casetype="10",
            casedesc="生日关怀",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
        )
        from crm.touch_suggestion import build_touch_context, _static_fallback

        ctx = build_touch_context(COMPANY, STORECODE, task, channel="30")
        result = _static_fallback(ctx, "30")
        assert "回复" in result["invitation"]
