# coding=utf-8
"""assistant 集成测试用最小数据工厂（租户 testco / 99）。"""

from __future__ import annotations

import datetime as pydatetime
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from baseinfo.models import Vip
from cashier.models import Expense, Expvstoll

TEST_COMPANY = "testco"
TEST_STORECODE = "99"


def make_vip(
    *,
    company: str = TEST_COMPANY,
    storecode: str = TEST_STORECODE,
    telph: str = "13800000001",
    vname: str = "测试会员",
    vcode: Optional[str] = None,
    **extra: Any,
) -> Vip:
    suffix = uuid.uuid4().hex[:6]
    return Vip.objects.create(
        company=company,
        storecode=storecode,
        flag="Y",
        telph=telph,
        mtcode=telph,
        vname=vname,
        vcode=vcode or f"T{suffix}",
        viptype="10",
        **extra,
    )


def make_expvstoll(
    vip: Vip,
    *,
    vsdate: str = "",
    totmount: Any = Decimal("100.00"),
    valiflag: str = "Y",
    **extra: Any,
) -> Expvstoll:
    if not vsdate:
        vsdate = pydatetime.date.today().strftime("%Y%m%d")
    return Expvstoll.objects.create(
        company=vip.company,
        storecode=vip.storecode,
        flag="Y",
        valiflag=valiflag,
        vipuuid=vip,
        vsdate=vsdate,
        totmount=totmount,
        exptxserno=f"TX{uuid.uuid4().hex[:12]}",
        **extra,
    )


def make_expense(
    trans: Expvstoll,
    *,
    ttype: str = "S",
    srvcode: str = "S001",
    s_mount: Any = Decimal("100.00"),
    **extra: Any,
) -> Expense:
    return Expense.objects.create(
        company=trans.company,
        storecode=trans.storecode,
        flag="Y",
        transuuid=trans,
        exptxserno=trans.exptxserno or f"TX{uuid.uuid4().hex[:8]}",
        ditem="01",
        ttype=ttype,
        srvcode=srvcode,
        s_mount=s_mount,
        s_qty=Decimal("1"),
        **extra,
    )
