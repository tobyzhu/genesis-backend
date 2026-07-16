"""
将 Appoption 中 seg='displayclass1' 的记录复制到
  srvdisplayclass1  (服务专用)
  goodsdisplayclass1 (商品专用)

用法: python3 manage.py copy_displayclass1_options
"""
from django.core.management.base import BaseCommand
from baseinfo.models import Appoption


class Command(BaseCommand):
    help = 'Copy displayclass1 options to srvdisplayclass1 and goodsdisplayclass1'

    def handle(self, *args, **options):
        NEW_SEGS = ['srvdisplayclass1', 'goodsdisplayclass1', 'cardtypedisplayclass1']

        old_records = Appoption.objects.filter(seg='displayclass1', flag='Y')
        total = old_records.count()
        self.stdout.write(f'找到 {total} 条 seg=displayclass1 的记录')

        created = 0
        skipped = 0

        for r in old_records:
            for new_seg in NEW_SEGS:
                _, is_new = Appoption.objects.get_or_create(
                    company=r.company,
                    seg=new_seg,
                    itemname=r.itemname,
                    defaults={
                        'itemvalues': r.itemvalues,
                        'itemvalues2': r.itemvalues2,
                        'itemvalues3': r.itemvalues3,
                        'flag': 'Y',
                    },
                )
                if is_new:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'完成: 新增 {created} 条, 跳过 {skipped} 条（已存在）'
        ))
