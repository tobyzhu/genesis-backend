# coding=utf-8
from django.core.management.base import BaseCommand

from assistant.vip_lifecycle import sync_sleeping_vip_status


class Command(BaseCommand):
    help = "按生命周期规则将休眠客户 vip.status 写为休眠码，并恢复已活跃客户为活跃码。"

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True, help="公司编码，如 yiren")
        parser.add_argument("--storecode", default="", help="门店编码，空则处理全部门店")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅统计将更新的数量，不写库",
        )
        parser.add_argument(
            "--snapshot",
            action="store_true",
            help="同步完成后写入当日生命周期快照",
        )
        parser.add_argument(
            "--crm-tasks",
            action="store_true",
            help="同步完成后为 at_risk/sleeping 生成 CRM 回访任务",
        )
        parser.add_argument(
            "--crm-segments",
            default="at_risk,sleeping",
            help="--crm-tasks 时处理的 segment，逗号分隔，默认 at_risk,sleeping",
        )
        parser.add_argument(
            "--crm-limit",
            type=int,
            default=100,
            help="每个 segment 最多生成任务数",
        )

    def handle(self, *args, **options):
        company = (options.get("company") or "").strip()
        storecode = (options.get("storecode") or "").strip()
        dry_run = bool(options.get("dry_run"))
        do_snapshot = bool(options.get("snapshot"))
        result = sync_sleeping_vip_status(company, storecode, dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS(str(result)))
        if do_snapshot and not dry_run:
            from assistant.vip_lifecycle import save_lifecycle_snapshot

            snap = save_lifecycle_snapshot(company, storecode, dry_run=False)
            self.stdout.write(self.style.SUCCESS("snapshot: " + str(snap)))
        if options.get("crm_tasks") and not dry_run:
            from assistant.vip_lifecycle_crm import create_lifecycle_crm_tasks

            segments = [
                s.strip().lower()
                for s in (options.get("crm_segments") or "at_risk,sleeping").split(",")
                if s.strip()
            ]
            crm_limit = int(options.get("crm_limit") or 100)
            for seg in segments:
                crm = create_lifecycle_crm_tasks(
                    company,
                    storecode,
                    segment=seg,
                    limit=crm_limit,
                    dry_run=False,
                )
                self.stdout.write(self.style.SUCCESS(f"crm_tasks[{seg}]: {crm}"))
