# coding=utf-8
"""营销活动分组（promotionsgroup + promotionsgroupdetail）主从保存测试。"""
import json

import pytest

from baseinfo.models import (
    Promotions,
    Promotionsdetail,
    Promotionsgroup,
    Promotionsgroupdetail,
    Serviece,
)


def _post(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type='application/json')


def _group_payload():
    return {
        'pgroupid': 'G001',
        'pgroupname': '测试分组',
        'pgrouptype': 'BUY',
        'status': 'active',
        'items': [{
            'ttype': 'S',
            'pgcode': 'SV001',
            'pgroupcondition': '',
            'qty1': 1,
            'price1': 88,
            'disc': 0.88,
            'amount1': 88,
            'oriprice': 100,
        }],
    }


def _header_payload(company, mainttype='10', promotionsid='ACT001'):
    return {
        'company': company,
        'promotionsid': promotionsid,
        'promotionsname': '测试活动',
        'mainttype': mainttype,
        'promotionsstatus': 'active',
        'fromdate': '20260801',
        'todate': '20260831',
        's_price': 88,
        'disc': 0.88,
        'emplperc': 1,
        'mainqty': 1,
        'sendqty': 0,
    }


@pytest.fixture
def service(db, test_company):
    return Serviece.objects.create(
        company=test_company, svrcdoe='SV001', svrname='清洁服务',
        price='100', discountclass='10', topcode='100',
        saleflag='Y', valiflag='Y', flag='Y',
    )


class TestPromotionGroupSetup:
    def test_save_tejia_activity_with_group(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='10')
        payload['group'] = _group_payload()
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 200, resp.content
        assert resp.json()['ok'] is True

        promo = Promotions.objects.get(company=test_company, promotionsid='ACT001')
        assert promo.mainpgroupid == 'G001'
        assert Promotionsgroup.objects.filter(company=test_company, pgroupid='G001', flag='Y').exists()
        detail = Promotionsgroupdetail.objects.get(
            company=test_company, pgroupid='G001', flag='Y'
        )
        assert detail.pgcode == 'SV001'
        assert float(detail.price1) == 88

        active = client.get('/adviser/active_promotions/', {
            'company': test_company, 'uuid': str(promo.uuid),
        })
        assert active.status_code == 200
        data = active.json()
        assert data['promotionsid'] == 'ACT001'
        assert data['items'][0]['sgcode'] == 'SV001'
        assert data['items'][0]['promotionsprice'] == 88

    def test_save_discount_activity_with_group(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='20', promotionsid='ACT002')
        payload['disc'] = 0.8
        payload['group'] = _group_payload()
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 200, resp.content

        promo = Promotions.objects.get(company=test_company, promotionsid='ACT002')
        assert promo.mainpgroupid == 'G001'
        active = client.get('/adviser/active_promotions/', {
            'company': test_company, 'uuid': str(promo.uuid),
        })
        assert active.json()['disc'] == 0.8
        assert active.json()['items'][0]['promotionsprice'] == 88

    def test_update_replaces_group_details(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='10', promotionsid='ACT003')
        payload['group'] = _group_payload()
        _post(client, '/adviser/save_promotion_setup/', payload)

        new_group = _group_payload()
        new_group['pgroupname'] = '改名分组'
        new_group['items'] = [{
            'ttype': 'S', 'pgcode': 'SV001', 'qty1': 2,
            'price1': 66, 'disc': 0.66, 'amount1': 132, 'oriprice': 100,
        }]
        payload['group'] = new_group
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 200

        assert Promotionsgroup.objects.get(
            company=test_company, pgroupid='G001', flag='Y'
        ).pgroupname == '改名分组'
        old = Promotionsgroupdetail.objects.filter(
            company=test_company, pgroupid='G001', flag='N'
        ).count()
        assert old == 1
        current = Promotionsgroupdetail.objects.get(
            company=test_company, pgroupid='G001', flag='Y'
        )
        assert float(current.qty1) == 2
        assert float(current.price1) == 66

    def test_save_combo_activity_with_items(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='30', promotionsid='ACT004')
        payload['items'] = [{
            'ttype': 'S', 'sgcode': 'SV001', 's_qty': 1, 's_price': 100,
            'promotionsqty': 1, 'promotionsprice': 80, 'promotionsamount': 80,
            'stype': 'N',
        }]
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 200, resp.content

        promo = Promotions.objects.get(company=test_company, promotionsid='ACT004')
        assert promo.mainpgroupid == ''
        detail = Promotionsdetail.objects.get(
            company=test_company, promotionsuuid=promo, flag='Y'
        )
        assert detail.sgcode == 'SV001'
        assert float(detail.promotionsprice) == 80

        active = client.get('/adviser/active_promotions/', {
            'company': test_company, 'uuid': str(promo.uuid),
        })
        data = active.json()
        assert data['combo_total'] == 80
        assert data['group_items'][0]['sgcode'] == 'SV001'

    def test_tejia_requires_group(self, client, db, test_company, service):
        payload = _header_payload(test_company, mainttype='10')
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 400
        assert '分组' in resp.json()['message']

    def test_combo_requires_items(self, client, db, test_company, service):
        payload = _header_payload(test_company, mainttype='30')
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 400
        assert '明细' in resp.json()['message']

    def test_get_promotion_setup_returns_group(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='20', promotionsid='ACT005')
        payload['group'] = _group_payload()
        save = _post(client, '/adviser/save_promotion_setup/', payload)
        uuid = save.json()['uuid']

        resp = client.get('/adviser/get_promotion_setup/', {
            'company': test_company, 'uuid': uuid,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['promotion']['mainttype'] == '20'
        assert data['group']['pgroupid'] == 'G001'
        assert data['group_items'][0]['pgcode'] == 'SV001'

    def test_send_group_type_saved(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='20', promotionsid='ACT006')
        group = _group_payload()
        group['pgrouptype'] = 'SEND'
        payload['group'] = group
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 200, resp.content

        promo = Promotions.objects.get(company=test_company, promotionsid='ACT006')
        assert promo.mainpgroupid == 'G001'
        assert Promotionsgroup.objects.get(
            company=test_company, pgroupid='G001', flag='Y'
        ).pgrouptype == 'SEND'

    def test_group_type_must_be_buy_or_send(
        self, client, db, test_company, service
    ):
        payload = _header_payload(test_company, mainttype='10', promotionsid='ACT007')
        group = _group_payload()
        group['pgrouptype'] = '10'
        payload['group'] = group
        resp = _post(client, '/adviser/save_promotion_setup/', payload)
        assert resp.status_code == 400
        assert 'BUY' in resp.json()['message']
