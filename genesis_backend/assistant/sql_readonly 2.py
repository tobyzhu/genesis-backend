#coding = utf-8
"""Guarded read-only SQL execution for the assistant (MySQL via Django connection)."""

from __future__ import annotations

import datetime as pydatetime
import decimal
import logging
import os
import re
import sys
from typing import Any, Dict, List, Set, Tuple

from django.db import connection

logger = logging.getLogger("assistant.sql_readonly")

_ALLOWED_TABLES_CACHE: Set[str] | None = None

_SKIP_APP_LABELS = frozenset(
    {
        "admin",
        "auth",
        "contenttypes",
        "sessions",
        "sites",
    }
)

_FORBIDDEN_FRAGMENTS = [
    " insert ",
    " update ",
    " delete ",
    " drop ",
    " alter ",
    " create ",
    " truncate ",
    " replace ",
    " grant ",
    " revoke ",
    " lock ",
    " unlock ",
    " call ",
    " execute ",
    " outfile",
    " infile",
    " load data",
    " handler ",
    " do ",
    " xa ",
    " savepoint ",
    " release ",
    " rollback ",
    " merge ",
]


def default_max_sql_rows() -> int:
    try:
        return max(10, min(int(os.environ.get("ASSISTANT_SQL_MAX_ROWS", "200")), 500))
    except (TypeError, ValueError):
        return 200


def _physical_table_name(name: str) -> str:
    """MySQL 物理表名（去掉库名/schema 或 Django app 前缀，如 cashier.expvstoll → expvstoll）。"""
    t = (name or "").strip().lower()
    if not t:
        return t
    if "." in t:
        return t.rsplit(".", 1)[-1]
    return t


_TABLE_REF_STOPWORDS = frozenset(
    {
        "on",
        "using",
        "where",
        "group",
        "order",
        "having",
        "limit",
        "inner",
        "left",
        "right",
        "cross",
        "natural",
        "join",
        "straight_join",
        "lateral",
    }
)

# FROM/JOIN 后的表引用（支持 schema.table、反引号、可选 AS 别名）
_TABLE_REF_PATTERN = re.compile(
    r"\b(?:from|join)\s+"
    r"(?:`([^`]+)`\.`([^`]+)`"
    r"|`([^`]+)`"
    r"|([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)"
    r"|([a-z_][a-z0-9_]*))"
    r"(?:\s+(?:as\s+)?(?:`([^`]+)`|([a-z_][a-z0-9_]*)))?",
    re.IGNORECASE,
)


def _parse_table_references(sql: str) -> Tuple[Dict[str, str], List[str]]:
    """
    从 SQL 解析 FROM/JOIN 表引用。
    返回 (别名→物理表名, 物理表名列表)。
    """
    alias_to_physical: Dict[str, str] = {}
    physical_tables: List[str] = []
    for m in _TABLE_REF_PATTERN.finditer(sql or ""):
        q_schema, q_table, q_only, schema, table, table_only, q_alias, alias = m.groups()
        if q_schema and q_table:
            phys = _physical_table_name(q_table)
        elif schema and table:
            phys = _physical_table_name(table)
        elif q_only:
            phys = _physical_table_name(q_only)
        elif table_only:
            phys = _physical_table_name(table_only)
        else:
            continue
        physical_tables.append(phys)
        alias_name = (q_alias or alias or "").strip().lower()
        if alias_name and alias_name not in _TABLE_REF_STOPWORDS:
            alias_to_physical[alias_name] = phys
        alias_to_physical[phys] = phys
    # 保持顺序去重
    uniq_phys = list(dict.fromkeys(physical_tables))
    return alias_to_physical, uniq_phys


def _collect_physical_tables_for_validation(sql: str) -> List[str]:
    """结合 SQL 解析与 EXPLAIN，得到用于白名单校验的物理表名。"""
    alias_map, parsed_tables = _parse_table_references(sql)
    explain_tables: List[str] = []
    try:
        explain_tables = _explain_physical_tables(sql)
    except Exception:
        explain_tables = []

    resolved: List[str] = []
    for name in explain_tables:
        low = (name or "").strip().lower()
        if not low or low.startswith("<"):
            continue
        if low in alias_map:
            resolved.append(alias_map[low])
            continue
        phys = _physical_table_name(low)
        if phys in alias_map:
            resolved.append(alias_map[phys])
        else:
            resolved.append(phys)

    for p in parsed_tables:
        if p not in resolved:
            resolved.append(p)
    return list(dict.fromkeys(resolved))


def _normalize_qualified_tables_in_sql(sql: str, allowed: Set[str]) -> str:
    """
    将 FROM/JOIN 中的 app.table 改写为物理表名 table（当 table 在白名单内时）。
    例如：FROM cashier.expvstoll → FROM expvstoll
    """
    pattern = re.compile(
        r"(\bfrom|\bjoin)\s+"
        r"`?([a-z_][a-z0-9_]*)`?\.`?([a-z_][a-z0-9_]*)`?"
        r"(\s+(?:as\s+)?`?[a-z_][a-z0-9_]*`?)?",
        re.IGNORECASE,
    )

    def repl(m: re.Match) -> str:
        kw, table, tail = m.group(1), m.group(3).lower(), m.group(4) or ""
        if table in allowed:
            return f"{kw} {table}{tail}"
        return m.group(0)

    return pattern.sub(repl, sql)


def get_allowed_tables() -> Set[str]:
    global _ALLOWED_TABLES_CACHE
    if _ALLOWED_TABLES_CACHE is not None:
        return _ALLOWED_TABLES_CACHE
    from django.apps import apps

    names: Set[str] = set()
    for model in apps.get_models():
        if model._meta.app_label in _SKIP_APP_LABELS:
            continue
        names.add(model._meta.db_table.lower())
    _ALLOWED_TABLES_CACHE = names
    return names


def _normalize_sql(sql: str) -> str:
    return (sql or "").strip()


def _assert_readonly_shape(sql: str) -> None:
    s = _normalize_sql(sql)
    if not s:
        raise ValueError("SQL 为空")
    low = s.lower()
    if not (low.startswith("select") or low.startswith("with")):
        raise ValueError("仅允许以 SELECT 或 WITH 开头的只读查询")
    padded = f" {low} "
    for frag in _FORBIDDEN_FRAGMENTS:
        if frag in padded:
            raise ValueError(f"包含不允许的关键字（{frag.strip()}）")
    if "--" in s or "/*" in s or "*/" in s:
        raise ValueError("不允许 SQL 注释")
    if ";" in s.rstrip().rstrip(";"):
        raise ValueError("仅允许单条 SQL，不能包含分号拼接多条语句")
    if " for update" in padded or " lock in share mode" in padded:
        raise ValueError("不允许锁定类语句（FOR UPDATE / LOCK IN SHARE MODE）")


def _apply_limit(sql: str, max_rows: int) -> str:
    s = _normalize_sql(sql).rstrip().rstrip(";").strip()
    m = re.search(r"\blimit\s+(\d+)\s*$", s, flags=re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if n > max_rows:
            s = s[: m.start()] + f" LIMIT {max_rows}"
        return s
    return f"{s} LIMIT {max_rows}"


def _explain_physical_tables(sql: str) -> List[str]:
    """Return lowercase physical table names from MySQL EXPLAIN (best-effort)."""
    with connection.cursor() as cursor:
        cursor.execute(f"EXPLAIN {sql}")
        cols = [c[0] for c in (cursor.description or [])]
        rows = cursor.fetchall()
    out: List[str] = []
    # MySQL 8 / 5.7: column often named 'table'
    key_table = "table" if "table" in cols else None
    if not key_table:
        for c in cols:
            if c.lower() == "table":
                key_table = c
                break
    if not key_table:
        return out
    ti = cols.index(key_table)
    for row in rows:
        if ti >= len(row):
            continue
        raw = row[ti]
        if raw is None:
            continue
        t = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        t = _physical_table_name(t.strip())
        if not t or t.startswith("<"):
            continue
        out.append(t)
    return out


def _validate_tables_against_whitelist(tables: List[str], allowed: Set[str]) -> None:
    bad = []
    for t in tables:
        phys = _physical_table_name(t)
        if phys not in allowed:
            bad.append(t if phys == t else f"{t}（物理表名 {phys} 未授权）")
    if bad:
        raise ValueError(
            "SQL 访问了未授权的表: "
            + ", ".join(bad)
            + "。readonly_sql 请使用物理表名（如 expvstoll、vip、toll），"
            "不要加 Django app 前缀（错误示例 cashier.expvstoll）。"
            "请用 list_table_catalog / describe_table 确认 db_table 字段。"
        )


def _json_friendly_cell(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, pydatetime.datetime):
        return v.isoformat(sep=" ", timespec="seconds")
    if isinstance(v, pydatetime.date):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray)):
        return bytes(v).decode("utf-8", errors="replace")
    return v


def _terminal_log_sql(
    event: str,
    sql: str,
    *,
    detail: str = "",
    original_sql: str = "",
) -> None:
    """无数据或执行失败时，在 runserver 终端打印实际 SQL。"""
    parts = [f"[assistant readonly_sql {event}]"]
    if original_sql and original_sql.strip() != (sql or "").strip():
        parts.append(f"original: {original_sql.strip()}")
    parts.append(f"executed: {(sql or '').strip()}")
    if detail:
        parts.append(f"detail: {detail}")
    msg = "\n".join(parts)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    if event == "error":
        logger.error(msg)
    else:
        logger.warning(msg)


def _enhance_sql_execution_error(exc: BaseException) -> ValueError:
    msg = str(exc)
    low = msg.lower()
    hints: List[str] = []
    if "unknown column" in low and "vipuuid" in low:
        hints.append(
            "vip 表主键列是 uuid，没有 vipuuid 列；"
            "vipuuid 仅作为外键出现在 expvstoll、cardinfo、crmcase 等表中（指向 vip.uuid）。"
            "联表应写：JOIN vip v ON e.vipuuid = v.uuid"
        )
    if "unknown column" in low and "expvstolluuid" in low:
        hints.append("关联交易主表应使用 transuuid → expvstoll.uuid，没有 expvstolluuid 列。")
    if "unknown column" in low and "transuuid" in low and "vip" in low:
        hints.append("vip 表没有 transuuid；transuuid 在 expense/toll 表，指向 expvstoll.uuid。")
    if "unknown column" in low and any(
        col in low for col in ("s_mount", "cashratio", "cardratio", "sendratio")
    ):
        hints.append(
            "s_mount（列 S_MOUNT）、cashratio、cardratio、sendratio 在 expense 表，不在 expvstoll。"
            "expvstoll 用 totmount 表示整单金额。"
            "示例：SELECT ... SUM(x.s_mount*x.cashratio) FROM expense x "
            "JOIN expvstoll e ON x.transuuid=e.uuid JOIN vip v ON e.vipuuid=v.uuid"
        )
    if hints:
        return ValueError(f"{msg}。提示：{' '.join(hints)}")
    return ValueError(msg)


def run_readonly_select(sql: str, max_rows: int | None = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Run a single SELECT (or WITH … SELECT). Returns (rows_as_dicts, meta).
    """
    original_sql = _normalize_sql(sql)
    cap = max_rows if max_rows is not None else default_max_sql_rows()
    try:
        _assert_readonly_shape(sql)
    except ValueError as e:
        _terminal_log_sql("error", original_sql, detail=str(e))
        raise

    allowed = get_allowed_tables()
    normalized_sql = _normalize_qualified_tables_in_sql(original_sql, allowed)
    bounded = _apply_limit(normalized_sql, cap)
    try:
        phys = _collect_physical_tables_for_validation(bounded)
    except Exception as e:
        low = str(e).lower()
        if "unknown column" in low:
            err = _enhance_sql_execution_error(e)
            _terminal_log_sql("error", bounded, detail=str(err), original_sql=original_sql)
            raise err from e
        detail = f"EXPLAIN 校验失败（语法或权限）: {e}"
        _terminal_log_sql("error", bounded, detail=detail, original_sql=original_sql)
        raise ValueError(detail) from e
    try:
        _validate_tables_against_whitelist(phys, allowed)
    except ValueError as e:
        _terminal_log_sql("error", bounded, detail=str(e), original_sql=original_sql)
        raise

    try:
        with connection.cursor() as cursor:
            cursor.execute(bounded)
            cols = [c[0] for c in (cursor.description or [])]
            fetched = cursor.fetchall()
    except Exception as e:
        err = _enhance_sql_execution_error(e)
        _terminal_log_sql("error", bounded, detail=str(err), original_sql=original_sql)
        raise err from e
    rows: List[Dict[str, Any]] = []
    for r in fetched:
        row = {}
        for i, col in enumerate(cols):
            v = r[i] if i < len(r) else None
            row[col] = _json_friendly_cell(v)
        rows.append(row)
    if not rows:
        _terminal_log_sql(
            "empty",
            bounded,
            detail="查询成功但返回 0 行",
            original_sql=original_sql,
        )
    meta = {
        "rowcount": len(rows),
        "columns": cols,
        "tables_checked": phys,
        "limit_applied": cap,
        "sql_executed": bounded,
        "sql_normalized": normalized_sql if normalized_sql != original_sql else None,
    }
    return rows, meta
