# coding=utf-8
"""默认关怀规则种子 + 全交易类型生成测试。"""
from __future__ import annotations

import datetime

import pytest

from baseinfo.models import Vip
from cashier.models import Expvstoll
from crm.crm_rules import generate_crm_cases
from crm.default_rules import DEFAULT_RULES, seed_default_crm_rules
from crm.models import CrmRule

COMPANY = "testco"
STORECODE = "99"


@pytest.mark.django_db
class TestDefaultRules:
    def test_seed_is_idempotent(self):
        first = seed_default_crm_rules(COMPANY, STORECODE)
        assert first["created"] == len(DEFAULT_RULES)

        second = seed_default_crm_rules(COMPANY, STORECODE)
        assert second["created"] == 0
        assert second["updated"] == len(DEFAULT_RULES)
        assert CrmRule.objects.filter(company=COMPANY, storecode=STORECODE).count() == len(DEFAULT_RULES)

    def test_default_rules_cover_birthday_and_next_day(self):
        seed_default_crm_rules(COMPANY, STORECODE)
        names = set(CrmRule.objects.filter(company=COMPANY).values_list("rule_name", flat=True))
        assert "生日关怀" in names
        assert "消费次日关怀" in names
        next_day = CrmRule.objects.get(company=COMPANY, rule_name="消费次日关怀")
        assert next_day.rule_type == "transaction"
        assert next_day.days_offset == 1


@pytest.mark.django_db
class TestTransactionAllTypes:
    def test_empty_ttype_covers_all_transactions(self):
        vip = Vip.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            flag="Y",
            vcode="V001",
            vname="张三",
            mtcode="13800000001",
            birth="0901",
        )
        rule = CrmRule.objects.create(
            company=COMPANY,
            storecode=STORECODE,
            rule_name="消费次日关怀",
            rule_type="transaction",
            casetype="10",
            days_offset=1,
            ttype="",
            assignee_policy="vip_ecode",
            enabled="Y",
        )
        for ttype, days_ago in (("S", 1), ("I", 2)):
            Expvstoll.objects.create(
                company=COMPANY,
                storecode=STORECODE,
                flag="Y",
                valiflag="Y",
                ttype=ttype,
                vipuuid=vip,
                vsdate=(datetime.date.today() - datetime.timedelta(days=days_ago)).strftime("%Y%m%d"),
            )
        result = generate_crm_cases(COMPANY, STORECODE, rule=rule, dry_run=False)
        assert result["created"] == 2
        assert result["skipped"] == 0
