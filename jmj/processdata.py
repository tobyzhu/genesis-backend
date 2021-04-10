
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
import requests

from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import date,datetime,timedelta
from django.core import serializers
from django.db.models import Avg,Sum,Count

# Create your views here.
# from .views  import ReadAndWrite,DelInvaildTrans,SetPrecentData


def ProcessData():

    fromdate = ( date.today() + timedelta(days=0) ).strftime('%Y%m%d')
    todate = date.today().strftime('%Y%m%d')
    fromdate = '20201201'
    todate = '20211220'

    # ReadAndWrite(fromdate,todate)
    # DelInvaildTrans('JMJ',fromdate,todate)
    # period = '05'

    host='http://localhost:8080/'
    # host='http://101.200.55.5:8030/'
    company='JMJ'
    reportyear ='2021'
    rptcode1='2021'

    # read from yingyebu
    url = host +'jmj/readandwrite/?company='+company+'&fromdate='+fromdate+'&todate='+todate
    #requests.request(url=url,method='GET')
    #
    # url = host +'jmj/delinvaildtrans/?company='+company+'&fromdate='+fromdate+'&todate='+todate
    # requests.request(url=url,method='GET')

    # 初始化门店数据  每年1次
    #url = host +'jmj/initperioddata/?company='+company+'&reportyear='+reportyear+'&rptcode1='+rptcode1
    #requests.request(url=url,method='GET')

    #抓取营业部吉祥物销售数据，处理作废记录，重新计算库存数
    url= host+ 'goods/processgoods/?company=' +company +'&fromdate=' + fromdate + '&todate=' + todate
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req =urllib.request.Request(url=url,headers=headers)
    #urllib.request.urlopen(req)

    # periodlist = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28']
    periodlist = ['01','02']
    # periodlist=['']


    # periodlist=['01']
    for period in periodlist:
        print(period)
        #产生阶段性报表数据
        report = '1'
        url3= host+ 'jmj/SetPeriodIqty/?period=' + period +'&report=' + report
        print(period,url3)
        req =urllib.request.Request(url=url3,headers=headers)
        urllib.request.urlopen(req).read()

        #产生关键阶段报表数据
        report2 = '2'
        url6 = host+ 'jmj/SetPeriodIqty/?period=' + period + '&report=' + report2
        print(url6)
        req = urllib.request.Request(url=url6, headers=headers)
        html = urllib.request.urlopen(req).read()
        print(period,url6)

        url3= host+ 'jmj/SetPrecentData/?period=' + period
        print(period,url3)
        # req =urllib.request.Request(url=url3,headers=headers)
        # urllib.request.urlopen(req).read()

    return 'finished'

ProcessData()