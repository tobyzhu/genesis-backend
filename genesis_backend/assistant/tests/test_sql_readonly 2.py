# coding=utf-8

import pytest

from assistant.sql_readonly import _assert_readonly_shape, _physical_table_name


def test_physical_table_name_strips_schema():
    assert _physical_table_name("cashier.expvstoll") == "expvstoll"
    assert _physical_table_name("vip") == "vip"


def test_assert_readonly_shape_allows_select():
    _assert_readonly_shape("SELECT uuid FROM vip WHERE company='demo'")


def test_assert_readonly_shape_rejects_delete():
    with pytest.raises(ValueError, match="SELECT|WITH"):
        _assert_readonly_shape("DELETE FROM vip")


def test_assert_readonly_shape_rejects_multi_statement():
    with pytest.raises(ValueError, match="分号"):
        _assert_readonly_shape("SELECT 1; SELECT 2")


def test_assert_readonly_shape_rejects_comments():
    with pytest.raises(ValueError, match="注释"):
        _assert_readonly_shape("SELECT 1 -- comment")
