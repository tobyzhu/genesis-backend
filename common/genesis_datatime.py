#coding:utf-8

from datetime import datetime,date


def datettime_to_datestring(ps_datetime):
    datestring= datetime(ps_datetime).strftime('yyyymmdd')
    return datestring
