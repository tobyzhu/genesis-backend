# coding=utf-8
"""通用 sysadmin 数据接口序列化回归测试。"""

import pytest

from baseinfo.models import Goods


class TestModelDataSerialization:
    def test_goods_list_with_image_fields(self, client, db, test_company):
        """商品含 ImageField，列表接口必须能正常序列化（回归 UUID 编码器 500）。"""
        Goods.objects.create(
            company=test_company, flag='Y', gcode='23400005', gname='测试商品',
            price='99', saleflag='Y', valiflag='Y',
        )
        resp = client.get('/adviser/sysadmin-data/baseinfo.goods/', {
            'company': test_company, 'gcode': '23400005', 'page': 1, 'page_size': 5,
        })
        assert resp.status_code == 200, resp.content
        rows = resp.json().get('rows') or []
        assert rows and rows[0]['gcode'] == '23400005'
        assert 'small_image' in rows[0]
        assert rows[0]['small_image'] == ''
