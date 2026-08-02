# coding=utf-8
"""客户关怀默认规则种子数据。"""

from __future__ import annotations

from typing import Any, Dict, List

from crm.models import CrmRule


DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "rule_name": "生日关怀",
        "rule_type": "birthday",
        "casetype": "10",
        "month_offset": 1,
        "days_offset": 0,
        "ttype": "",
        "lifecycle_segment": "",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 本月生日，送上生日祝福与专属到店礼遇",
        "enabled": "Y",
    },
    {
        "rule_name": "消费次日关怀",
        "rule_type": "transaction",
        "casetype": "10",
        "month_offset": 0,
        "days_offset": 1,
        "ttype": "",
        "lifecycle_segment": "",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 昨日到店消费，今日回访体验与满意度",
        "enabled": "Y",
    },
    {
        "rule_name": "到店服务回访",
        "rule_type": "transaction",
        "casetype": "40",
        "month_offset": 0,
        "days_offset": 7,
        "ttype": "S",
        "lifecycle_segment": "",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 服务后 7 天回访",
        "enabled": "Y",
    },
    {
        "rule_name": "购买商品回访",
        "rule_type": "transaction",
        "casetype": "45",
        "month_offset": 0,
        "days_offset": 30,
        "ttype": "G",
        "lifecycle_segment": "",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 商品购买后 30 天回访",
        "enabled": "Y",
    },
    {
        "rule_name": "入会周年关怀",
        "rule_type": "anniversary",
        "casetype": "10",
        "month_offset": 0,
        "days_offset": 0,
        "ttype": "",
        "lifecycle_segment": "",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 入会周年关怀",
        "enabled": "Y",
    },
    {
        "rule_name": "沉睡会员唤醒",
        "rule_type": "lifecycle",
        "casetype": "10",
        "month_offset": 0,
        "days_offset": 0,
        "ttype": "",
        "lifecycle_segment": "sleeping",
        "assignee_policy": "vip_ecode",
        "fixed_ecode": "",
        "casedesc_template": "{vname} 沉睡会员唤醒关怀",
        "enabled": "Y",
    },
]


def seed_default_crm_rules(
    company: str,
    storecode: str = "",
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """幂等写入默认关怀规则，已存在的规则按名称更新。"""
    company = (company or "").strip()
    if not company:
        return {"error": "缺少 company", "created": 0, "updated": 0, "skipped": 0}
    storecode = (storecode or "").strip()
    created = 0
    updated = 0
    skipped = 0
    for item in DEFAULT_RULES:
        rule, was_created = CrmRule.objects.get_or_create(
            company=company,
            storecode=storecode,
            rule_name=item["rule_name"],
            defaults={**item, "flag": "Y", "creater": "seed_rules"},
        )
        if was_created:
            created += 1
        else:
            if dry_run:
                skipped += 1
                continue
            for key, value in item.items():
                setattr(rule, key, value)
            rule.flag = "Y"
            rule.save()
            updated += 1
    return {
        "company": company,
        "storecode": storecode or "*",
        "dry_run": dry_run,
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }
