# coding=utf-8
"""写入客户关怀默认规则（生日关怀、消费次日关怀等）。

用法：
    python manage.py seed_default_crm_rules --company yiren
    python manage.py seed_default_crm_rules --company yiren --storecode 01
    python manage.py seed_default_crm_rules --dry-run
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from crm.default_rules import seed_default_crm_rules


class Command(BaseCommand):
    help = "幂等写入客户关怀默认规则"

    def add_arguments(self, parser):
        parser.add_argument("--company", default="", help="公司编码，缺省时为全公司")
        parser.add_argument("--storecode", default="", help="门店编码，空表示全门店")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        company = (options.get("company") or "").strip()
        dry_run = bool(options.get("dry_run"))
        if company:
            companies = [company]
        else:
            from baseinfo.models import Storeinfo
            companies = sorted(
                set(
                    c for c in Storeinfo.objects.exclude(company__isnull=True)
                    .exclude(company="")
                    .values_list("company", flat=True)
                )
            )
        if not companies:
            raise CommandError("没有可写入的公司")

        for code in companies:
            result = seed_default_crm_rules(
                code,
                options.get("storecode") or "",
                dry_run=dry_run,
            )
            self.stdout.write(
                "%s company=%s created=%d updated=%d skipped=%d" % (
                    "DRY-RUN" if dry_run else "OK",
                    result.get("company"),
                    result.get("created", 0),
                    result.get("updated", 0),
                    result.get("skipped", 0),
                )
            )
