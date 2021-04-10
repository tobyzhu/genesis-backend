from django.shortcuts import render
import sys
import json
from django.http import HttpResponse
from xlwt import *
from rest_framework import serializers,viewsets,pagination
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from django.db import models
import uuid
import django.utils.timezone as timezone
import time,datetime
# from datetime import timedelta,datetime
from django.db.models import Q

# from .serializers import UserSerializer, GroupSerializer
from .serializers import CrmCaseSerializer,CrmCaseDetailSerializer,VipCaseDetailSerializer

from baseinfo.serializers import VipSerializer
from .models import Empl,CrmCase,CrmCaseDetail,Vip,VipCaseDetail
from adviser.views import sql_to_json

# Create your views here.

# @login_required()
# Create your models here.
from cashier.models import Expvstoll, Expense
from baseinfo.models import Goods,Empl,Serviece,Vip
import common.constants
import crm.crmsql

class mydate(object):
    def __init__(self):
        self.today = datetime.date.today()
        self.this_year = self.today.year
        self.this_year_s = str(self.this_year)
        self.this_month = self.today.month
        self.nextmonth = self.today.month + 1
        if self.today.month < 10:
            self.this_month_s =   '0'+str(self.today.month)
            self.nextmonth_s = str(self.today.month + 1)
        else:
            self.this_month_s = str(self.today.month)

        if self.today.month == 12:
            self.nextmonth_s =  '01'
            self.guduomonth_s = '02'
        else:
            self.nextmonth_s =  ('0'+ str(self.today.month +1))[:2]
            if self.today.month == 11:
                self.guduomonth_s ='01'
            else:
                self.guduomonth_s =  ('0'+ str(self.today.month + 2))[:2]

        self.this_day = self.today.day
        if self.today.day < 10:
            self.this_day_s =  '0'+str(self.today.day)
        else:
            self.this_day_s = str(self.today.day)

# 按会员特殊日期 产生计划性回访认为列表
def generatecrmcase_10_yiren(company):
    company='yiren'
    crmcase_month = ['10','20','30']

    thisdate = mydate()
    today = thisdate.today
    now = datetime.now()
    print('now',now)
    print('timedelta',now + datetime.timedelta(days=30))

    # 按照客户列表，产生阶段性的客服任务
    # vsdate = datetime.datetime.strptime(vipttypes[item]['vsdate'], '%Y%m%d')
    nextmonth =  datetime.datetime.strftime(today,'%Y%m')
    viplist = Vip.objects.filter(company=company,flag='LY',status='Y', valiflag='Y',ecode__isnull=False )
    for vip in viplist:
        print('vip.indate_month', vip.indate, vip.indate_month, vip.indate_day, vip.birth, vip.birth_month,
              vip.birth_day,vip.ecode_list)

        if vip.birth_month == thisdate.nextmonth_s :
            CASETYPE='10'
            PLANBEGINDATE = datetime.date(thisdate.this_year,thisdate.this_month,thisdate.this_day)
            PLANFINISHDATE =  datetime.date(thisdate.this_year,thisdate.this_month + 1,int(vip.birth_day))
            print('PLANFINISHDATE',PLANFINISHDATE)
            # empl = Empl.objects.get(company=vip.company,flag='Y',ecode=vip.ecode2)
            crmcase = CrmCase.objects.update_or_create(company=vip.company,  storecode=vip.storecode, casetype=CASETYPE,ecode=vip.ecode, vipuuid=vip,planbegindate=PLANBEGINDATE)[0]
            crmcase.viptype = vip.viptype
            crmcase.planfinishdate = PLANFINISHDATE
            crmcase.ecodelist = vip.ecode_list
            # crmcase.ecode = empl
            if crmcase.casedesc is None:
                crmcase.casedesc =  '生日回访'
            elif '生日回访' not in crmcase.casedesc :
                    crmcase.casedesc = crmcase.casedesc +'/'+'生日回访'
            else:
                print(vip, '生日回访已存在,skipped')
            crmcase.save()
            print('gerentatcrm birth',vip.vcode,vip.vname, vip.birth)

        if vip.birth_month == thisdate.guduomonth_s:
            CASETYPE='10'
            PLANBEGINDATE = datetime.date(thisdate.this_year,thisdate.this_month,thisdate.this_day)
            PLANFINISHDATE =  datetime.date(thisdate.this_year,thisdate.this_month + 2,int(vip.birth_day))
            try:
                # empl = Empl.objects.get(company=vip.company,flag='Y',ecode=vip.ecode2)
                crmcase = CrmCase.objects.update_or_create(company=vip.company, storecode=vip.storecode, casetype=CASETYPE,ecode=vip.ecode,  vipuuid=vip,planbegindate=PLANBEGINDATE)[0]
                crmcase.viptype = vip.viptype
                crmcase.planfinishdate = PLANFINISHDATE
                crmcase.ecodelist = vip.ecode_list
                # crmcase.ecode = empl
                if crmcase.casedesc is None:
                    crmcase.casedesc =  '骨朵月回访'
                elif '骨朵月回访' not in crmcase.casedesc :
                    crmcase.casedesc = crmcase.casedesc +'/'+'骨朵月回访'
                else:
                    print(vip,'骨朵月回访已存在,skipped')
                crmcase.save()
                print('gerentatcrm guduomonth_s',vip.vcode,vip.vname, vip.birth)
            except:
                print(vip ,'skipped')

        if vip.indate_month == thisdate.nextmonth_s:
            CASETYPE = '10'
            PLANBEGINDATE = datetime.date(thisdate.this_year, thisdate.this_month, thisdate.this_day)
            PLANFINISHDATE =  datetime.date(thisdate.this_year,thisdate.this_month + 1,int(vip.indate_day))
            try:
                # empl = Empl.objects.get(company=vip.company, flag='Y', ecode=vip.ecode2)
                crmcase = CrmCase.objects.update_or_create(company=vip.company, storecode=vip.storecode,casetype=CASETYPE, ecode=vip.ecode,  vipuuid=vip,
                                                 planbegindate=PLANBEGINDATE)[0]
                crmcase.viptype = vip.viptype
                crmcase.planfinishdate = PLANFINISHDATE
                crmcase.ecodelist = vip.ecode_list
                # crmcase.ecode = empl
                if crmcase.casedesc is None:
                    crmcase.casedesc = '缘分月回访'
                elif '缘分月回访' not in crmcase.casedesc:
                    crmcase.casedesc = crmcase.casedesc + '/' + '缘分月回访'
                else:
                    print(vip, '缘分月回访已存在,skipped')
                crmcase.save()
                print('gerentatcrm yuanfen_s', vip.vcode, vip.vname, vip.birth)
            except:
                print(vip, 'skipped')

            print('guduomonth_s',vip.vcode, vip.birth,vip.indate_month)



    return HttpResponse(200,content_type="application/json")
    # indate_viplist = Vip.objects.filter(company=company,valiflag='Y',indate__gte=nextmonth_firstdate,indate__lte=nextmonth_lastdate)



# 按照交易 产生计划性回访任务列表
def generatecrmcase_20_yiren(casetype,fromdate,todate):
    company='yiren'
    thisdate = mydate()
    today = thisdate.today
    now = datetime.now()
    if casetype == '20':
        CASETYPE = '20'
        tranx = Expvstoll.objects.filter(company=company, flag='Y', valiflag='Y',vsdate__gte=fromdate, vsdate__lte=todate)
        for tran in tranx:
            print(tran.vsdate, tran.exptxserno)
            vip = Vip.objects.get(company=company,uuid=tran.vipuuid)
            if tran.oldcustflag == '1':
                PLANBEGINDATE = now + datetime.timedelta(days=1)
                PLANFINISHDATE = now + datetime.timedelta(days=1)

                crmcase = CrmCase.objects.update_or_create(company=vip.company, storecode=vip.storecode, casetype=CASETYPE, ecode=vip.ecode,
                                                 vipuuid=vip, planbegindate=PLANBEGINDATE)[0]
                crmcase.viptype = vip.viptype
                crmcase.planfinishdate = PLANFINISHDATE
                crmcase.ecodelist = vip.ecode_list

                if crmcase.casedesc is None:
                    crmcase.casedesc =  '新客回访'
                elif '新客回访' not in crmcase.casedesc :
                        crmcase.casedesc = crmcase.casedesc +'/'+'新客回访'
                else:
                    print(vip, '新客已存在,skipped')
                crmcase.save()

            if tran.ttype == 'S':
                PLANBEGINDATE = now + datetime.timedelta(days=1)
                PLANFINISHDATE = now + datetime.timedelta(days=1)

                crmcase = CrmCase.objects.update_or_create(company=vip.company, storecode=vip.storecode, casetype=CASETYPE, ecode=vip.ecode,
                                                 vipuuid=vip, planbegindate=PLANBEGINDATE)[0]
                crmcase.viptype = vip.viptype
                crmcase.planfinishdate = PLANFINISHDATE
                crmcase.ecodelist = vip.ecode_list

                if crmcase.casedesc is None:
                    crmcase.casedesc =  '护理次日回访'
                elif '护理次日回访' not in crmcase.casedesc :
                        crmcase.casedesc = crmcase.casedesc +'/'+'护理次日回访'
                else:
                    print(vip, '护理次日回访已存在,skipped')
                crmcase.save()
                print('护理次日回访')

    return HttpResponse(200,content_type="application/json")


def getvipcase_yiren(request):
    company='yiren'
    crmcase_month = ['10','20','30']

    thisdate = mydate()
    today = thisdate.today

    # 按照客户列表，产生阶段性的客服任务
    # vsdate = datetime.datetime.strptime(vipttypes[item]['vsdate'], '%Y%m%d')
    nextmonth =  datetime.datetime.strftime(today,'%Y%m')
    viplist = Vip.objects.filter(company=company,flag='Y',status='Y', valiflag='Y',ecode__isnull=False )
    for vip in viplist:
        print('vip.indate_month',vip.indate_month)
        if vip.birthmonth == thisdate.nextmonth_s :
            CASETYPE='10'
            PLANBEGINDATE = datetime.date(thisdate.this_year,thisdate.this_month,thisdate.this_day)
            empl = Empl.objects.get(company=vip.company,flag='Y',ecode=vip.ecode)
            vipcasedetail = VipCaseDetail.objects.get_or_create(company=vip.company,storecode=vip.storecode,casetype=CASETYPE,nextecode=vip.ecode,vipuuid=vip,nextdate=PLANBEGINDATE)[0]
            if vipcasedetail.detail is None:
                vipcasedetail.detail =  '生日回访'
            elif '生日回访' not in vipcasedetail.detail :
                vipcasedetail.detail = vipcasedetail.detail +'/'+'生日回访'
            else:
                print(vip, '生日回访已存在,skipped')

            vipcasedetail.save()

            print('gerentatcrm birth',vip.vcode,vip.vname, vip.birth)

        if vip.birthmonth == thisdate.guduomonth_s:
            CASETYPE='10'
            PLANBEGINDATE = datetime.date(thisdate.this_year,thisdate.this_month,thisdate.this_day)
            try:
                empl = Empl.objects.get(company=vip.company,flag='Y',ecode=vip.ecode)
                vipcasedetail = VipCaseDetail.objects.get_or_create(company=vip.company, storecode=vip.storecode, casetype=CASETYPE,
                                                                    nextecode=vip.ecode, vipuuid=vip, nextdate=PLANBEGINDATE)[0]
                if vipcasedetail.detail is None:
                    vipcasedetail.detail = '骨朵月回访'
                elif '骨朵月回访' not in vipcasedetail.detail:
                    vipcasedetail.detail = vipcasedetail.detail + '/' + '骨朵月回访'
                else:
                    print(vip, '骨朵月回访已存在,skipped')
                vipcasedetail.save()

                print('gerentatcrm guduomonth_s',vip.vcode,vip.vname, vip.birth)
            except:
                print(vip ,'skipped')

        if vip.indate_month == thisdate.nextmonth_s:
            CASETYPE = '10'
            PLANBEGINDATE = datetime.date(thisdate.this_year, thisdate.this_month, thisdate.this_day)
            try:
                empl = Empl.objects.get(company=vip.company, flag='Y', ecode=vip.ecode)
                vipcasedetail = VipCaseDetail.objects.get_or_create(company=vip.company, storecode=vip.storecode, casetype=CASETYPE,
                                                                    nextecode=vip.ecode, vipuuid=vip, nextdate=PLANBEGINDATE)[0]
                if vipcasedetail.detail is None:
                    vipcasedetail.detail = '缘分月回访'
                elif '缘分月回访' not in vipcasedetail.detail:
                    vipcasedetail.detail = vipcasedetail.detail + '/' + '缘分月回访'
                else:
                    print(vip, '缘分月回访已存在,skipped')
                vipcasedetail.save()


                print('gerentatcrm yuanfen_s', vip.vcode, vip.vname, vip.birth)
            except:
                print(vip, 'skipped')

            print('guduomonth_s',vip.vcode, vip.birth,vip.indate_month)


    # 按照交易，产生相应客服任务

    #print('viplist',viplist)

    # tranx = Expvstoll.objects.filter(company=company,flag='Y',valiflag='Y')
    # for tran in tranx:
    #     CASETYPE = '20'
    #     PLANBEGINDATE = datetime.timedelta(datetime.date(tran.vsdate), days = 1)
    #     try:
    #         empl = Empl.objects.get(company=vip.company, flag='Y', ecode=tran.vipuuid.ecode)
    #         vip = tran.vipuuid
    #         crmcase = CrmCase.objects.update_or_create(company=vip.company, storecode=tran.storecode, casetype=CASETYPE, empl=empl, vipuuid=vip,
    #                                                    planbegindate=PLANBEGINDATE)[0]
    #         crmcase.viptype = vip.viptype
    #         # crmcase.ecode = empl
    #         if crmcase.casedesc is None:
    #             crmcase.casedesc = '次日回访'
    #         elif '次日回访' not in crmcase.casedesc:
    #             crmcase.casedesc = crmcase.casedesc + '/' + '次日回访'
    #         else:
    #             print(vip, '次日回访已存在,skipped')
    #         crmcase.save()
    #         print('gerentatcrm nextday', vip.vcode, vip.vname, vip.birth)
    #     except:
    #         print(vip, 'skipped')

    return HttpResponse(200,content_type="application/json")
    # indate_viplist = Vip.objects.filter(company=company,valiflag='Y',indate__gte=nextmonth_firstdate,indate__lte=nextmonth_lastdate)



def getcrmcase_yiren(request):
    company = request.GET['company']
    thisdate = mydate()
    today = thisdate.today
    now = datetime.now()
    fromdate = datetime.date.strptime(now,'%Y%m%d')
    todate = datetime.date.strptime(now,'%Y%m%d')

    generatecrmcase_10_yiren(company)
    generatecrmcase_20_yiren(company,fromdate,todate)


    return HttpResponse(200,content_type="application/json")

