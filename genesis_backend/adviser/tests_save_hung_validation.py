# coding=utf-8
"""save_hung_order 服务端校验与现金分组测试。"""
import json

import pytest

from adviser.models import Cardinfo, ExpvstollHung, ExpenseHung
from baseinfo.models import Cardtype, CardtypeVsDiscountClass, Serviece, Vip


def _make_vip(company, storecode, vcode, vname):
    return Vip.objects.create(
        company=company,
        storecode=storecode,
        flag='Y',
        vcode=vcode,
        vname=vname,
        mtcode='13800000001',
        viplevel='A',
        viptype='10',
        valiflag='Y',
    )


def _make_cardtype(company, code='CT001', comptype='amount', ttype=''):
    return Cardtype.objects.create(
        company=company, cardtype=code, cardname='测试卡',
        comptype=comptype, leftmoney='1000', price='1000',
        ttype=ttype, saleflag='Y', valiflag='Y', flag='Y',
    )


def _make_card(company, storecode, vip, cardtype, ccode='C001',
               leftmoney='1000', leftqty='10'):
    return Cardinfo.objects.create(
        company=company, storecode=storecode, ccode=ccode,
        cardtype=cardtype.cardtype, cardtypeuuid=cardtype,
        vcode=vip.vcode, vipuuid=vip, status='O', flag='Y',
        leftmoney=leftmoney, leftqty=leftqty, s_price='100',
    )


def _make_service(company, code='SV001', price='100',
                  discountclass='10', topcode='100'):
    return Serviece.objects.create(
        company=company, svrcdoe=code, svrname='测试服务' + code,
        price=price, discountclass=discountclass, topcode=topcode,
        saleflag='Y', valiflag='Y', flag='Y',
    )


def _post_save_hung(client, company, storecode, vipuuid, items):
    return client.post(
        '/adviser/save_hung/',
        data=json.dumps({
            'company': company,
            'storecode': storecode,
            'vipuuid': vipuuid,
            'items': items,
        }),
        content_type='application/json',
    )


@pytest.fixture
def vip(db, test_company, test_storecode):
    return _make_vip(test_company, test_storecode, 'V001', '测试会员')


class TestCashGrouping:
    def test_cash_items_stay_separate_from_card_group(
        self, client, db, test_company, test_storecode, vip
    ):
        _make_service(test_company)
        ct = _make_cardtype(test_company)
        # 卡余额不足，旧逻辑会把现金行并入缺口最大的卡组
        _make_card(test_company, test_storecode, vip, ct, ccode='C001', leftmoney='50')

        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'cash', 'card_ccode': '',
            },
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:C001', 'card_ccode': 'C001',
            },
        ])
        assert resp.status_code == 200
        assert resp.json().get('ok') is True

        hungs = list(ExpvstollHung.objects.filter(
            company=test_company, vipuuid=vip
        ).order_by('ccode_hung'))
        # 现金与卡付必须分成两笔挂单，现金行不能被并入卡组
        assert len(hungs) == 2
        ccode_list = sorted(h.ccode_hung or '' for h in hungs)
        assert ccode_list == ['', 'C001']
        assert ExpenseHung.objects.filter(
            company=test_company, hunguuid__in=[h.uuid for h in hungs]
        ).count() == 2


class TestSaveHungValidation:
    def test_rejects_payment_card_of_other_vip(
        self, client, db, test_company, test_storecode, vip
    ):
        _make_service(test_company)
        ct = _make_cardtype(test_company)
        other_vip = _make_vip(test_company, test_storecode, 'V002', '其他会员')
        _make_card(test_company, test_storecode, other_vip, ct, ccode='C099')

        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:C099', 'card_ccode': 'C099',
            },
        ])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('ok') is False
        assert '付款卡' in data.get('message', '')
        assert ExpvstollHung.objects.filter(company=test_company).count() == 0

    def test_rejects_unknown_payment_card(
        self, client, db, test_company, test_storecode, vip
    ):
        _make_service(test_company)
        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:NOPE', 'card_ccode': 'NOPE',
            },
        ])
        data = resp.json()
        assert data.get('ok') is False
        assert '付款卡' in data.get('message', '')

    def test_rejects_item_not_allowed_for_card(
        self, client, db, test_company, test_storecode, vip
    ):
        _make_service(test_company, discountclass='10')
        ct = _make_cardtype(test_company)
        _make_card(test_company, test_storecode, vip, ct, ccode='C001')
        CardtypeVsDiscountClass.objects.create(
            company=test_company, cardtypeuuid=ct, cardtype='CT001',
            ttype='S', discountclass='10', discounttype='DISC',
            disc='0.8', consume_flag='N', flag='Y',
        )

        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:C001', 'card_ccode': 'C001',
            },
        ])
        data = resp.json()
        assert data.get('ok') is False
        assert '禁止使用' in data.get('message', '')
        assert ExpvstollHung.objects.filter(company=test_company).count() == 0

    def test_rejects_times_card_insufficient_qty(
        self, client, db, test_company, test_storecode, vip
    ):
        svc = _make_service(test_company)
        ct = _make_cardtype(test_company, code='SV999', comptype='times')
        ct.ttype = 'S'
        ct.sguuid = svc.uuid
        ct.save()
        _make_card(test_company, test_storecode, vip, ct, ccode='C001', leftqty='1')

        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:C001', 'card_ccode': 'C001',
            },
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'card:C001', 'card_ccode': 'C001',
            },
        ])
        data = resp.json()
        assert data.get('ok') is False
        assert '余次不足' in data.get('message', '')
        assert ExpvstollHung.objects.filter(company=test_company).count() == 0

    def test_rejects_vip_of_other_company(
        self, client, db, test_company, test_storecode
    ):
        other_vip = _make_vip('otherco', test_storecode, 'V099', '异公司会员')
        resp = _post_save_hung(client, test_company, test_storecode, str(other_vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': 100,
                'pay_type': 'cash', 'card_ccode': '',
            },
        ])
        data = resp.json()
        assert data.get('ok') is False
        assert '会员' in data.get('message', '')

    def test_rejects_negative_price(
        self, client, db, test_company, test_storecode, vip
    ):
        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'S', 'srvcode': 'SV001', 's_qty': 1, 's_price': -10,
                'pay_type': 'cash', 'card_ccode': '',
            },
        ])
        data = resp.json()
        assert data.get('ok') is False
        assert '单价不能为负数' in data.get('message', '')


class TestCardSaleValidation:
    def test_times_card_sale_initializes_leftmoney(
        self, client, db, test_company, test_storecode, vip
    ):
        _make_cardtype(test_company, code='CT001', comptype='times')
        resp = _post_save_hung(client, test_company, test_storecode, str(vip.uuid), [
            {
                'ttype': 'C', 'srvcode': 'CT001', 's_qty': 10, 's_price': 800,
                'pay_type': 'cash', 'card_ccode': '',
            },
        ])
        data = resp.json()
        assert data.get('ok') is True
        card = Cardinfo.objects.filter(
            company=test_company, cardtype='CT001', status='P'
        ).first()
        assert card is not None
        assert card.leftqty == 10
        assert card.leftmoney == 8000
