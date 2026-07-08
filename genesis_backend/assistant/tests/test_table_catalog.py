# coding=utf-8

import pytest

from assistant.data_tools import tool_describe_table, tool_list_table_catalog
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE


def test_list_table_catalog_includes_vip_and_expvstoll():
    rows = tool_list_table_catalog(TEST_COMPANY, TEST_STORECODE)
    tables = {r["db_table"] for r in rows}

    assert "vip" in tables
    assert "expvstoll" in tables
    assert rows == sorted(rows, key=lambda r: r["db_table"])

    vip_row = next(r for r in rows if r["db_table"] == "vip")
    assert vip_row["app"] == "baseinfo"
    assert vip_row["model"] == "Vip"


def test_list_table_catalog_excludes_django_internal_apps():
    rows = tool_list_table_catalog(TEST_COMPANY, TEST_STORECODE)
    apps = {r["app"] for r in rows}
    assert "auth" not in apps
    assert "contenttypes" not in apps


def test_describe_table_vip_has_uuid_primary_key():
    info = tool_describe_table(TEST_COMPANY, TEST_STORECODE, db_table="vip")

    assert info["db_table"] == "vip"
    assert info["model"] == "Vip"
    assert info["primary_key_column"] == "uuid"
    field_names = {f["name"] for f in info["fields"]}
    assert {"telph", "vname", "vcode", "company", "storecode"}.issubset(field_names)
    assert info.get("sql_hints")


def test_describe_table_strips_app_prefix():
    info = tool_describe_table(TEST_COMPANY, TEST_STORECODE, db_table="cashier.expvstoll")
    assert info["db_table"] == "expvstoll"
    assert info["model"] == "Expvstoll"


def test_describe_table_missing_name_returns_error():
    assert tool_describe_table(TEST_COMPANY, TEST_STORECODE, db_table="") == {
        "error": "缺少 db_table"
    }


def test_describe_table_unknown_table_returns_error():
    result = tool_describe_table(TEST_COMPANY, TEST_STORECODE, db_table="not_a_real_table_xyz")
    assert result["error"] == "未找到表"
    assert result["db_table"] == "not_a_real_table_xyz"
