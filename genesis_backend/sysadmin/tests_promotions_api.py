# coding=utf-8
"""营销活动通用 CRUD 接口测试（PC 营销活动页依赖路径）。"""
import json

import pytest

from baseinfo.models import Promotions, Promotionsdetail


def _post(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type='application/json')


def _put(client, url, payload):
    return client.put(url, data=json.dumps(payload), content_type='application/json')


@pytest.fixture
def promotion(db, test_company):
    return Promotions.objects.create(
        company=test_company, flag='Y', promotionsid='ACT001',
        promotionsname='测试活动', mainttype='30', promotionsstatus='active',
    )


class TestPromotionsGenericApi:
    def test_create_and_list_promotion(self, client, db, test_company):
        resp = _post(client, '/adviser/sysadmin-data/baseinfo.promotions/', {
            'company': test_company,
            'promotionsid': 'ACT001',
            'promotionsname': '测试活动',
            'mainttype': '30',
            'promotionsstatus': 'active',
        })
        assert resp.status_code == 200
        assert resp.json().get('ok') is True
        pk = resp.json().get('pk')
        assert pk

        list_resp = client.get('/adviser/sysadmin-data/baseinfo.promotions/', {
            'company': test_company, 'page': 1, 'page_size': 20,
        })
        assert list_resp.status_code == 200
        rows = list_resp.json().get('rows') or []
        assert any(r.get('promotionsid') == 'ACT001' for r in rows)

    def test_create_detail_with_fk_uuid_string(self, client, db, test_company, promotion):
        resp = _post(client, '/adviser/sysadmin-data/baseinfo.promotionsdetail/', {
            'company': test_company,
            'promotionsuuid': str(promotion.uuid),
            'promotionsid': 'ACT001',
            'promotionsseq': '0001',
            'ttype': 'S',
            'sgcode': 'SV001',
            's_qty': 1,
            's_price': 100,
            'promotionsqty': 1,
            'promotionsprice': 88,
            'promotionsamount': 88,
            'stype': 'N',
        })
        assert resp.status_code == 200, resp.content
        assert resp.json().get('ok') is True

        detail = Promotionsdetail.objects.get(company=test_company, promotionsid='ACT001')
        assert str(detail.promotionsuuid_id) == str(promotion.uuid)
        assert float(detail.promotionsprice) == 88

        list_resp = client.get('/adviser/sysadmin-data/baseinfo.promotionsdetail/', {
            'company': test_company, 'promotionsuuid': str(promotion.uuid),
            'page': 1, 'page_size': 20,
        })
        assert list_resp.status_code == 200
        rows = list_resp.json().get('rows') or []
        assert len(rows) == 1
        assert rows[0]['sgcode'] == 'SV001'

    def test_update_and_soft_delete(self, client, db, test_company, promotion):
        detail = Promotionsdetail.objects.create(
            company=test_company, flag='Y', promotionsuuid=promotion,
            promotionsid='ACT001', promotionsseq='0001',
            ttype='S', sgcode='SV001',
        )
        put_resp = _put(client, f'/adviser/sysadmin-data/baseinfo.promotions/{promotion.uuid}/', {
            'promotionsname': '改名活动', 'promotionsstatus': 'inactive',
        })
        assert put_resp.status_code == 200
        promotion.refresh_from_db()
        assert promotion.promotionsname == '改名活动'

        del_resp = client.delete(f'/adviser/sysadmin-data/baseinfo.promotionsdetail/{detail.uuid}/')
        assert del_resp.status_code == 200
        detail.refresh_from_db()
        assert detail.flag == 'N'

    def test_list_filters_active_and_blank_status(self, client, db, test_company):
        Promotions.objects.create(
            company=test_company, flag='Y', promotionsid='ACT001',
            promotionsname='启用活动', mainttype='10', promotionsstatus='active',
        )
        Promotions.objects.create(
            company=test_company, flag='Y', promotionsid='ACT002',
            promotionsname='停用活动', mainttype='20',
        )

        active_resp = client.get('/adviser/sysadmin-data/baseinfo.promotions/', {
            'company': test_company, 'page': 1, 'page_size': 20,
            'promotionsstatus': 'active',
        })
        assert active_resp.status_code == 200
        assert [r['promotionsid'] for r in active_resp.json()['rows']] == ['ACT001']

        blank_resp = client.get('/adviser/sysadmin-data/baseinfo.promotions/', {
            'company': test_company, 'page': 1, 'page_size': 20,
            'promotionsstatus': '__blank__',
        })
        assert blank_resp.status_code == 200
        assert [r['promotionsid'] for r in blank_resp.json()['rows']] == ['ACT002']
