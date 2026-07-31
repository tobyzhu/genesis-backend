# coding=utf-8
from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def fmt_amount(value):
    if value is None:
        return '0.00'
    return '{:,.2f}'.format(Decimal(str(value)))


@register.filter
def fmt_qty(value):
    if value is None:
        return '0'
    d = Decimal(str(value))
    if d == d.to_integral_value():
        return str(int(d))
    return '{:,.2f}'.format(d)
