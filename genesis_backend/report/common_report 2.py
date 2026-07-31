from django.shortcuts import render
import datetime,time
from django.db.models import Avg,Count,Sum,F,Max
import json
from django.http import HttpResponse,StreamingHttpResponse
from django.db.models import Q,F
import uuid
import numpy as np
import pandas as pd
import os
import genesis.settings as settings

# Create your views here.
#from .models import DailyReportNo1,ReportClassData
from cashier.models import Expvstoll,Expense,Toll
from adviser.models import Cardinfo
from adviser.views import *
from baseinfo.models import *  #Appoption,Storeinfo,Vip,Cardtype,Serviece,Goods,Paymode,Empl
from goods.models import Goodstranslog
from baseinfo.models import BRAND,MARKETCLASS1,MARKETCLASS2,MARKETCLASS3,MARKETCLASS4,FINANCECLASS1,FINANCECLASS2,ARCHIVEMENTCLASS1,ARCHIVEMENTCLASS2
from common.models import *
from wechat.models import *
import common.constants
from report.views import CardinfoData
from matplotlib import pyplot as plt

class GenesisDate(object):
    def __init__(self,**kwargs):
        self.today = datetime.date.today()
        self.today_string_8 = datetime.datetime.today().strptime('')


    def get_lastmonthlist(self,**kwargs):
        reportdate = kwargs.get('reportdate','20210101')
        num = kwargs.get('num', 0)
        lastmonthlist=[]
        reportdate_date = datetime.datetime.strptime(reportdate,'%Y%m%d').date()
        reportyear = reportdate.year
        for i  in range[1, int(self.num) + 1]:
            month = reportdate.month - 1
            if month == 0:
                year= reportyear -1
                month=12
                # monthlist = monthlist.append(str(year) + str(month))
            if month in [1,2,3,4,5,6,7,8,9]:
                lastmonthlist.append(str(year)+'0'+str(month))
            else:
                lastmonthlist.append(str(year)  + str(month))
        print('lastmonthlist',month, lastmonthlist)
        return lastmonthlist


class StoreReport(object):
    def __init__(self, **kwargs):
        self.default_fromdate = ''
        self.default_todate = ''
        self.company = kwargs.get('company', 'yiren')
        self.storelist = kwargs.get('storecode', '01,02,03,04').split(',')
        self.fromdate = kwargs.get('fromdate', self.default_fromdate)
        self.todate = kwargs.get('todate', self.default_todate)


        self.TRANXS = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, flag='Y', valiflag='Y',
                                          vsdate__gte=self.fromdate, vsdate__lte=self.todate)
        print('init data',self.fromdate,self.todate,self.company,self.storelist,type(self.storelist),self.TRANXS)

    def vipcnt_bydate(self):
        vipcnt_bydate = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                          vsdate__lte=self.todate, valiflag='Y', flag='Y'). \
            values('storecode', 'vsdate').annotate(vipcnt=Count('vipuuid', distinct=True)).distinct().order_by(
            'storecode', '-vsdate')
        vipcnt_bydate_df = pd.DataFrame(vipcnt_bydate, columns=['storecode', 'vsdate', 'vipcnt'])
        return vipcnt_bydate_df

    def vipcnt(self):
        vipcnt = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                          vsdate__lte=self.todate, valiflag='Y', flag='Y'). \
            values('storecode').annotate(vipcnt=Count('vipuuid', distinct=True)).distinct().order_by('storecode')
        vipcnt_df = pd.DataFrame(vipcnt, columns=['storecode', 'vipcnt'])
        return vipcnt_df

    def viptimes_bydate(self):
        viptimes_bydate = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                          vsdate__lte=self.todate, valiflag='Y', flag='Y'). \
            values('storecode', 'vsdate').annotate(vipcnt=Count('vipuuid', distinct=True)).distinct().order_by(
            'storecode', '-vsdate')
        viptimes_bydate_df = pd.DataFrame(viptimes_bydate, columns=['storecode', 'vsdate', 'vipcnt'])
        return viptimes_bydate_df

    def viptimes(self):
        viptimes = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                          vsdate__lte=self.todate, valiflag='Y', flag='Y'). \
            values('storecode').annotate(vipcnt=Count('vipuuid', distinct=True)).distinct().order_by('storecode')
        viptimes_df = pd.DataFrame(viptimes, columns=['storecode', 'vipcnt'])
        return viptimes_df

    def newvipcnt_bydate(self):
        newvipcnt_bydate = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                             vsdate__lte=self.todate, oldcustflag='1').values('storecode', 'vsdate'). \
            annotate(newvipcnt=Count('vipuuid', distinct=True)).distinct()
        newvipcnt_bydate_df = pd.DataFrame(list(newvipcnt_bydate), columns=['storecode', 'vsdate', 'newvipcnt'])
        return newvipcnt_bydate_df

    def newvipcnt(self):
        newvipcnt = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, vsdate__gte=self.fromdate,
                                             vsdate__lte=self.todate, oldcustflag='1').values('storecode', 'vsdate'). \
            annotate(newvipcnt=Count('vipuuid', distinct=True)).distinct()
        newvipcnt_df = pd.DataFrame(list(newvipcnt), columns=['storecode', 'newvipcnt'])
        return newvipcnt_df

    def pm_vipcnt_bydate(self):
        pm_vipcnt_bydate = Expense.objects.filter(flag='Y', transuuid__company=self.company,transuuid__storecode__in=self.storelist,transuuid__vsdate__gte=self.fromdate,
                                               transuuid__vsdate__lte=self.todate,transuuid__valiflag='Y').values('storecode','transuuid__vsdate','pmcode').annotate(vipcnt_bydate=Count('transuuid_vipuuid',distinct=True))
        pm_vipcnt_bydate_df = pd.DataFrame(list(pm_vipcnt_bydate), columns=['storecode','transuuid__vsdate','pmcode', 'vipcnt_bydate'])
        pm_vipcnt_bydate_df.rename(columns={'transuuid__vsdate':'vsdate','pmcode':'ecode'}, inplace = True)
        return pm_vipcnt_bydate_df

    def sec_vipcnt_bydate(self):
        sec_vipcnt_bydate = Expense.objects.filter(flag='Y', transuuid__company=self.company,transuuid__storecode__in=self.storelist,transuuid__vsdate__gte=self.fromdate,
                                               transuuid__vsdate__lte=self.todate,transuuid__valiflag='Y').values('storecode','transuuid__vsdate','asscode1').annotate(vipcnt_bydate=Count('transuuid_vipuuid', distinct=True))
        sec_vipcnt_bydate_df = pd.DataFrame(list(sec_vipcnt_bydate),
                                           columns=['storecode', 'transuuid__vsdate', 'asscode1', 'vipcnt_bydate'])
        sec_vipcnt_bydate_df.rename(columns={'transuuid__vsdate':'vsdate','asscode1':'ecode'}, inplace = True)
        return sec_vipcnt_bydate_df

    def thr_vipcnt_bydate(self):
        thr_vipcnt_bydate =Expense.objects.filter(flag='Y', transuuid__company=self.company,transuuid__storecode__in=self.storelist,transuuid__vsdate__gte=self.fromdate,
                                               transuuid__vsdate__lte=self.todate,transuuid__valiflag='Y').values('storecode','transuuid__vsdate', 'asscode1').\
            annotate(thr_vipcnt_bydate=Count('transuuid_vipuuid', distinct=True))
        thr_vipcnt_bydate_df = pd.DataFrame(list(thr_vipcnt_bydate),
                                            columns=['storecode', 'transuuid__vsdate', 'asscode1', 'newvipcnt'])
        thr_vipcnt_bydate_df.rename(columns={'transuuid__vsdate': 'vsdate', 'asscode1': 'ecode'}, inplace=True)
        return thr_vipcnt_bydate_df

    def amount_bydate(self):
        amount_bydate = Expense.objects.filter(flag='Y', transuuid__company=self.company,transuuid__storecode__in=self.storelist,transuuid__vsdate__gte=self.fromdate,
                                               transuuid__vsdate__lte=self.todate,transuuid__valiflag='Y').values('storecode','transuuid__vsdate').\
            annotate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount=Sum(F('s_mount')*F('cardratio')),sendamount=Sum(F('s_mount')*F('sendratio')))
        print('amount_bydate',amount_bydate.query,amount_bydate)
        amount_bydate_df = pd.DataFrame(list(amount_bydate),columns=['storecode','transuuid__vsdate','cashamount','cardamount','sendamount'])
        print('amount_bydate_df',amount_bydate_df)
        return amount_bydate_df

    def amount_byttype_date(self):
        amount_byttype_date = Expense.objects.filter(flag='Y', transuuid__company=self.company,
                                               transuuid__storecode__in=self.storelist,
                                               transuuid__vsdate__gte=self.fromdate,
                                               transuuid__vsdate__lte=self.todate, transuuid__valiflag='Y').values(
            'storecode', 'transuuid__vsdate','ttype'). \
            annotate(cashamount=Sum(F('s_mount') * F('cashratio')), cardamount=Sum(F('s_mount') * F('cardratio')),
                     sendamount=Sum(F('s_mount') * F('sendratio')))
        print('amount_bydate', amount_bydate.query, amount_bydate)
        amount_byttype_date_df = pd.DataFrame(list(amount_byttype_date),
                                        columns=['storecode', 'transuuid__vsdate','ttype', 'cashamount', 'cardamount',
                                                 'sendamount'])
        print('amount_byttype_date_df', amount_byttype_date_df)
        return amount_byttype_date_df

    # def CI_cardsuptype_bydate(self):

    # def empl_archivement_sum(self):

def amount_bydate(request):
    params = {
        'company': 'yiren',
        'storelist': '01,02,03,04',
        'fromdate': '20200101',
        'todate': '20200401'
    }
    report = StoreReport(**params)
    data_df = report.amount_bydate()

    return HttpResponse('200', content_type="application/json")

def get_carddata(request):
    params = {
        'company': 'yfy',
        'storecode':'01',
        'cardinfouuid':'ee9f4dc69baf11e9974f00163e08811c',
        'storelist': '01,02,03,04',
        'fromdate': '2021-01-01',
        'todate': '2021-06-01'
    }
    report = CardinfoData(**params)
    # data_df = report.get_date_leftmoney()
    # print('data_df',data_df)
    # print('json_data',json.dumps(data_df))

    # data_df2 = report.get_total_leftmoney()
    # print('data_df',data_df2)

    misstrans= report.check_data()
    print('data_df',misstrans)

    return HttpResponse('200', content_type="application/json")

class EmplReport(object):
    def __init__(self, **kwargs):
        self.default_fromdate = ''
        self.default_todate = ''
        self.company = kwargs.get('company', 'yiren')
        self.storelist = kwargs.get('storecode', '01,02,03,04').split(',')
        self.fromdate = kwargs.get('fromdate', self.default_fromdate)
        self.todate = kwargs.get('todate', self.default_todate)
        self.ecode = kwargs.get('ecode','')


        self.TRANXS = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, flag='Y', valiflag='Y',
                                          vsdate__gte=self.fromdate, vsdate__lte=self.todate)
        self.trans = Expense.objects.filter(company=self.company,storecide__in=self.storelist,flag='Y',
                                            transuuid__flag='Y',transuuid__valiflag='Y',vsdate__gte=self.fromdate,vsdate__lte=self.todate)
        self.empl_pm_trans = self.trans.filter(pmcode=self.ecode)
        self.empl_sec_trans = self.trans.filter(asscode1=self.ecode)
        self.empl_thr_trans = self.trans.filter(asscode2=self.ecode)
        self.genesisdate= GenesisDate()


        print('init data',self.fromdate,self.todate,self.company,self.storelist,type(self.storelist),self.trans)

    def get_month(self,reportdate):
        self.reportmonth= self.reporttdate[:6]
        self.reportmonth = ['202008','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107']
        # self.last_three_month = self.genesisdate(reportdate,3)
        self.last_three_month =['202005','202006','202007']
        # self.last_six_month = self.genesisdate(reportdate,6)
        self.last_six_month = ['202002','202003','202004','202005','202006','202007']

    def get_empllist(self):
        empltrans = self.empl_sec_trans | self.empl_thr_trans

    # 计算每个美疗师，每个个月份所分配到的护理师的数量
    # 以会员资料建立日期作为评判是否计算的一个条件
    def get_empl_vip_cnt_by_month(self):
        for month in self.reportmonth:
            last_create_time = datetime.datetime.strptime(month+'01','%Y%m%d')
            empl_vip_cnt = Vip.objects.filter(flag='Y',company=self.company,valiflag='Y',create_time__lte=last_create_time).values('storecode','ecode2').annotate(vipcnt=Count('uuid'))
            emplcnt_df = pd.DataFrame(empl_vip_cnt, columns=[month,'storecode', 'ecode', 'vipcnt'])
            print('emplcnt_df',emplcnt_df)

        return emplcnt_df


# def test():
#     genesisdate= GenesisDate()
#     genesisdate.get_lastmonthlist(reportdate='20200801',num=3)
#
# test()