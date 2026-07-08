#!/usr/bin/env bash
# 创建 test_<DB_NAME>，从源库复制表结构（不含数据），供 pytest 使用。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/genesis_backend"

.venv/bin/python - <<'PY'
import pymysql
from dotenv import dotenv_values

c = dotenv_values(".env")
db_name = c.get("DB_NAME") or "youlan"
test_db = f"test_{db_name}"
host = c.get("DB_HOST") or "127.0.0.1"
port = int(c.get("DB_PORT") or 3306)
user = c.get("DB_USER") or "sa"
password = c.get("DB_PASSWORD") or ""

conn = pymysql.connect(host=host, port=port, user=user, password=password)
conn.autocommit(True)
with conn.cursor() as cur:
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{test_db}` DEFAULT CHARACTER SET utf8mb4"
    )
    cur.execute(
        "SELECT TABLE_NAME FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'",
        (db_name,),
    )
    tables = [row[0] for row in cur.fetchall()]
    if not tables:
        raise SystemExit(f"源库 {db_name} 无表，请先确认 DB_NAME 正确")
    for table in tables:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS `{test_db}`.`{table}` "
            f"LIKE `{db_name}`.`{table}`"
        )
    print(f"Cloned {len(tables)} table structures: {db_name} -> {test_db} @ {host}")
conn.close()
PY

export GENESIS_USE_TEST_DB=1
.venv/bin/python manage.py migrate --noinput 2>/dev/null || true
echo "Done. Run: GENESIS_USE_TEST_DB=1 .venv/bin/pytest assistant/tests -q"
