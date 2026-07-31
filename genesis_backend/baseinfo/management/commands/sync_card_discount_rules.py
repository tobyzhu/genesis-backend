#coding:utf-8
"""同步服务/商品大类到折扣分类，并把 Cardvsdi 迁移为折扣分类规则。"""
from django.core.management.base import BaseCommand

from baseinfo.card_rules import sync_card_discount_rules


class Command(BaseCommand):
    help = '同步服务/商品大类到折扣分类，并迁移 Cardvsdi 到折扣分类规则'

    def add_arguments(self, parser):
        parser.add_argument('--company', default='', help='只同步指定公司')

    def handle(self, *args, **options):
        company = options['company'] or None
        stats = sync_card_discount_rules(company=company)
        self.stdout.write(self.style.SUCCESS(f"同步完成: {stats}"))
