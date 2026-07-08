# -*- coding: utf-8 -*-
"""Optional legacy / sync MySQL connections; credentials from environment only."""
import os
import pymysql


def _g(key, default=""):
    return os.environ.get(key, default)


def connect_youlan_sync():
    """datamanage / youlan 同步库（如 youlan.softweb.net.cn）。"""
    return pymysql.connect(
        _g("YOULAN_SYNC_HOST"),
        _g("LEGACY_MYSQL_USER", "sa"),
        _g("LEGACY_MYSQL_PASSWORD", ""),
        _g("YOULAN_SYNC_DB", "youlan"),
    )


def connect_dieshang_sync():
    """ftp.softweb 等店尚同步库。"""
    return pymysql.connect(
        _g("DIESHANG_SYNC_HOST"),
        _g("LEGACY_MYSQL_USER", "sa"),
        _g("LEGACY_MYSQL_PASSWORD", ""),
        _g("DIESHANG_SYNC_DB", "youlan"),
        charset="utf8",
    )


def _jmj_read_user():
    return _g("JMJ_IMPORT_READ_USER") or _g("LEGACY_MYSQL_USER", "sa")


def connect_jmj_read():
    """jmj/goods: 从 genesis 等读库。"""
    return pymysql.connect(
        _g("JMJ_IMPORT_READ_HOST"),
        _jmj_read_user(),
        _g("LEGACY_MYSQL_PASSWORD", ""),
        _g("JMJ_IMPORT_READ_DB", "genesis"),
    )


def connect_jmj_write():
    """jmj/goods: 写 multistore 等。"""
    return pymysql.connect(
        _g("JMJ_IMPORT_WRITE_HOST"),
        _g("LEGACY_MYSQL_USER", "sa"),
        _g("LEGACY_MYSQL_PASSWORD", ""),
        _g("JMJ_IMPORT_WRITE_DB", "multistore"),
    )
