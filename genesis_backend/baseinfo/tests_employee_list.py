# coding=utf-8
"""员工下拉列表接口测试（客户关怀等页面依赖）。"""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from baseinfo.models import Empl


@pytest.mark.django_db
class TestEmployeesList:
    def test_list_scoped_by_company_and_storecode(self):
        Empl.objects.filter(company="testco").delete()
        Empl.objects.create(company="testco", storecode="99", flag="Y", ecode="1001", ename="顾问甲")
        Empl.objects.create(company="testco", storecode="98", flag="Y", ecode="1002", ename="顾问乙")
        Empl.objects.create(company="otherco", storecode="99", flag="Y", ecode="2001", ename="他人")

        resp = APIClient().get("/baseinfo/employees/", {"company": "testco", "storecode": "99"})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert {r["ecode"] for r in results} == {"1001"}

    def test_list_without_storecode_returns_all_company(self):
        Empl.objects.filter(company="testco").delete()
        Empl.objects.create(company="testco", storecode="99", flag="Y", ecode="1001", ename="顾问甲")
        Empl.objects.create(company="testco", storecode="98", flag="Y", ecode="1002", ename="顾问乙")

        resp = APIClient().get("/baseinfo/employees/", {"company": "testco"})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2
