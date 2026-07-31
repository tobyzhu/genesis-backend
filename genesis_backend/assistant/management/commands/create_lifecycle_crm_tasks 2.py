# coding=utf-8
from django.core.management.base import BaseCommand

from assistant.vip_lifecycle_crm import create_lifecycle_crm_tasks


class Command(BaseCommand):
    help = "为生命周期预警/休眠客户生成 CRM 回访任务（VipCaseDetail）。"

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True, help="公司编码")
        parser.add_argument("--storecode", default="", help="门店编码，空则全部门店")
        parser.add_argument(
            "--segment",
            default="at_risk",
            help="at_risk 或 sleeping，默认 at_risk",
        )
        parser.add_argument("--ecode", default="", help="仅指定顾问的客户")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--dry-run", action="store_true", help="仅预览不写库")

    def handle(self, *args, **options):
        company = (options.get("company") or "").strip()
        storecode = (options.get("storecode") or "").strip()
        result = create_lifecycle_crm_tasks(
            company,
            storecode,
            segment=(options.get("segment") or "at_risk").strip(),
            ecode=(options.get("ecode") or "").strip(),
            limit=int(options.get("limit") or 100),
            dry_run=bool(options.get("dry_run")),
        )
        self.stdout.write(self.style.SUCCESS(str(result)))
