# coding=utf-8
"""get_hung_list 收银结账列表：功能正确性 + 查询次数约束。"""
import pytest

from django.db import connection
from django.test.utils import CaptureQueriesContext

from adviser.models import Cardinfo, ExpvstollHung, ExpenseHung
from baseinfo.models import Cardtype, Goods, Serviece, Vip


def _make_hung_data(test_company, test_storecode):
    vip = Vip.objects.create(
        company=test_company, storecode=test_storecode, flag='Y',
        vcode='V001', vname='测试会员', mtcode='13800000001',
        viplevel='A', viptype='10', valiflag='Y',
    )
    svc = Serviece.objects.create(
        company=test_company, svrcdoe='SV001', svrname='清洁服务',
        price='100', saleflag='Y', valiflag='Y', flag='Y',
    )
    gd = Goods.objects.create(
        company=test_company, gcode='G001', gname='商品A',
        price='100', saleflag='Y', valiflag='Y', flag='Y',
    )
    ct = Cardtype.objects.create(
        company=test_company, cardtype='CT001', cardname='测试卡',
        comptype='amount', leftmoney='1000', price='1000',
        saleflag='Y', valiflag='Y', flag='Y',
    )
    Cardinfo.objects.create(
        company=test_company, storecode=test_storecode, ccode='C001',
        cardtype='CT001', cardtypeuuid=ct, vcode=vip.vcode, vipuuid=vip,
        status='O', flag='Y', leftmoney='1000',
    )
    for i in range(10):
        h = ExpvstollHung.objects.create(
            company=test_company, storecode=test_storecode,
            vipuuid=vip, vcode_hung=vip.vcode, vipcode=vip.vcode,
            exptxserno_hung=f'HS{i:02d}', vsdate_hung='20260731',
            vstime_hung='120000', totmount_hung='300',
            psstatus_hung='10', ttype_hung='S', valiflag_hung='Y', flag='Y',
            ccode_hung='C001' if i == 0 else '',
            cardtype_hung='CT001' if i == 0 else '',
        )
        line_specs = [
            ('S', svc.svrcdoe, '100', '0.8', '10'),
            ('S', svc.svrcdoe, '100', '1', '0'),
            ('G', gd.gcode, '100', '1', '0'),
        ]
        for j, (ttype, code, price, secdisc, mondisc) in enumerate(line_specs):
            s_mount = str(round(float(price) * float(secdisc) - float(mondisc), 2))
            ExpenseHung.objects.create(
                company=test_company, storecode=test_storecode,
                hunguuid=h, exptxserno_hung=h.exptxserno_hung,
                ditem_hung=f'{j + 1:04d}', ttype_hung=ttype,
                stype_hung='N', srvcode_hung=code, s_qty_hung=1,
                s_price_hung=price, s_mount_hung=s_mount,
                srvactmount_hung=s_mount, addvamoney_hung=s_mount,
                secdisc_hung=secdisc, srvmondisc_hung=mondisc,
                otherserno_hung='', flag='Y',
            )
    return vip


@pytest.fixture
def hung_data(db, test_company, test_storecode):
    return _make_hung_data(test_company, test_storecode)


class TestGetHungList:
    def test_returns_item_details_and_paycard(
        self, client, db, test_company, test_storecode, hung_data
    ):
        resp = client.get('/adviser/get_hung_list/', {
            'company': test_company,
            'storecode': test_storecode,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 10

        first = data[0]
        assert first['itemcount'] == 3
        names = [d['name'] for d in first['item_details']]
        assert names == ['清洁服务', '清洁服务', '商品A']
        first_line = first['item_details'][0]
        assert first_line['secdisc'] == 0.8
        assert first_line['mondisc'] == 10

        pay_order = next(d for d in data if d['paycode'] == 'C001')
        assert pay_order['cardtypename'] == '测试卡'

    def test_query_count_bounded(
        self, client, db, test_company, test_storecode, hung_data,
    ):
        # 10 单 × 3 明细：修复前逐行/逐单查询会远超此值
        with CaptureQueriesContext(connection) as ctx:
            resp = client.get('/adviser/get_hung_list/', {
                'company': test_company,
                'storecode': test_storecode,
            })
        assert resp.status_code == 200
        assert len(ctx.captured_queries) <= 20
