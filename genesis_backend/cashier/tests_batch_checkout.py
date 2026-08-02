# coding=utf-8
"""batch_checkout 结账前卡付权限校验测试。"""
import json

import pytest

from adviser.models import Cardinfo, ExpvstollHung, ExpenseHung
from baseinfo.models import Cardtype, CardtypeVsDiscountClass, Serviece, Vip


@pytest.fixture
def checkout_data(db, test_company, test_storecode):
    vip = Vip.objects.create(
        company=test_company, storecode=test_storecode, flag='Y',
        vcode='V001', vname='测试会员', mtcode='13800000001',
        viplevel='A', viptype='10', valiflag='Y',
    )
    Serviece.objects.create(
        company=test_company, svrcdoe='SV001', svrname='清洁服务',
        price='100', discountclass='10', topcode='100',
        saleflag='Y', valiflag='Y', flag='Y',
    )
    ct = Cardtype.objects.create(
        company=test_company, cardtype='CT001', cardname='测试卡',
        comptype='amount', leftmoney='1000', price='1000',
        saleflag='Y', valiflag='Y', flag='Y',
    )
    CardtypeVsDiscountClass.objects.create(
        company=test_company, cardtypeuuid=ct, cardtype='CT001',
        ttype='S', discountclass='10', discounttype='DISC',
        disc='0.8', consume_flag='N', flag='Y',
    )
    Cardinfo.objects.create(
        company=test_company, storecode=test_storecode, ccode='C001',
        cardtype='CT001', cardtypeuuid=ct, vcode=vip.vcode, vipuuid=vip,
        status='O', flag='Y', leftmoney='1000',
    )
    hung = ExpvstollHung.objects.create(
        company=test_company, storecode=test_storecode,
        vipuuid=vip, vcode_hung=vip.vcode, vipcode=vip.vcode,
        exptxserno_hung='HS01', vsdate_hung='20260801',
        vstime_hung='120000', totmount_hung='100',
        psstatus_hung='10', ttype_hung='S', valiflag_hung='Y', flag='Y',
        ccode_hung='C001', cardtype_hung='CT001',
    )
    ExpenseHung.objects.create(
        company=test_company, storecode=test_storecode,
        hunguuid=hung, exptxserno_hung='HS01', ditem_hung='0001',
        ttype_hung='S', stype_hung='N', srvcode_hung='SV001',
        s_qty_hung=1, s_price_hung='100', s_mount_hung='100',
        srvactmount_hung='100', addvamoney_hung='100',
        secdisc_hung=1, srvmondisc_hung=0,
        otherserno_hung='C001', flag='Y',
    )
    return {'hung': hung}


class TestBatchCheckoutPermission:
    def test_rejects_disallowed_card_item(
        self, client, db, test_company, test_storecode, checkout_data
    ):
        hung = checkout_data['hung']
        resp = client.post(
            '/cashier/batch_checkout/',
            data=json.dumps({
                'company': test_company,
                'storecode': test_storecode,
                'cashier': 'E001',
                'uuids': [str(hung.uuid)],
                'payments': {},
                'splits': {},
            }),
            content_type='application/json',
        )
        data = resp.json()
        assert data.get('ok') is True
        assert data.get('success') == 0
        assert '不可使用付款卡' in data['results'][0]['message']


class TestBatchCheckoutPendingPayCard:
    def test_rejects_pending_paycard_on_hung_header(
        self, client, db, test_company, test_storecode, checkout_data
    ):
        hung = checkout_data['hung']
        Cardinfo.objects.filter(company=test_company, ccode='C001').update(status='P')
        resp = client.post(
            '/cashier/batch_checkout/',
            data=json.dumps({
                'company': test_company,
                'storecode': test_storecode,
                'cashier': 'E001',
                'uuids': [str(hung.uuid)],
                'payments': {},
                'splits': {},
            }),
            content_type='application/json',
        )
        data = resp.json()
        assert data.get('ok') is True
        assert data.get('success') == 0
        assert '尚未生效' in data['results'][0]['message']
        hung.refresh_from_db()
        assert hung.psstatus_hung == '10'

    def test_rejects_pending_paycard_in_splits(
        self, client, db, test_company, test_storecode, checkout_data
    ):
        hung = checkout_data['hung']
        Cardinfo.objects.filter(company=test_company, ccode='C001').update(status='P')
        hung.ccode_hung = ''
        hung.save(update_fields=['ccode_hung'])
        ExpenseHung.objects.filter(hunguuid=hung).update(otherserno_hung='')
        resp = client.post(
            '/cashier/batch_checkout/',
            data=json.dumps({
                'company': test_company,
                'storecode': test_storecode,
                'cashier': 'E001',
                'uuids': [str(hung.uuid)],
                'payments': {},
                'splits': {
                    str(hung.uuid): [
                        {'pcode': 'CARD', 'ccode': 'C001', 'amount': 100},
                    ],
                },
            }),
            content_type='application/json',
        )
        data = resp.json()
        assert data.get('ok') is True
        assert data.get('success') == 0
        assert '尚未生效' in data['results'][0]['message']
        hung.refresh_from_db()
        assert hung.psstatus_hung == '10'

    def test_rejects_pending_paycard_even_one_fen_with_cash_makeup(
        self, client, db, test_company, test_storecode, checkout_data
    ):
        """未生效卡支出 0.01 + 现金补齐 → 仍须整单禁止。"""
        hung = checkout_data['hung']
        Cardinfo.objects.filter(company=test_company, ccode='C001').update(status='P')
        hung.ccode_hung = ''
        hung.save(update_fields=['ccode_hung'])
        ExpenseHung.objects.filter(hunguuid=hung).update(otherserno_hung='')
        card = Cardinfo.objects.get(company=test_company, ccode='C001')
        before = card.leftmoney
        resp = client.post(
            '/cashier/batch_checkout/',
            data=json.dumps({
                'company': test_company,
                'storecode': test_storecode,
                'cashier': 'E001',
                'uuids': [str(hung.uuid)],
                'payments': {},
                'splits': {
                    str(hung.uuid): [
                        {'pcode': 'CARD', 'ccode': 'C001', 'amount': 0.01},
                        {'pcode': 'CASH', 'ccode': '', 'amount': 99.99},
                    ],
                },
            }),
            content_type='application/json',
        )
        data = resp.json()
        assert data.get('ok') is True
        assert data.get('success') == 0
        assert '尚未生效' in data['results'][0]['message']
        hung.refresh_from_db()
        assert hung.psstatus_hung == '10'
        card.refresh_from_db()
        assert card.leftmoney == before
