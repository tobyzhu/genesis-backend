# coding=utf-8

import uuid

import pytest

from assistant.data_tools import tool_search_vips
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_vip


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


@pytest.mark.django_db
def test_search_vips_empty_keyword_returns_empty_list():
    assert tool_search_vips(TEST_COMPANY, TEST_STORECODE, keyword="") == []
    assert tool_search_vips(TEST_COMPANY, TEST_STORECODE, keyword="   ") == []


@pytest.mark.django_db
def test_search_vips_by_telph():
    telph = _unique_telph()
    vip = make_vip(telph=telph, vname="搜索测试A")

    rows = tool_search_vips(TEST_COMPANY, TEST_STORECODE, keyword=telph[-8:])

    assert any(r["vipuuid"] == str(vip.uuid) for r in rows)
    match = next(r for r in rows if r["vipuuid"] == str(vip.uuid))
    assert match["telph"] == telph
    assert match["vname"] == "搜索测试A"


@pytest.mark.django_db
def test_search_vips_by_vname_partial():
    suffix = uuid.uuid4().hex[:6]
    vname = f"唯一名{suffix}"
    vip = make_vip(telph=_unique_telph(), vname=vname)

    rows = tool_search_vips(TEST_COMPANY, TEST_STORECODE, keyword=suffix)

    assert any(r["vipuuid"] == str(vip.uuid) for r in rows)


@pytest.mark.django_db
def test_search_vips_respects_store_isolation():
    telph = _unique_telph()
    make_vip(telph=telph, storecode=TEST_STORECODE, vname="门店隔离")

    rows = tool_search_vips(TEST_COMPANY, "88", keyword=telph)
    assert rows == []


@pytest.mark.django_db
def test_search_vips_limit():
    telph_prefix = "139" + uuid.uuid4().hex[:4]
    for i in range(3):
        make_vip(telph=f"{telph_prefix}{i:04d}", vname=f"批量{i}")

    rows = tool_search_vips(TEST_COMPANY, TEST_STORECODE, keyword=telph_prefix, limit=2)
    assert len(rows) <= 2
