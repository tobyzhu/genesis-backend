# coding=utf-8

import pytest

from assistant.tests.factories import TEST_COMPANY, TEST_STORECODE, make_vip


@pytest.mark.django_db
def test_vip_factory_persists():
    from baseinfo.models import Vip

    v = make_vip(telph="13800009999", vname="冒烟会员")
    assert v.uuid is not None
    row = Vip.objects.get(uuid=v.uuid)
    assert row.company == TEST_COMPANY
    assert row.storecode == TEST_STORECODE
    assert row.telph == "13800009999"
