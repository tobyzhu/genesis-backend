# coding=utf-8
"""pytest 全局配置：测试库开关在 genesis/settings.py 中读取 GENESIS_USE_TEST_DB。"""

from __future__ import annotations

import os

import pytest


def pytest_configure(config):
    os.environ.setdefault("GENESIS_USE_TEST_DB", "1")


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """复用 scripts/setup-test-db.sh 准备好的 test_* 库，不再 create/migrate。"""
    with django_db_blocker.unblock():
        pass


@pytest.fixture
def test_company():
    return "testco"


@pytest.fixture
def test_storecode():
    return "99"
