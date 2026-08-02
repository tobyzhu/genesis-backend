# coding=utf-8
"""结账前批量更新挂单明细（折扣/赠送/员工）测试。"""
import json
from decimal import Decimal

import pytest

from adviser.models import ExpvstollHung, ExpenseHung
from baseinfo.models import Serviece, Vip


@pytest.fixture
def audit_hung(db, test_company, test_storecode):
    vip = Vip.objects.create(
        company=test_company, storecode=test_storecode, flag='Y',
        vcode='V100', vname='审核会员', mtcode='13900000001',
        viplevel='A', viptype='10', valiflag='Y',
    )
    Serviece.objects.create(
        company=test_company, svrcdoe='SV100', svrname='护理服务',
        price='200', discountclass='10', topcode='100',
        saleflag='Y', valiflag='Y', flag='Y',
    )
    hung = ExpvstollHung.objects.create(
        company=test_company, storecode=test_storecode,
        vipuuid=vip, vcode_hung=vip.vcode, vipcode=vip.vcode,
        exptxserno_hung='HA01', vsdate_hung='20260801',
        vstime_hung='120000', totmount_hung='200',
        psstatus_hung='10', ttype_hung='S', valiflag_hung='Y', flag='Y',
    )
    item = ExpenseHung.objects.create(
        company=test_company, storecode=test_storecode,
        hunguuid=hung, exptxserno_hung='HA01', ditem_hung='0001',
        ttype_hung='S', stype_hung='N', srvcode_hung='SV100',
        s_qty_hung=1, s_price_hung='200', s_mount_hung='200',
        srvactmount_hung='200', addvamoney_hung='200',
        secdisc_hung=1, srvmondisc_hung=0, pmcode_hung='',
        flag='Y',
    )
    return {'hung': hung, 'item': item}


class TestUpdateHungItemsAudit:
    def test_updates_discount_stype_pmcode_and_totmount(
        self, client, db, test_company, test_storecode, audit_hung
    ):
        hung = audit_hung['hung']
        item = audit_hung['item']
        resp = client.post(
            '/adviser/update_hung_items_audit/',
            data=json.dumps({
                'company': test_company,
                'storecode': test_storecode,
                'items': [{
                    'hunguuid': str(hung.uuid),
                    'uuid': str(item.uuid),
                    'ditem': '0001',
                    'secdisc': 0.8,
                    'stype': 'P',
                    'pmcode': 'E001',
                    'asscode1': 'E002',
                    'asscode2': 'E003',
                    'mondisc': 0,
                }],
            }),
            content_type='application/json',
        )
        data = resp.json()
        assert data.get('ok') is True

        item.refresh_from_db()
        hung.refresh_from_db()
        assert Decimal(str(item.secdisc_hung)) == Decimal('0.8')
        assert item.stype_hung == 'P'
        assert item.pmcode_hung == 'E001'
        assert item.asscode1_hung == 'E002'
        assert item.asscode2_hung == 'E003'
        assert Decimal(str(item.s_mount_hung)) == Decimal('160.00')
        assert Decimal(str(hung.totmount_hung)) == Decimal('160.00')
