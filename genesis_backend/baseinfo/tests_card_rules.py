#coding:utf-8
"""卡类规则核心测试：Ruler 解析、定价/权限、同步命令、API。"""
import json
from decimal import Decimal

import pytest

from adviser.models import Cardinfo
from baseinfo.models import (
    Appoption, Cardtype, CardtypeVsDiscountClass, Cardvsdi,
    Goods, Goodsct, Ruler, Serviece, Srvtopty,
)
from baseinfo.card_rules import (
    card_use_for_month, parse_ruler, resolve_card_item_price,
    ruler_lookup, sync_card_discount_rules,
)


@pytest.fixture
def test_company():
    return 'testco'


def _make_cardtype(company, code='CT001', comptype='amount', ruler=None,
                   ttype='', sguuid=None, price='1000'):
    return Cardtype.objects.create(
        company=company, cardtype=code, cardname='测试卡',
        comptype=comptype, leftmoney=price, price=price,
        ruler=ruler, ttype=ttype, sguuid=sguuid,
        saleflag='Y', valiflag='Y', flag='Y',
    )


def _make_cardinfo(company, cardtype, ccode='C001', valdate='20991231',
                   leftmoney='1000'):
    return Cardinfo.objects.create(
        company=company, ccode=ccode, cardtype=cardtype.cardtype,
        cardtypeuuid=cardtype, leftmoney=leftmoney, status='Y',
        valdate=valdate, flag='Y',
    )


class TestParseRuler:
    def test_parse_ruler_example(self):
        parsed = parse_ruler(
            '#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#'
        )
        assert parsed['ttype'] == 'S'
        assert parsed['itemcode'] == '105001'
        assert parsed['tiers'] == [(1, Decimal('1260')), (2, Decimal('960'))]
        assert parsed['others'] == Decimal('720')

    def test_parse_ruler_goods(self):
        parsed = parse_ruler('#ttype=G#gcode=G001#1sttimes=100#others=80#')
        assert parsed['ttype'] == 'G'
        assert parsed['itemcode'] == 'G001'
        assert parsed['tiers'] == [(1, Decimal('100'))]
        assert parsed['others'] == Decimal('80')

    def test_parse_ruler_missing_others(self):
        parsed = parse_ruler('#ttype=S#srvcode=100#1sttimes=10#2ndtimes=8#')
        assert parsed['others'] is None
        assert ruler_lookup(parsed, 2) == Decimal('8')

    def test_parse_ruler_invalid(self):
        assert parse_ruler('') == {}
        assert parse_ruler('garbage') == {}
        assert parse_ruler('#ttype=#srvcode=100#') == {}

    def test_ruler_lookup_tiers(self):
        parsed = parse_ruler(
            '#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#'
        )
        assert ruler_lookup(parsed, 0) == Decimal('1260')
        assert ruler_lookup(parsed, 1) == Decimal('960')
        assert ruler_lookup(parsed, 2) == Decimal('720')
        assert ruler_lookup(parsed, 9) == Decimal('720')


class TestLogicCardPricing:
    def test_logic_card_uses_natural_month_tiers(self, db, test_company):
        ruler = Ruler.objects.create(
            rulername='拓客卡',
            ruler='#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#',
        )
        ct = _make_cardtype(test_company, comptype='amount', ruler=ruler, ttype='S')
        ci = _make_cardinfo(test_company, ct)
        ci.logic_cycle_month = '2026-07'
        ci.logic_usecount = 0
        ci.save()

        first = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('2000'),
            now_month='2026-07',
        )
        assert first['allowed'] is True
        assert first['price'] == Decimal('1260')
        assert first['source'] == 'ruler'

        ci.logic_usecount = 1
        ci.save()
        second = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('2000'),
            now_month='2026-07',
        )
        assert second['price'] == Decimal('960')

        ci.logic_usecount = 2
        ci.save()
        third = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('2000'),
            now_month='2026-07',
        )
        assert third['price'] == Decimal('720')

    def test_logic_card_month_switch_resets(self, db, test_company):
        ruler = Ruler.objects.create(
            rulername='拓客卡',
            ruler='#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#',
        )
        ct = _make_cardtype(test_company, comptype='amount', ruler=ruler, ttype='S')
        ci = _make_cardinfo(test_company, ct)
        ci.logic_cycle_month = '2026-07'
        ci.logic_usecount = 2
        ci.save()

        res = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('2000'),
            now_month='2026-08',
        )
        assert res['price'] == Decimal('1260')
        assert card_use_for_month(ci, '2026-08') == 0

    def test_logic_card_item_mismatch_blocked(self, db, test_company):
        ruler = Ruler.objects.create(
            rulername='拓客卡',
            ruler='#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#',
        )
        ct = _make_cardtype(test_company, comptype='amount', ruler=ruler, ttype='S')
        ci = _make_cardinfo(test_company, ct)
        res = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='999999',
            discountclass='', topcode='', original_price=Decimal('2000'),
            now_month='2026-07',
        )
        assert res['allowed'] is False
        assert '绑定' in res['reason']


class TestAmountCardPricing:
    def test_discountclass_rule(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        CardtypeVsDiscountClass.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', discountclass='10', discounttype='DISC',
            disc=Decimal('0.8'), consume_flag='Y',
        )
        res = resolve_card_item_price(
            test_company, ct, None, ttype='S', itemcode='SV001',
            discountclass='10', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is True
        assert res['price'] == Decimal('800')
        assert res['source'] == 'discountclass'

    def test_discountclass_fixed_price(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        CardtypeVsDiscountClass.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='G', discountclass='01', discounttype='PRICE',
            price=Decimal('500'), consume_flag='Y',
        )
        res = resolve_card_item_price(
            test_company, ct, None, ttype='G', itemcode='G001',
            discountclass='01', topcode='', original_price=Decimal('1000'),
        )
        assert res['price'] == Decimal('500')

    def test_discountclass_rule_blocks_consumption(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        CardtypeVsDiscountClass.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', discountclass='10', discounttype='DISC',
            disc=Decimal('0.8'), consume_flag='N',
        )
        res = resolve_card_item_price(
            test_company, ct, None, ttype='S', itemcode='SV001',
            discountclass='10', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is False
        assert '禁止' in res['reason']

    def test_fallback_to_service_category(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        Cardvsdi.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', topcode='100', pricetype='DISCOUNT',
            cardvsdisc=Decimal('0.9'), consume_flag='Y', flag='Y',
        )
        res = resolve_card_item_price(
            test_company, ct, None, ttype='S', itemcode='SV001',
            discountclass='', topcode='100', original_price=Decimal('1000'),
        )
        assert res['allowed'] is True
        assert res['price'] == Decimal('900')
        assert res['source'] == 'cardvsdi'

    def test_service_category_blocks_consumption(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        Cardvsdi.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', topcode='100', pricetype='DISCOUNT',
            cardvsdisc=Decimal('0.9'), consume_flag='N', flag='Y',
        )
        res = resolve_card_item_price(
            test_company, ct, None, ttype='S', itemcode='SV001',
            discountclass='', topcode='100', original_price=Decimal('1000'),
        )
        assert res['allowed'] is False

    def test_no_rule_uses_original_price(self, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        res = resolve_card_item_price(
            test_company, ct, None, ttype='S', itemcode='SV001',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is True
        assert res['price'] == Decimal('1000')
        assert res['source'] == 'original'


class TestPeriodAndTimesCard:
    def test_period_card_valid_and_bound(self, db, test_company):
        ct = _make_cardtype(test_company, code='105001', comptype='period', ttype='S')
        ci = _make_cardinfo(test_company, ct, valdate='20991231')
        res = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is True
        assert res['price'] == Decimal('1000')
        assert res['source'] == 'period'

    def test_period_card_item_mismatch_blocked(self, db, test_company):
        ct = _make_cardtype(test_company, code='105001', comptype='period', ttype='S')
        ci = _make_cardinfo(test_company, ct, valdate='20991231')
        res = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='999999',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is False

    def test_period_card_expired_blocked(self, db, test_company):
        ct = _make_cardtype(test_company, code='105001', comptype='period', ttype='S')
        ci = _make_cardinfo(test_company, ct, valdate='20200101')
        res = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert res['allowed'] is False
        assert '过期' in res['reason']

    def test_times_card_binding_check(self, db, test_company):
        ct = _make_cardtype(test_company, code='105001', comptype='times', ttype='S')
        ci = _make_cardinfo(test_company, ct)
        ok = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='105001',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert ok['allowed'] is True
        bad = resolve_card_item_price(
            test_company, ct, ci, ttype='S', itemcode='999999',
            discountclass='', topcode='', original_price=Decimal('1000'),
        )
        assert bad['allowed'] is False


class TestSyncRules:
    def test_sync_creates_dictionary_rules_and_backfill(self, db, test_company):
        Srvtopty.objects.create(
            company=test_company, topcode='100', ttname='面部', flag='Y')
        Goodsct.objects.create(
            company=test_company, goodsct='01', goodsctname='护肤品', flag='Y')
        sv = Serviece.objects.create(
            company=test_company, svrcdoe='SV001', svrname='清洁',
            topcode='100', saleflag='Y', valiflag='Y')
        gd = Goods.objects.create(
            company=test_company, gcode='G001', gname='精华',
            goodsct='01', saleflag='Y', valiflag='Y')
        ct = _make_cardtype(test_company)
        Cardvsdi.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', topcode='100', pricetype='DISCOUNT',
            cardvsdisc=Decimal('0.9'), flag='Y')
        Cardvsdi.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='G', topcode='01', pricetype='PRICE',
            cardvsprice=Decimal('500'), flag='N', consume_flag=None)

        result = sync_card_discount_rules(company=test_company)

        assert result['srv_categories'] == 1
        assert result['goods_categories'] == 1
        assert result['items_backfilled'] == 2
        assert result['rules_created'] == 2
        assert Appoption.objects.filter(
            company=test_company, seg='srvdiscountclass',
            itemname='100', itemvalues='面部').exists()
        assert Appoption.objects.filter(
            company=test_company, seg='goodsdiscountclass',
            itemname='01', itemvalues='护肤品').exists()

        sv.refresh_from_db()
        gd.refresh_from_db()
        assert sv.discountclass == '100'
        assert gd.discountclass == '01'

        rule_s = CardtypeVsDiscountClass.objects.get(
            company=test_company, cardtype='CT001', ttype='S',
            discountclass='100')
        assert rule_s.discounttype == 'DISC'
        assert rule_s.disc == Decimal('0.9')
        assert rule_s.consume_flag == 'Y'

        rule_g = CardtypeVsDiscountClass.objects.get(
            company=test_company, cardtype='CT001', ttype='G',
            discountclass='01')
        assert rule_g.discounttype == 'PRICE'
        assert rule_g.price == Decimal('500')
        assert rule_g.consume_flag == 'N'

    def test_sync_is_idempotent(self, db, test_company):
        Srvtopty.objects.create(
            company=test_company, topcode='100', ttname='面部', flag='Y')
        ct = _make_cardtype(test_company)
        Cardvsdi.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', topcode='100', pricetype='DISCOUNT',
            cardvsdisc=Decimal('0.9'), flag='Y')

        sync_card_discount_rules(company=test_company)
        sync_card_discount_rules(company=test_company)

        assert CardtypeVsDiscountClass.objects.filter(
            company=test_company, cardtype='CT001',
            ttype='S', discountclass='100').count() == 1
        assert Appoption.objects.filter(
            company=test_company, seg='srvdiscountclass',
            itemname='100').count() == 1


class TestCardPricingApi:
    def test_card_pricing_api(self, client, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        CardtypeVsDiscountClass.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', discountclass='10', discounttype='DISC',
            disc=Decimal('0.8'), consume_flag='Y')
        resp = client.post(
            '/adviser/card-pricing/',
            data=json.dumps({
                'cardtypeuuid': str(ct.uuid),
                'company': test_company,
                'items': [{
                    'ttype': 'S', 'code': 'SV001',
                    'discountclass': '10', 'topcode': '',
                    'price': 1000, 'qty': 1,
                }],
            }),
            content_type='application/json',
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data['results'][0]['allowed'] is True
        assert data['results'][0]['price'] == 800

    def test_ruler_save_api_validates_rule(self, client, db, test_company):
        resp = client.post(
            '/adviser/ruler-save/',
            data=json.dumps({
                'rulername': '新规则',
                'ruler': '#ttype=S#srvcode=100#1sttimes=10#others=8#',
            }),
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert Ruler.objects.filter(rulername='新规则').exists()

    def test_ruler_save_api_rejects_bad_rule(self, client, db, test_company):
        resp = client.post(
            '/adviser/ruler-save/',
            data=json.dumps({'rulername': '坏规则', 'ruler': 'not-a-rule'}),
            content_type='application/json',
        )
        assert resp.status_code == 400
        assert not Ruler.objects.filter(rulername='坏规则').exists()

    def test_cardtype_discount_save_api(self, client, db, test_company):
        ct = _make_cardtype(test_company, comptype='amount')
        resp = client.post(
            '/adviser/cardtype-discount-save/',
            data=json.dumps({
                'company': test_company,
                'cardtype': 'CT001',
                'rules': [{
                    'ttype': 'S', 'discountclass': '10',
                    'discounttype': 'DISC', 'disc': 0.8,
                    'price': 0, 'consume_flag': 'Y',
                }],
            }),
            content_type='application/json',
        )
        assert resp.status_code == 200
        rule = CardtypeVsDiscountClass.objects.get(
            company=test_company, cardtype='CT001',
            ttype='S', discountclass='10')
        assert rule.disc == Decimal('0.8')
