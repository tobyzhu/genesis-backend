# coding=utf-8
import csv
import logging

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str

from common.admin_utils import get_admin_company, get_admin_storecodes
from report.models import CardBalanceReportQuery
from report.card_balance_report import (
    COMPTYPE_LABELS,
    build_card_balance_report,
    get_company_choices,
    get_store_choices,
    get_suptype_choices,
)

logger = logging.getLogger(__name__)


@admin.register(CardBalanceReportQuery)
class CardBalanceReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/report/card_balance_report.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def get_queryset(self, request):
        return CardBalanceReportQuery.objects.none()

    def _resolve_company(self, request):
        profile_company = get_admin_company(request)
        if request.user.is_superuser:
            picked = (request.GET.get('company') or '').strip()
            if picked:
                return picked
        return profile_company

    def changelist_view(self, request, extra_context=None):
        company = self._resolve_company(request)
        allowed_stores = get_admin_storecodes(request) or None

        params = {
            'storecode': (request.GET.get('storecode') or '').strip(),
            'suptype': (request.GET.get('suptype') or '').strip(),
            'comptype': (request.GET.get('comptype') or '').strip(),
            'nature': (request.GET.get('nature') or '').strip(),
            'keyword': (request.GET.get('keyword') or '').strip(),
            'only_with_balance': request.GET.get('only_with_balance', '1') != '0',
        }

        has_filters = request.GET.get('q') == '1'

        if request.GET.get('export') == 'csv':
            return self._export_csv(request, company, params)

        report = None
        report_error = ''

        if has_filters:
            try:
                report = build_card_balance_report(company=company, **params)
                report_error = report.get('error') or ''
            except Exception as exc:
                logger.exception('card_balance admin view error')
                report_error = str(exc)
                report = {
                    'summary_rows': [],
                    'grand_totals': {
                        'card_count': 0,
                        'normal_amount': 0,
                        'gift_amount': 0,
                        'normal_times': 0,
                        'gift_times': 0,
                    },
                }

        context = {
            **self.admin_site.each_context(request),
            'title': '卡余额汇总',
            'opts': CardBalanceReportQuery._meta,
            'company': company,
            'profile_company': get_admin_company(request),
            'params': params,
            'store_choices': get_store_choices(company, allowed_stores),
            'suptype_choices': get_suptype_choices(company),
            'company_choices': get_company_choices() if request.user.is_superuser else [],
            'comptype_choices': list(COMPTYPE_LABELS.items()),
            'nature_choices': [('正常', '正常'), ('赠送', '赠送')],
            'report': report,
            'report_error': report_error,
            'has_filters': has_filters,
        }
        if extra_context:
            context.update(extra_context)
        return render(request, self.change_list_template, context)

    def _export_csv(self, request, company, params):
        report = build_card_balance_report(company=company, **params)
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="card_balance_by_cardtype.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                '序号',
                '卡类编号',
                '卡类名称',
                '卡大类',
                '消费模式',
                '品牌',
                '正常张数',
                '正常余额',
                '正常余次',
                '赠送张数',
                '赠送余额',
                '赠送余次',
                '合计张数',
                '合计余额',
                '合计余次',
            ]
        )
        for idx, row in enumerate(report['summary_rows'], start=1):
            is_times = row['comptype'] == 'times'
            writer.writerow(
                [
                    str(idx),
                    row['cardtype_code'],
                    row['cardtype_name'],
                    row['suptype_name'],
                    row['comptype_label'],
                    row['brand'],
                    row['normal_count'],
                    force_str(row['normal_leftmoney']),
                    force_str(row['normal_leftqty']) if is_times else '',
                    row['gift_count'],
                    force_str(row['gift_leftmoney']),
                    force_str(row['gift_leftqty']) if is_times else '',
                    row['total_count'],
                    force_str(row['total_leftmoney']),
                    force_str(row['total_leftqty']) if is_times else '',
                ]
            )
        return response
