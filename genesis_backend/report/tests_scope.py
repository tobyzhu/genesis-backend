# coding=utf-8
"""报表门店范围解析单测。"""
from report.scope import intersect_storecodes, parse_storecodes_param


def test_parse_storecodes_param_dedupes_and_strips():
    assert parse_storecodes_param('01, 03,01,,05') == ['01', '03', '05']
    assert parse_storecodes_param('') == []
    assert parse_storecodes_param(None) == []


def test_intersect_empty_requested_means_all_allowed():
    assert intersect_storecodes([], ['01', '02', '03']) == ['01', '02', '03']


def test_intersect_clips_unauthorized():
    assert intersect_storecodes(['01', '99', '03'], ['01', '02', '03']) == ['01', '03']


def test_intersect_keeps_requested_order():
    assert intersect_storecodes(['03', '01'], ['01', '02', '03']) == ['03', '01']
