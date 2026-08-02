# coding=utf-8
from report.business_flow import _disc_percent, _fmt_date, _fmt_time, _specified_label


def test_fmt_date():
    assert _fmt_date('20260731') == '2026-07-31'
    assert _fmt_date('') == ''


def test_fmt_time():
    assert _fmt_time('092828') == '09:28:28'
    assert _fmt_time('92828') == '09:28:28'


def test_disc_percent():
    assert _disc_percent(1) == 100.0
    assert _disc_percent(0.85) == 85.0
    assert _disc_percent(100) == 100.0


def test_specified_label():
    assert _specified_label('1') == '是'
    assert _specified_label('Y') == '是'
    assert _specified_label('N') == '否'
    assert _specified_label('0') == '否'
    assert _specified_label('') == ''
    assert _specified_label('X') == 'X'
