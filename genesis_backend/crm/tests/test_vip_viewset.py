# coding=utf-8
"""
VipViewSet 筛选功能测试。
"""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from rest_framework import status

from baseinfo.models import Vip


VIP_URL = "/crm/vip/"
TEST_COMPANY = "testco"
TEST_STORECODE = "99"


def _create_vips():
    """创建一批测试会员数据。"""
    Vip.objects.filter(company=TEST_COMPANY).delete()
    data = [
        {
            "company": TEST_COMPANY,
            "storecode": TEST_STORECODE,
            "flag": "Y",
            "vcode": "V001",
            "vname": "张三",
            "mtcode": "13800000001",
            "viplevel": "A",
            "viptype": "10",
            "sex": "男",
            "birth": "0101",
            "indate": "2024-01-01",
            "telph": "13800000001",
            "wechat": "zhangsan",
        },
        {
            "company": TEST_COMPANY,
            "storecode": TEST_STORECODE,
            "flag": "Y",
            "vcode": "V002",
            "vname": "李四",
            "mtcode": "13800000002",
            "viplevel": "B",
            "viptype": "10",
            "sex": "女",
            "birth": "0202",
            "indate": "2024-06-15",
            "telph": "13800000002",
            "wechat": "lisi",
        },
        {
            "company": TEST_COMPANY,
            "storecode": TEST_STORECODE,
            "flag": "Y",
            "vcode": "V003",
            "vname": "散客王",
            "mtcode": "",
            "viplevel": "C",
            "viptype": "20",
            "sex": "男",
            "birth": "",
            "indate": "2024-03-20",
            "telph": "",
        },
    ]
    return [Vip.objects.create(**d) for d in data]


@pytest.mark.django_db
class TestVipViewSetFilters:
    """VipViewSet 筛选参数测试。"""

    def setup_method(self):
        self.client = APIClient()
        self.vips = _create_vips()

    def _list(self, params: dict) -> dict:
        params.setdefault("company", TEST_COMPANY)
        resp = self.client.get(VIP_URL, params)
        assert resp.status_code == status.HTTP_200_OK, resp.data
        return resp.json()

    # === 基础 ===
    def test_list_returns_all(self):
        data = self._list({"company": TEST_COMPANY, "page_size": 50})
        assert data["count"] == 3

    # === search ===
    def test_search_by_name(self):
        data = self._list({"search": "张三"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001"}

    def test_search_by_phone(self):
        data = self._list({"search": "13800000002"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V002"}

    def test_search_by_vcode(self):
        data = self._list({"search": "V003"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V003"}

    # === viplevel ===
    def test_filter_viplevel(self):
        data = self._list({"viplevel": "A"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001"}

    # === viptype ===
    def test_filter_viptype_member(self):
        data = self._list({"viptype": "10"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001", "V002"}

    def test_filter_viptype_visitor(self):
        data = self._list({"viptype": "20"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V003"}

    # === sex ===
    def test_filter_sex_male(self):
        data = self._list({"sex": "男"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001", "V003"}

    def test_filter_sex_female(self):
        data = self._list({"sex": "女"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V002"}

    # === birth ===
    def test_filter_birth_range(self):
        data = self._list({"birth__gte": "0101", "birth__lte": "0202"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001", "V002"}

    # === indate ===
    def test_filter_indate_range(self):
        data = self._list({"indate__gte": "2024-03-01", "indate__lte": "2024-06-30"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V002", "V003"}

    # === has_phone ===
    def test_filter_has_phone_yes(self):
        data = self._list({"has_phone": "Y"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001", "V002"}

    def test_filter_has_phone_no(self):
        data = self._list({"has_phone": "N"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V003"}

    # === wechat ===
    def test_filter_wechat(self):
        data = self._list({"wechat": "zhangsan"})
        codes = {r["vcode"] for r in data["results"]}
        assert codes == {"V001"}
