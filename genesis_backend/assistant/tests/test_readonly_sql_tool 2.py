# coding=utf-8

import uuid

import pytest

from assistant.data_tools import tool_readonly_sql
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_vip


def _unique_telph() -> str:
    return "138" + uuid.uuid4().hex[:8]


@pytest.mark.django_db
def test_readonly_sql_select_vip_row():
    telph = _unique_telph()
    vname = f"SQL会员{uuid.uuid4().hex[:4]}"
    make_vip(telph=telph, vname=vname)

    sql = (
        f"SELECT telph, vname FROM vip "
        f"WHERE company = '{TEST_COMPANY}' AND storecode = '{TEST_STORECODE}' "
        f"AND telph = '{telph}'"
    )
    result = tool_readonly_sql(TEST_COMPANY, TEST_STORECODE, sql=sql, max_rows=10)

    assert "error" not in result
    assert len(result["rows"]) >= 1
    assert result["rows"][0]["telph"] == telph
    assert result["rows"][0]["vname"] == vname
    assert result["meta"]["rowcount"] >= 1


@pytest.mark.django_db
def test_readonly_sql_empty_sql_returns_error():
    result = tool_readonly_sql(TEST_COMPANY, TEST_STORECODE, sql="")
    assert result["error"] == "sql 不能为空"
    assert result["rows"] == []


@pytest.mark.django_db
def test_readonly_sql_rejects_write_statement():
    with pytest.raises(ValueError, match="SELECT|WITH"):
        tool_readonly_sql(
            TEST_COMPANY,
            TEST_STORECODE,
            sql=f"DELETE FROM vip WHERE company='{TEST_COMPANY}'",
        )


@pytest.mark.django_db
def test_readonly_sql_join_expvstoll():
    telph = _unique_telph()
    vip = make_vip(telph=telph)
    from assistant.tests.factories import make_expvstoll

    make_expvstoll(vip, totmount="88.00")

    sql = (
        f"SELECT v.telph, COUNT(e.uuid) AS cnt FROM vip v "
        f"JOIN expvstoll e ON e.vipuuid = v.uuid "
        f"WHERE v.company = '{TEST_COMPANY}' AND v.storecode = '{TEST_STORECODE}' "
        f"AND v.telph = '{telph}' AND e.valiflag = 'Y' "
        f"GROUP BY v.telph"
    )
    result = tool_readonly_sql(TEST_COMPANY, TEST_STORECODE, sql=sql, max_rows=5)

    assert len(result["rows"]) == 1
    assert int(result["rows"][0]["cnt"]) >= 1
