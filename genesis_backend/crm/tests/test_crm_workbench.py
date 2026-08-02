# coding=utf-8
"""客户关怀工作台：规则引擎 + PC API + 任务/触达/流水 测试。"""
from __future__ import annotations

import datetime

import pytest
from rest_framework.test import APIClient

from baseinfo.models import Empl, Vip
from cashier.models import Expvstoll
from crm.crm_rules import generate_crm_cases
from crm.models import CrmCase, CrmCaseDetail, CrmRule, VipCaseDetail

COMPANY = "testco"
STORECODE = "99"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def vip():
    return Vip.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        flag="Y",
        vcode="V001",
        vname="张三",
        mtcode="13800000001",
        viptype="10",
        sex="男",
        birth="0901",
        indate=datetime.date(2024, 1, 1),
        telph="13800000001",
        ecode="1001",
        ecode2="1002",
    )


@pytest.fixture
def empl():
    return Empl.objects.create(
        company=COMPANY,
        flag="Y",
        ecode="1001",
        ename="顾问甲",
    )


@pytest.fixture
def birthday_rule():
    return CrmRule.objects.create(
        company=COMPANY,
        storecode=STORECODE,
        rule_name="下月生日关怀",
        rule_type="birthday",
        casetype="10",
        month_offset=1,
        assignee_policy="vip_ecode",
        enabled="Y",
    )


@pytest.mark.django_db
class TestRuleCrud:
    def test_dicts(self, client):
        resp = client.get("/crm/pc/dicts/", {"company": COMPANY})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert any(item["value"] == "birthday" for item in data["rule_type"])
        assert any(item["value"] == "10" for item in data["channel"])

    def test_create_list_update_delete(self, client):
        resp = client.post(
            "/crm/pc/rules/",
            {
                "company": COMPANY,
                "storecode": STORECODE,
                "rule_name": "成交回访",
                "rule_type": "transaction",
                "days_offset": 7,
                "ttype": "S",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.content
        rule = resp.json()["data"]
        assert rule["rule_type"] == "transaction"

        resp = client.get("/crm/pc/rules/", {"company": COMPANY})
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

        resp = client.put(
            f"/crm/pc/rules/{rule['uuid']}/",
            {"company": COMPANY, "rule_name": "成交回访-改", "days_offset": 10},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["rule_name"] == "成交回访-改"

        resp = client.delete(f"/crm/pc/rules/{rule['uuid']}/?company={COMPANY}")
        assert resp.status_code == 200
        assert not CrmRule.objects.filter(uuid=rule["uuid"], flag="Y").exists()


@pytest.mark.django_db
class TestRuleEngine:
    def test_birthday_generation_dedupe(self, client, vip, empl, birthday_rule):
        target = datetime.date(2026, 8, 1)
        preview = generate_crm_cases(
            COMPANY,
            STORECODE,
            rule=birthday_rule,
            target_date=target,
            dry_run=True,
        )
        assert preview["created"] == 0
        assert len(preview["previews"]) == 1

        result = generate_crm_cases(
            COMPANY,
            STORECODE,
            rule=birthday_rule,
            target_date=target,
            dry_run=False,
        )
        assert result["created"] == 1
        task = CrmCase.objects.get(vipuuid=vip, rule=birthday_rule)
        assert task.status == "10"
        assert task.planbegindate == datetime.date(2026, 9, 1)
        assert task.planfinishdate == datetime.date(2026, 9, 30)
        assert task.ecode == "1001"
        assert task.empl is not None

        again = generate_crm_cases(
            COMPANY,
            STORECODE,
            rule=birthday_rule,
            target_date=target,
            dry_run=False,
        )
        assert again["created"] == 0
        assert again["skipped"] == 1
        assert CrmCase.objects.filter(vipuuid=vip, rule=birthday_rule).count() == 1

    def test_transaction_generation(self, vip, empl):
        rule = CrmRule.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            rule_name="服务回访",
            rule_type="transaction",
            casetype="40",
            days_offset=7,
            ttype="S",
            assignee_policy="vip_ecode",
            enabled="Y",
        )
        trans_date = datetime.date.today() - datetime.timedelta(days=7)
        Expvstoll.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            flag="Y",
            valiflag="Y",
            ttype="S",
            vipuuid=vip,
            vsdate=trans_date.strftime("%Y%m%d"),
        )
        result = generate_crm_cases(COMPANY, STORECODE, rule=rule, dry_run=False)
        assert result["created"] == 1
        task = CrmCase.objects.get(vipuuid=vip, rule=rule)
        assert task.vsdate == trans_date
        assert task.planbegindate == datetime.date.today()
        assert task.casetype == "40"

    def test_birthday_full_date_format(self, client, empl):
        vip_full = Vip.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            flag="Y",
            vcode="V099",
            vname="全格式生日",
            mtcode="13800000009",
            birth="19920901",
            ecode="1001",
        )
        rule = CrmRule.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            rule_name="下月生日关怀-全格式",
            rule_type="birthday",
            casetype="10",
            month_offset=1,
            assignee_policy="vip_ecode",
            enabled="Y",
        )
        result = generate_crm_cases(
            COMPANY,
            STORECODE,
            rule=rule,
            target_date=datetime.date(2026, 8, 1),
            dry_run=False,
        )
        assert result["created"] == 1
        task = CrmCase.objects.get(vipuuid=vip_full, rule=rule)
        assert task.planbegindate == datetime.date(2026, 9, 1)

    def test_preview_and_run_api(self, client, vip, birthday_rule):
        url = f"/crm/pc/rules/{birthday_rule.uuid}/preview/"
        resp = client.get(url, {"company": COMPANY, "storecode": STORECODE, "date": "2026-08-01"})
        assert resp.status_code == 200
        assert resp.json()["data"]["created"] == 0
        assert len(resp.json()["data"]["previews"]) == 1

        url = f"/crm/pc/rules/{birthday_rule.uuid}/run/"
        resp = client.post(url, {"company": COMPANY, "storecode": STORECODE, "date": "2026-08-01"}, format="json")
        assert resp.status_code == 200
        assert resp.json()["data"]["created"] == 1
        assert CrmCase.objects.filter(vipuuid=vip, rule=birthday_rule).exists()


@pytest.mark.django_db
class TestTaskWorkflow:
    def test_create_task_and_attempt_complete(self, client, vip, empl):
        resp = client.post(
            "/crm/pc/tasks/",
            {
                "company": COMPANY,
                "storecode": STORECODE,
                "vipuuid": str(vip.uuid),
                "casetype": "10",
                "casedesc": "生日关怀回访",
                "planbegindate": "2026-09-01",
                "planfinishdate": "2026-09-30",
                "ecode": "1001",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.content
        task = resp.json()["data"]
        assert task["vip"]["vname"] == "张三"

        resp = client.get("/crm/pc/tasks/", {"company": COMPANY, "storecode": STORECODE})
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 1

        resp = client.get(f"/crm/pc/tasks/{task['uuid']}/", {"company": COMPANY})
        assert resp.status_code == 200
        assert resp.json()["data"]["attempts"] == []

        resp = client.post(
            f"/crm/pc/tasks/{task['uuid']}/attempt/",
            {
                "company": COMPANY,
                "channel": "20",
                "outcome": "10",
                "detail": "微信联系成功，客户表示下周到店",
                "ecode": "1001",
                "nextdate": "2026-09-15",
                "nextecode": "1001",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.content
        assert CrmCaseDetail.objects.filter(caseid_id=task["uuid"]).count() == 1
        assert VipCaseDetail.objects.filter(vipuuid=vip).count() == 1
        db_task = CrmCase.objects.get(uuid=task["uuid"])
        assert db_task.status == "20"

        resp = client.get(f"/crm/pc/tasks/{task['uuid']}/", {"company": COMPANY})
        attempt = resp.json()["data"]["attempts"][0]
        assert attempt["content"] == "微信联系成功，客户表示下周到店"

        resp = client.post(
            f"/crm/pc/tasks/{task['uuid']}/complete/",
            {"company": COMPANY, "outcome": "50", "note": "已预约到店"},
            format="json",
        )
        assert resp.status_code == 200
        db_task.refresh_from_db()
        assert db_task.status == "30"
        assert db_task.finishedate == datetime.date.today()

    def test_complete_without_note_skips_empty_attempt(self, client, vip, empl):
        task = CrmCase.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            vipuuid=vip,
            casetype="10",
            casedesc="快速完成",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
            ecode="1001",
            empl=empl,
        )
        resp = client.post(
            f"/crm/pc/tasks/{task.uuid}/complete/",
            {"company": COMPANY, "outcome": "10"},
            format="json",
        )
        assert resp.status_code == 200
        assert CrmCaseDetail.objects.filter(caseid_id=task.uuid).count() == 0

    def test_pause_and_reassign(self, client, vip, empl):
        task = CrmCase.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            vipuuid=vip,
            casetype="10",
            casedesc="临时任务",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
            ecode="1001",
            empl=empl,
        )
        resp = client.post(
            f"/crm/pc/tasks/{task.uuid}/status/",
            {"company": COMPANY, "status": "40"},
            format="json",
        )
        assert resp.status_code == 200
        task.refresh_from_db()
        assert task.status == "40"

        Empl.objects.create(company=COMPANY, flag="Y", ecode="1003", ename="顾问丙")
        resp = client.post(
            f"/crm/pc/tasks/{task.uuid}/status/",
            {"company": COMPANY, "status": "20", "ecode": "1003"},
            format="json",
        )
        assert resp.status_code == 200
        task.refresh_from_db()
        assert task.status == "20"
        assert task.ecode == "1003"
        assert task.empl.ecode == "1003"


@pytest.mark.django_db
class TestTimeline:
    def test_quick_log_crud(self, client, vip, empl):
        resp = client.post(
            "/crm/pc/timeline/",
            {
                "company": COMPANY,
                "storecode": STORECODE,
                "vipuuid": str(vip.uuid),
                "casetype": "10",
                "detail": "电话关怀，客户状态良好",
                "ecode": "1001",
                "nextdate": "2026-09-01",
            },
            format="json",
        )
        assert resp.status_code == 201, resp.content
        log = resp.json()["data"]
        assert log["vname"] == "张三"

        resp = client.get("/crm/pc/timeline/", {"company": COMPANY, "vipuuid": str(vip.uuid)})
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

        resp = client.put(
            f"/crm/pc/timeline/{log['uuid']}/",
            {"company": COMPANY, "detail": "微信关怀，已约到店"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["detail"] == "微信关怀，已约到店"

        resp = client.delete(f"/crm/pc/timeline/{log['uuid']}/?company={COMPANY}")
        assert resp.status_code == 200
        assert not VipCaseDetail.objects.filter(uuid=log["uuid"], flag="Y").exists()

    def test_timeline_content_falls_back_to_detaildescription(self, client, vip, empl):
        log = VipCaseDetail.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            vipuuid=vip,
            casetype="10",
            detail="",
            detaildescription="微信回访，已约到店",
            ecode="1001",
        )
        resp = client.get("/crm/pc/timeline/", {"company": COMPANY, "vipuuid": str(vip.uuid)})
        assert resp.status_code == 200
        row = resp.json()["data"][0]
        assert row["content"] == "微信回访，已约到店"


@pytest.mark.django_db
class TestCompanyScope:
    def test_task_list_scoped_by_storecode(self, client, vip):
        vip_a = vip
        vip_b = Vip.objects.create(
            company="otherco",
            storecode="99",
            flag="Y",
            vcode="V002",
            vname="李四",
            mtcode="13800000002",
        )
        CrmCase.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            vipuuid=vip_a,
            casetype="10",
            casedesc="A公司任务",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
        )
        CrmCase.objects.create(
            company="otherco",
            storecode="99",
            vipuuid=vip_b,
            casetype="10",
            casedesc="B公司任务",
            planbegindate=datetime.date.today(),
            planfinishdate=datetime.date.today(),
            status="10",
        )
        resp = client.get("/crm/pc/tasks/", {"company": COMPANY, "storecode": STORECODE})
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["casedesc"] == "A公司任务"


@pytest.mark.django_db
class TestTaskSummary:
    def test_summary_counts_and_filters(self, client, vip, empl):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        rule = CrmRule.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            rule_name="生日关怀",
            rule_type="birthday",
            casetype="10",
            enabled="Y",
        )
        CrmCase.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=vip, rule=rule,
            casetype="10", casedesc="今日待办", status="10",
            planbegindate=today, planfinishdate=today, ecode="1001", empl=empl,
        )
        CrmCase.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=vip, rule=rule,
            casetype="10", casedesc="超期", status="10",
            planbegindate=yesterday, planfinishdate=yesterday, ecode="1001", empl=empl,
        )
        CrmCase.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=vip, rule=rule,
            casetype="10", casedesc="已完成", status="30",
            planbegindate=today, planfinishdate=today, ecode="1001", empl=empl,
            finishedate=today,
        )
        CrmCase.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=vip,
            casetype="10", casedesc="手工任务未派单", status="20",
            planbegindate=today, planfinishdate=today, ecode="",
        )

        resp = client.get("/crm/pc/tasks/summary/", {"company": COMPANY, "storecode": STORECODE})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["counts"]["total"] == 4
        assert data["counts"]["today"] == 3
        assert data["counts"]["overdue"] == 1
        assert data["counts"]["in_progress"] == 1
        assert data["counts"]["completed"] == 1
        assert data["counts"]["unassigned"] == 1
        rule_groups = {g["key"]: g["count"] for g in data["groups"]["rule_type"]}
        assert rule_groups.get("birthday") == 3
        assert rule_groups.get("manual") == 1

        resp = client.get("/crm/pc/tasks/", {"company": COMPANY, "storecode": STORECODE, "overdue": "1"})
        assert resp.json()["data"]["total"] == 1
        resp = client.get("/crm/pc/tasks/", {"company": COMPANY, "storecode": STORECODE, "unassigned": "1"})
        assert resp.json()["data"]["total"] == 1
        resp = client.get("/crm/pc/tasks/", {"company": COMPANY, "storecode": STORECODE, "source": "manual"})
        assert resp.json()["data"]["total"] == 1
