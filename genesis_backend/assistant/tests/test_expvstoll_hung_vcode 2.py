# coding=utf-8
"""挂账单 vcode_hung 自动补齐与 legacy vipcode 回填。"""

from __future__ import annotations

import pytest

from adviser.models import ExpvstollHung
from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_vip


@pytest.mark.django_db
def test_expvstoll_hung_save_fills_vcode_from_vip():
    vip = make_vip(vcode="0100970")
    hung = ExpvstollHung.objects.create(
        company=TEST_COMPANY,
        storecode=TEST_STORECODE,
        vipuuid=vip,
        valiflag_hung="Y",
    )
    assert hung.vcode_hung == "0100970"


@pytest.mark.django_db
def test_expvstoll_hung_save_fills_vcode_from_legacy_vipcode():
    vip = make_vip(vcode="0100999")
    hung = ExpvstollHung(
        company=TEST_COMPANY,
        storecode=TEST_STORECODE,
        vipuuid=vip,
        vipcode="0100970",
        valiflag_hung="Y",
    )
    hung.save()
    assert hung.vcode_hung == "0100970"


@pytest.mark.django_db
def test_expvstoll_hung_save_keeps_existing_vcode_hung():
    vip = make_vip(vcode="0100999")
    hung = ExpvstollHung.objects.create(
        company=TEST_COMPANY,
        storecode=TEST_STORECODE,
        vipuuid=vip,
        vcode_hung="CUSTOM01",
        valiflag_hung="Y",
    )
    assert hung.vcode_hung == "CUSTOM01"
