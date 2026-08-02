# coding=utf-8
"""按启用的关怀规则批量生成回访/回馈任务。

用法：
    python manage.py generate_crm_cases --company yiren --storecode 01 --dry-run
    python manage.py generate_crm_cases --company yiren --rule <uuid>
"""

from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand, CommandError

from crm.crm_rules import generate_crm_cases


class Command(BaseCommand):
    help = "按 CrmRule 生成 CrmCase 客户关怀任务"

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True, help="公司编码")
        parser.add_argument("--storecode", default="", help="门店编码，空则按规则门店范围")
        parser.add_argument("--rule", default="", help="指定规则 UUID")
        parser.add_argument("--rule-type", default="", help="指定规则类型")
        parser.add_argument("--date", default="", help="目标日期 YYYY-MM-DD")
        parser.add_argument("--limit", type=int, default=500)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        from crm.models import CrmRule

        rule = None
        rule_uuid = (options.get("rule") or "").strip()
        if rule_uuid:
            try:
                rule = CrmRule.objects.get(uuid=rule_uuid, flag="Y")
            except CrmRule.DoesNotExist:
                raise CommandError("规则不存在: %s" % rule_uuid)

        target_date = None
        raw_date = (options.get("date") or "").strip()
        if raw_date:
            try:
                target_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("date 格式应为 YYYY-MM-DD")

        result = generate_crm_cases(
            company=options["company"],
            storecode=options.get("storecode") or "",
            rule=rule,
            rule_type=options.get("rule_type") or "",
            target_date=target_date,
            dry_run=bool(options["dry_run"]),
            limit=int(options.get("limit") or 500),
        )
        self.stdout.write("created=%d skipped=%d dry_run=%s" % (
            result.get("created", 0),
            result.get("skipped", 0),
            result.get("dry_run"),
        ))
        for err in result.get("errors") or []:
            self.stderr.write(err)
        for row in (result.get("previews") or [])[:10]:
            self.stdout.write("  %s %s -> %s %s" % (
                row.get("planbegindate"),
                row.get("vname"),
                row.get("ecode") or "未派单",
                row.get("casedesc"),
            ))
        if result.get("error"):
            self.stderr.write(result["error"])
