# coding=utf-8
"""
Admin 卡余额汇总：按卡类 + stype(N=正常/P=赠送) 汇总。
余额取自 Cardinfo.leftmoney；疗程剩余次数取自 Cardinfo.leftqty。
"""
from __future__ import unicode_literals

import logging
import time
from collections import OrderedDict
from decimal import Decimal

from django.db.models import (
    Case,
    CharField,
    OuterRef,
    Subquery,
    Count,
    DecimalField,
    F,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce

import common.constants
from adviser.models import Cardinfo
from baseinfo.models import Cardsupertype, Storeinfo, Appoption
from baseinfo.models import Cardtype

logger = logging.getLogger(__name__)

COMPTYPE_LABELS = {
    'amount': '储值（计费）',
    'times': '疗程（计次）',
    'period': '计时',
}


def _decimal(value):
    if value is None:
        return Decimal('0')
    return Decimal(str(value))


def get_store_choices(company, allowed_storecodes=None):
    qs = Storeinfo.objects.filter(company=company, flag='Y').order_by('storecode')
    if allowed_storecodes:
        qs = qs.filter(storecode__in=allowed_storecodes)
    return [
        (s.storecode, (s.storename or s.storecode or '').strip())
        for s in qs
    ]


def get_suptype_choices(company):
    return list(
        Cardsupertype.objects.filter(company=company, flag='Y')
        .order_by('code')
        .values_list('code', 'name')
    )


def get_company_choices():
    return list(
        Cardinfo.objects.filter(flag='Y')
        .values_list('company', flat=True)
        .distinct()
        .order_by('company')
    )


def _suptype_name_map(company):
    names = dict(get_suptype_choices(company))
    for code, name in list(common.constants.CARDSUPTYPE):
        names.setdefault(code, name)
    return names


def _brand_name_map(company):
    return dict(
        Appoption.objects.filter(company=company, flag='Y', seg='brand').values_list(
            'itemname', 'itemvalues'
        )
    )


def _resolve_brand_display(comptype, brand_code, brand_names):
    """疗程/计次卡显示 Cardtype.brand；储值卡留空。"""
    if (comptype or '').strip() != 'times':
        return ''
    code = (brand_code or '').strip()
    if not code:
        return ''
    return (brand_names.get(code) or code).strip()


def build_card_balance_queryset(
    company,
    storecode='',
    storecodes=None,
    suptype='',
    comptype='',
    nature='',
    keyword='',
    only_with_balance=True,
):
    """
    stype: N=正常购买, P=赠送。
    有效卡：flag='Y' 且 status='O'。
    余额：Cardinfo.leftmoney；余次：Cardinfo.leftqty（疗程/计次卡）。
    storecodes: 多店列表；优先于单个 storecode。
    """
    qs = Cardinfo.objects.filter(
        company=company, flag='Y', status='O'
    ).select_related('cardtypeuuid')

    qs = qs.annotate(
        _cardtype_subq=Subquery(
            Cardtype.objects.filter(
                company=OuterRef('company'), cardtype=OuterRef('cardtype'), flag='Y'
            ).values('suptype')[:1],
            output_field=CharField(),
        ),
        eff_suptype=Coalesce(F('cardtypeuuid__suptype'), F('_cardtype_subq'), F('suptype'), Value('')),
        eff_comptype=Coalesce(
            F('cardtypeuuid__comptype'),
            Subquery(
                Cardtype.objects.filter(
                    company=OuterRef('company'), cardtype=OuterRef('cardtype'), flag='Y'
                ).values('comptype')[:1],
                output_field=CharField(),
            ),
            Value('amount'),
        ),
        eff_cardtype_code=Coalesce(
            F('cardtypeuuid__cardtype'),
            Subquery(
                Cardtype.objects.filter(
                    company=OuterRef('company'), cardtype=OuterRef('cardtype'), flag='Y'
                ).values('cardtype')[:1],
                output_field=CharField(),
            ),
            F('cardtype'),
            Value(''),
        ),
        eff_cardtype_name=Coalesce(
            F('cardtypeuuid__cardname'),
            Subquery(
                Cardtype.objects.filter(
                    company=OuterRef('company'), cardtype=OuterRef('cardtype'), flag='Y'
                ).values('cardname')[:1],
                output_field=CharField(),
            ),
            F('cardtype'),
            Value(''),
        ),
        eff_brand=Coalesce(
            F('cardtypeuuid__brand'),
            Subquery(
                Cardtype.objects.filter(
                    company=OuterRef('company'), cardtype=OuterRef('cardtype'), flag='Y'
                ).values('brand')[:1],
                output_field=CharField(),
            ),
            Value(''),
        ),
        nature=Case(
            When(stype='P', then=Value('赠送')),
            default=Value('正常'),
            output_field=CharField(),
        ),
    )

    codes = [str(c).strip() for c in (storecodes or []) if str(c).strip()]
    if codes:
        qs = qs.filter(storecode__in=codes)
    elif storecode:
        qs = qs.filter(storecode=storecode)
    if suptype:
        qs = qs.filter(eff_suptype=suptype)
    if comptype:
        qs = qs.filter(eff_comptype=comptype)
    if nature == '正常':
        qs = qs.exclude(stype='P')
    elif nature == '赠送':
        qs = qs.filter(stype='P')
    if keyword:
        kw = keyword.strip()
        qs = qs.filter(
            Q(ccode__icontains=kw)
            | Q(vcode__icontains=kw)
            | Q(cardtype__icontains=kw)
            | Q(cardtypeuuid__cardname__icontains=kw)
        )

    if only_with_balance:
        qs = qs.filter(Q(leftmoney__gt=0) | Q(leftqty__gt=0))

    return qs


def collect_diagnostics(company, params, qs, elapsed_ms, error=None):
    base = Cardinfo.objects.filter(company=company)
    active = base.filter(flag='Y', status='O')
    diag = {
        'elapsed_ms': round(elapsed_ms, 1),
        'company': company,
        'params': dict(params),
        'error': error or '',
        'counts': {},
    }
    try:
        diag['counts'] = {
            'company_all_cards': base.count(),
            'company_active_op': active.count(),
            'stype_N_normal': active.filter(stype='N').count(),
            'stype_P_gift': active.filter(stype='P').count(),
            'matched_after_all_filters': qs.count(),
        }
        diag['stype_distribution'] = list(
            active.values('stype').annotate(n=Count('uuid')).order_by('-n')[:6]
        )
    except Exception as exc:
        diag['counts_error'] = str(exc)
    return diag


def build_card_balance_report(
    company,
    storecode='',
    storecodes=None,
    suptype='',
    comptype='',
    nature='',
    keyword='',
    only_with_balance=True,
):
    """返回卡类级 summary_rows、grand_totals、diagnostics。"""
    t0 = time.time()
    suptype_names = _suptype_name_map(company)
    brand_names = _brand_name_map(company)
    codes = [str(c).strip() for c in (storecodes or []) if str(c).strip()]

    try:
        qs = build_card_balance_queryset(
            company=company,
            storecode=storecode,
            storecodes=codes or None,
            suptype=suptype,
            comptype=comptype,
            nature=nature,
            keyword=keyword,
            only_with_balance=only_with_balance,
        )

        summary_agg = (
            qs.values(
                'eff_suptype',
                'eff_cardtype_code',
                'eff_cardtype_name',
                'eff_comptype',
                'eff_brand',
                'nature',
            )
            .annotate(
                card_count=Count(
                    'uuid',
                    filter=(
                        Q(eff_comptype='times', leftqty__gt=0)
                        | ~Q(eff_comptype='times') & Q(leftmoney__gt=0)
                    ),
                ),
                total_leftmoney=Coalesce(
                    Sum('leftmoney'),
                    Value(Decimal('0')),
                    output_field=DecimalField(max_digits=16, decimal_places=2),
                ),
                total_leftqty=Coalesce(
                    Sum('leftqty'),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .order_by('eff_comptype', 'eff_suptype', 'eff_cardtype_code', 'nature')
        )

        grand = {
            'card_count': 0,
            'normal_amount': Decimal('0'),
            'gift_amount': Decimal('0'),
            'normal_times': Decimal('0'),
            'gift_times': Decimal('0'),
        }

        pivot = OrderedDict()
        for row in summary_agg:
            st_code = (row['eff_suptype'] or '').strip()
            cp = (row['eff_comptype'] or 'amount').strip() or 'amount'
            card_key = (st_code, row['eff_cardtype_code'] or '', cp)
            if card_key not in pivot:
                pivot[card_key] = {
                    'suptype_code': st_code,
                    'suptype_name': suptype_names.get(st_code, st_code or '—'),
                    'cardtype_code': row['eff_cardtype_code'] or '',
                    'cardtype_name': row['eff_cardtype_name'] or '',
                    'comptype': cp,
                    'comptype_label': COMPTYPE_LABELS.get(cp, cp),
                    'brand': _resolve_brand_display(
                        cp, row.get('eff_brand'), brand_names
                    ),
                    'normal_count': 0,
                    'normal_leftmoney': Decimal('0'),
                    'normal_leftqty': Decimal('0'),
                    'gift_count': 0,
                    'gift_leftmoney': Decimal('0'),
                    'gift_leftqty': Decimal('0'),
                }
            item = pivot[card_key]
            cnt = row['card_count']
            money = _decimal(row['total_leftmoney'])
            qty = _decimal(row['total_leftqty'])
            if row['nature'] == '赠送':
                item['gift_count'] += cnt
                item['gift_leftmoney'] += money
                item['gift_leftqty'] += qty
                grand['gift_amount'] += money
                if cp == 'times':
                    grand['gift_times'] += qty
            else:
                item['normal_count'] += cnt
                item['normal_leftmoney'] += money
                item['normal_leftqty'] += qty
                grand['normal_amount'] += money
                if cp == 'times':
                    grand['normal_times'] += qty
            grand['card_count'] += cnt

        summary_rows = []
        for item in pivot.values():
            item['total_count'] = item['normal_count'] + item['gift_count']
            item['total_leftmoney'] = item['normal_leftmoney'] + item['gift_leftmoney']
            item['total_leftqty'] = item['normal_leftqty'] + item['gift_leftqty']
            summary_rows.append(item)

        summary_rows.sort(
            key=lambda r: (r['comptype'], r['suptype_code'], r['cardtype_code'])
        )

        grand['total_amount'] = grand['normal_amount'] + grand['gift_amount']
        grand['total_times'] = grand['normal_times'] + grand['gift_times']

        elapsed = (time.time() - t0) * 1000
        diagnostics = collect_diagnostics(
            company,
            {
                'storecode': storecode,
                'storecodes': codes,
                'suptype': suptype,
                'comptype': comptype,
                'nature': nature,
                'keyword': keyword,
                'only_with_balance': only_with_balance,
            },
            qs,
            elapsed,
        )

        logger.info(
            'card_balance_report company=%s rows=%s matched=%s ms=%.1f',
            company,
            len(summary_rows),
            diagnostics['counts'].get('matched_after_all_filters'),
            elapsed,
        )

        return {
            'summary_rows': summary_rows,
            'grand_totals': grand,
            'diagnostics': diagnostics,
        }
    except Exception as exc:
        elapsed = (time.time() - t0) * 1000
        logger.exception('card_balance_report failed company=%s', company)
        return {
            'summary_rows': [],
            'grand_totals': {
                'card_count': 0,
                'normal_amount': Decimal('0'),
                'gift_amount': Decimal('0'),
                'normal_times': Decimal('0'),
                'gift_times': Decimal('0'),
                'total_amount': Decimal('0'),
                'total_times': Decimal('0'),
            },
            'diagnostics': collect_diagnostics(
                company,
                {
                    'storecode': storecode,
                    'storecodes': codes,
                    'suptype': suptype,
                    'comptype': comptype,
                    'nature': nature,
                    'keyword': keyword,
                    'only_with_balance': only_with_balance,
                },
                Cardinfo.objects.none(),
                elapsed,
                error=str(exc),
            ),
            'error': str(exc),
        }
