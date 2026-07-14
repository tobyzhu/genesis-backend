# coding=utf-8
from django.core.management.base import BaseCommand

from assistant.vip_lifecycle import save_lifecycle_snapshot


class Command(BaseCommand):
    help = "保存客户生命周期快照（用于观察分级迁移）。"

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True, help="公司编码，如 yiren")
        parser.add_argument("--storecode", default="", help="门店编码，空则全部门店")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅统计将写入的数量，不写库",
        )

    def handle(self, *args, **options):
        company = (options.get("company") or "").strip()
        storecode = (options.get("storecode") or "").strip()
        dry_run = bool(options.get("dry_run"))
        result = save_lifecycle_snapshot(company, storecode, dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS(str(result)))
