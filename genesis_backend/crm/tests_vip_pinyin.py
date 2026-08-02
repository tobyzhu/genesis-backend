# coding=utf-8
"""VIP 列表拼音首字母筛选与拼音搜索测试。"""

import pytest

from baseinfo.models import Appoption
from baseinfo.models import Vip


def _make_vip(company, storecode, vcode, vname, pinyin, status=''):
    return Vip.objects.create(
        company=company, storecode=storecode, flag='Y',
        vcode=vcode, vname=vname, pinyin=pinyin,
        mtcode='13800000001', viplevel='A', viptype='10', status=status or None, valiflag='Y',
    )


def _rows(data):
    if isinstance(data, dict):
        return data.get('results', data.get('data', []))
    return data


class TestVipPinyinFilter:
    def test_filter_by_pinyin_initial(self, client, db, test_company, test_storecode):
        _make_vip(test_company, test_storecode, 'V001', '张三', 'zs')
        _make_vip(test_company, test_storecode, 'V002', '李四', 'ls')

        resp = client.get('/crm/vip/', {'company': test_company, 'pinyin': 'z'})
        assert resp.status_code == 200
        codes = [r['vcode'] for r in _rows(resp.json())]
        assert codes == ['V001']

    def test_pinyin_filter_is_case_insensitive(self, client, db, test_company, test_storecode):
        _make_vip(test_company, test_storecode, 'V003', '王五', 'ww')

        resp = client.get('/crm/vip/', {'company': test_company, 'pinyin': 'W'})
        assert resp.status_code == 200
        codes = [r['vcode'] for r in _rows(resp.json())]
        assert codes == ['V003']

    def test_search_includes_pinyin(self, client, db, test_company, test_storecode):
        _make_vip(test_company, test_storecode, 'V004', '赵六', 'zl')

        resp = client.get('/crm/vip/', {'company': test_company, 'search': 'zl'})
        assert resp.status_code == 200
        codes = [r['vcode'] for r in _rows(resp.json())]
        assert codes == ['V004']

    def test_status_name_is_serialized(self, client, db, test_company, test_storecode):
        _make_vip(test_company, test_storecode, 'V005', '周七', 'zq', status='20')

        resp = client.get('/crm/vip/', {'company': test_company, 'search': 'zq'})
        assert resp.status_code == 200
        rows = _rows(resp.json())
        assert rows and 'status_name' in rows[0]
        assert rows[0]['status'] == '20'

    def test_viptype_name_from_appoption(self, client, db, test_company, test_storecode):
        Appoption.objects.create(
            company='common', seg='viptype', itemname='20', itemvalues='会员', flag='Y'
        )
        _make_vip(test_company, test_storecode, 'V006', '吴八', 'wb', status='20')
        vip = Vip.objects.get(company=test_company, vcode='V006')
        vip.viptype = '20'
        vip.save()

        resp = client.get('/crm/vip/', {'company': test_company, 'search': 'wb'})
        assert resp.status_code == 200
        rows = _rows(resp.json())
        assert rows and rows[0]['viptype_name'] == '会员'

    def test_default_ordering_is_pinyin_then_vcode(self, client, db, test_company, test_storecode):
        _make_vip(test_company, test_storecode, 'V100', '张三', 'zs')
        _make_vip(test_company, test_storecode, 'V101', '李四', 'ls')

        resp = client.get('/crm/vip/', {'company': test_company})
        assert resp.status_code == 200
        codes = [r['vcode'] for r in _rows(resp.json())]
        assert codes == ['V101', 'V100']
