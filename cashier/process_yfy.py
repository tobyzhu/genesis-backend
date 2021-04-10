
#coding = utf-8
import io
import sys
import urllib
#import urllib2
import re
import string
import pymysql
import time
import random
from urllib.request import urlopen

from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import date,datetime,timedelta
from django.core import serializers
from django.db.models import Avg,Sum,Count

# Create your views here.
#from jmj.views import SetPrecentData


def ProcessData():
    fromdate = ( date.today() + timedelta(days=0) ).strftime('%Y%m%d')
    todate = date.today().strftime('%Y%m%d')
    fromdate = '2019-06-10'
    todate = '2219-5-31'

    # period = '05'

    host='http://localhost:8080/'
    #抓取营业部吉祥物销售数据，处理作废记录，重新计算库存数
    url= host+ 'cashier/cal_empalarch_yfy_daily/?fromdate=' + fromdate + '&todate=' + todate
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req =urllib.request.Request(url=url,headers=headers)
    urllib.request.urlopen(req)


    url = host+ 'goods/processgoods/?fromdate=' + fromdate + '&todate=' + todate
    req =urllib.request.Request(url=url,headers=headers)
    urllib.request.urlopen(req)


    return 'finished'

ProcessData()