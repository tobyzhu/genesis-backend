#coding = utf-8

from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import datetime
from django.core import serializers
from django.db.models import Avg,Sum,Count
import pymysql
import uuid


# Create your views here.
from jmj.models import ReportPeriod,PeriodData,OldData
from baseinfo.models import Appoption,Goods,Storeinfo,Wharehouse
from cashier.models import Expvstoll,Expense
from goods.models import Goodstranslog,Salehead,Saledtl
from adviser.views import sql_to_json,json_to_excel


class Report(object):
    def __init__(self):
        self.company = 'JMJ'
        self.fromdate = '20191201'
        self.todate = '20200701'
        self.reportyear = '2020'
        self.beforeyear = '2019'

    # 去年购买了该类商品，今年到店，但今年未购买该类商品的客户数量
    def report1(self):
        goodsrpt3s = Appoption.objects.filter(seg='goodsrpt3').values('itemname','itemvalues').order_by('itemname')
        for goodsrpt3 in goodsrpt3s:
            item = goodsrpt3['itemname']
            sql = " select a.storecode, g.rptcode1, getappoptionvalue(g.company,'goodsrpt1',g.rptcode1) rptname1, g.rptcode2,getappoptionvalue(g.company,'goodsrpt2',g.rptcode2) rptname2,"\
	              " g.rptcode3, getappoptionvalue(g.company,'goodsrpt3',g.rptcode3) rptname3, "\
                  "      count(distinct a.vipuuid) vipcnt "\
                  "  from expvstoll a, expense b, goods g "\
                  "  where 1=1  and a.valiflag='Y' and a.uuid = b.transuuid and b.srvcode=g.gcode "\
                  "  and a.vsdate>= '20181201' and a.vsdate<= '20190701' "\
                  "  and g.rptcode1= '2019' "\
                  "  and g.rptcode3 = %s" \
                  "  and a.vipuuid in ( "\
                  "          select distinct vipuuid from expvstoll  "\
                  "          where 1=1  "\
                  "          and valiflag = 'Y'   " \
                  "          and vsdate >= '20191201' " \
                  "          and vsdate <= '20200701' " \
                  "          ) "\
                  "  and a.vipuuid not in ( "\
                  "          select distinct a.vipuuid "\
                  "          from expvstoll a, expense b, goods g "\
                  "          where 1=1 "\
                  "          and a.valiflag='Y' "\
                  "          and a.uuid = b.transuuid "\
                  "          and b.srvcode=g.gcode "\
                  "          and a.vsdate>='20191201' "\
                  "          and a.vsdate<='20200701' "\
                  "          and g.rptcode1='2020' " \
                  "          and g.rptcode3 = %s" \
                  "      ) "\
                  "  group by a.storecode, g.rptcode1, g.rptcode2, g.rptcode3"

            params = (item + '  ' + item ).split()
            # print(sql, params)
            json_data = sql_to_json(sql, params)
            # print(item,type(item),json_data)
            filename = 'c:/tmp/'+goodsrpt3['itemvalues']+'_19年购买，20年到店未购买的客户数量.xls'
            json_to_excel(json_data,filename)
            # return json_data
            # return HttpResponse(json_data, content_type="application/json")



    # 老客户未到店客户中，去年即购买方位，又购买属相的客户数量
    # 马羊，属牛，龙鸡，狗兔，猴蛇，猪虎 每个单独统计
    def report2(self):
        goodsrpt3s = Appoption.objects.filter(seg='goodsrpt3',itemname__in=['301','302','303','304','305','306','307','308','309','310','311','312','313']).values('itemname','itemvalues')
        for goodsrpt3 in goodsrpt3s:
            item = goodsrpt3['itemname']
            sql = " select a.storecode, b.rptcode1,b.rptname1, b.rptcode2, b.rptname2, b.rptcode3,  b.rptname3,      count(distinct a.vipuuid) vipcnt    "\
                  "   from  (    "\
                  "      select distinct a.storecode, a.vipuuid , g.rptcode1, getappoptionvalue(g.company,'goodsrpt1',g.rptcode1) rptname1,  g.rptcode2, getappoptionvalue(g.company,'goodsrpt2',g.rptcode2) rptname2     "\
                  "      from expvstoll a, expense b, goods g     where 1=1   and a.valiflag='Y'   and a.uuid = b.transuuid    "\
                  "     and b.srvcode=g.gcode     and a.vsdate>= '20181201' and a.vsdate<= '20190701'    "\
                  "      and g.rptcode1= '2019'  and g.rptcode2 = '10'    "\
                  "      ) a,    "\
                  "      (    "\
                  "      select distinct a.storecode, a.vipuuid , g.rptcode1, getappoptionvalue(g.company,'goodsrpt1',g.rptcode1) rptname1,   g.rptcode2, getappoptionvalue(g.company,'goodsrpt2',g.rptcode2) rptname2,   g.rptcode3, getappoptionvalue(g.company,'goodsrpt3',g.rptcode3) rptname3    "\
                  "      from expvstoll a, expense b, goods g    "\
                  "      where 1=1    and a.valiflag='Y'   and a.uuid = b.transuuid and b.srvcode=g.gcode    "\
                  "      and a.vsdate>= '20181201' and a.vsdate<= '20190701'    "\
                  "     and g.rptcode1= '2019'  and g.rptcode3 = %s    "\
                  "      ) b     "\
                  "  where a.vipuuid = b.vipuuid    "\
                  "  and a.vipuuid not in (    "\
                  "          select distinct vipuuid from expvstoll    "\
                  "          where 1=1            and valiflag = 'Y'    "\
                  "          and vsdate >= '20191201'           and vsdate <= '20200701'    "\
                  "          )    "\
                  "  group by a.storecode, b.rptcode1, b.rptcode2, b.rptcode3"

            params = (item + '  ' ).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            print(item,type(item),json_data)
            filename = 'c:/tmp/'+goodsrpt3['itemvalues']+'_19年即购买方位又购买属相，20年未到店客户数量.xls'
            json_to_excel(json_data,filename)
            # return json_data
            # return HttpResponse(json_data, content_type="application/json")



def report1(request):
    report = Report()
    json_data = report.report1()

    return HttpResponse(200, content_type="application/json")
    # return HttpResponse(json_data, content_type="application/json")

def report2(request):
    report = Report()
    json_data = report.report2()

    return HttpResponse(200, content_type="application/json")