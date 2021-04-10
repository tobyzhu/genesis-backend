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
from django.db.models import Q

# from .serializers import UserSerializer, GroupSerializer
from .serializers import CrmCaseSerializer,CrmCaseDetailSerializer,VipCaseDetailSerializer
from baseinfo.serializers import VipSerializer
from .models import Empl,CrmCase,CrmCaseDetail,Vip,VipCaseDetail,CrmSubReport,CrmInfoItem,CrmInfoItemChoice
from adviser.views import sql_to_json

# Create your views here.

# @login_required()
# Create your models here.
from cashier.models import Expvstoll, Expense
from baseinfo.models import Goods,Empl,Serviece,Vip
import common.constants
import crm.crmsql

class VipCaseDetailViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = VipCaseDetail.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('create_time')
    serializer_class = VipCaseDetailSerializer

class CrmCaseViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset =  CrmCase.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('planbegindate')
    serializer_class = CrmCaseSerializer


class CrmCaseDetailViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = CrmCaseDetail.objects.filter(company=common.constants.COMPANYID)
    serializer_class = CrmCaseDetailSerializer

@csrf_exempt
def AddCrmCaseDetail(request):
    if request.method=='POST':
        req = json.loads(request.body.decode())
        company = req.get('company')
        storecode = req.get('storecode')
        crmcaseid= req.get('caseid')
        detaildescription = req.get('detaildescription')
        ecode = req.get('ecode')
    if company == None:
        company = common.constants.COMPANYID
    if storecode == None:
        storecode = '000'

    try:
        crmcase = CrmCase.objects.get(uuid=crmcaseid)
    except:
        return HttpResponse('No this crm case!')
    print('request info ',company,storecode, crmcaseid,detaildescription,ecode)
    crmcasedetail = CrmCaseDetail.objects.create(company=company,storecode=storecode,caseid=crmcase,detaildescription=detaildescription)
    return HttpResponse('OK!')

@csrf_exempt
def UpdateCrmCaseDetail(request):
    # print(request)
    if request.method=='PUT':
        req = json.loads(request.body.decode())
        print(req)

        company = req.get('company')
        storecode = req.get('storecode')
        crmcasedetailuuid= req.get('crmcasedetailuuid')
        detaildescription = req.get('detaildescription')
        ecode = req.get('ecode')

    if company == None:
        company = common.constants.COMPANYID

    if storecode == None:
        storecode = '000'
        # return  HttpResponse('The storecode is need!')

    try:
        crmcasedetail = CrmCaseDetail.objects.get(uuid=crmcasedetailuuid)
        crmcasedetail.detaildescription = detaildescription
        crmcasedetail.save()
        return HttpResponse('OK!')
    except:
        return HttpResponse('No this crm case detail!')

    return HttpResponse('OK!')

class VipViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Vip.objects.filter(company='JMJ').order_by('viptype','vcode')
    serializer_class = VipSerializer

def generatecrmcase(request):
    ps_date = request.GET['ps_date']
    srvintervaldays=7
    goodsintervaldays=30

    vipttypes =  Expvstoll.objects.filter(Q(vsdate=ps_date),Q(ttype='S')|Q(ttype='G')).values('company','storecode','vsdate','vipuuid','ttype').distinct()
    for item in range(len(vipttypes)):
        print(item)

        company = vipttypes[item]['company']
        storecode = vipttypes[item]['storecode']
        vsdate = datetime.datetime.strptime( vipttypes[item]['vsdate'],'%Y%m%d')
        vipuuid = vipttypes[item]['vipuuid']
        vip = Vip.objects.get(uuid=vipuuid)
        viptype = vip.viptype

        if vipttypes[item]['ttype']=='S':
            casetype='40'
            planbegindate = vsdate + datetime.timedelta(days=+srvintervaldays)
            casedesc = vip.vname +'服务回访'
        elif vipttypes[item]['ttype']=='G':
            casetype='45'
            planbegindate = vsdate + datetime.timedelta(days=+goodsintervaldays)
            casedesc = vip.vname +'购买商品回访'
        else:
            casetype='48'


        ecode = vip.ecode
        ecode2 = vip.ecode2
        print('vip=',vip.vname, vip.vcode,'ecode=',ecode, 'ecode2=',ecode2)
        if ecode == None:
            print(vip.vname, "do not set ecode")
        else:
            # try:
                print('company=',company,'storecode=',storecode,'casetype=',casetype,'vsdate=',vsdate,'ecode=',ecode)
                empl = Empl.objects.get(company=company,storecode=storecode,ecode=ecode)
                print('company=',company,'storecode=',storecode,'casetype=',casetype,'vsdate=',vsdate,'empl=',empl)
                crmcase = CrmCase.objects.get_or_create(company=company,storecode=storecode,casetype=casetype,vipuuid=vip,vsdate=vsdate,ecode=empl)[0]
                print('crmcase',crmcase)
                crmcase.status ='10'
                crmcase.planbegindate = planbegindate
                crmcase.casedesc = casedesc
                crmcase.save()
                print(viptype,vip.uuid, vip.vname,vsdate,casetype, empl.ename,'is created ')
            # except:
            #     # crmcase = CrmCase.objects.create(casetype=casetype,vipuuid=vipuuid,vsdate=vsdate,ecode=empl)
            #     # crmcase.
            #     print(viptype, vip.uuid,vip.vname, vsdate, casetype, 'already exists!')
            #     print("skip")


        if ecode2 == None:
            print("skipped")
            print(vip.vname, "do not set ecode2")
        else:
            try:
                empl2 = Empl.objects.get(company=company,storecode=storecode,ecode=ecode)
                crmcase = CrmCase.objects.get_or_create(company=company,storecode=storecode,casetype=casetype,vipuuid=vip,vsdate=vsdate,ecode=empl2)
                crmcase.status ='10'
                crmcase.planbegindate = planbegindate
                crmcase.casedesc = casedesc
                crmcase.save()
                print(viptype, vip.uuid,vip.vname, vsdate, casetype, empl2.ename,'is created ')
            except:
                # crmcase = CrmCase.objects.create(casetype=casetype,vipuuid=vipuuid,vsdate=vsdate,ecode=empl)
                # crmcase.
                print(viptype,vip.uuid, vip.vname, vsdate, casetype, 'already exists!')
                print("skip")


    return HttpResponse(0)


def update_crmcase(request):
    company=request.GET.get('company')
    storecode=request.GET.get('storecode')
    crmcaseuuid_s = request.GET.get('crmcaseuuid').replace('-','')
    crmcaseuuid = uuid.UUID(crmcaseuuid_s)
    try:
        crmcase_status = request.GET.get('status')
    except:
        crmcase_status =''
    print('tt',crmcaseuuid_s,crmcaseuuid,crmcase_status)

    try:
        crmcase = CrmCase.objects.get(company=company,uuid=crmcaseuuid)
        print('crmcase',crmcase.casedesc)
        # crmcase_status = crmcase.status
    except:
        print('error')
        # crmcase  = CrmCase.objects.create(uuid=crmcase_uuid)
        return HttpResponse('500', content_type="application/json")
    if crmcase_status =='' :
        crmcase_status = crmcase.status
    crmcase.status = crmcase_status
    crmcase.save()
    return HttpResponse('200', content_type="application/json")




def get_vipcasedetail_byvipuuid(request):
    company = request.GET.get('company','demo')
    print('company=',company)
    vipuuid = request.GET.get('vipuuid','').replace('-','')
    print('vipuuid=',vipuuid)

    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,status"\
          "  from vipcasedetail a"\
          "  where 1=1 and a.flag='Y' "\
          "  and a.company = %s AND a.vipuuid = %s " \
          "  order by a.create_time desc  "\

    params =  (company+' '+ vipuuid  ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_planvipcasedetail_byecode(request):
    company = request.GET.get('company','demo')
    print('company=',company)
    try:
        vipuuid = request.GET.get('vipuuid','').replace('-','')
        print('vipuuid=',vipuuid)
    except:
        vipuuid=''

    try:
        nextecode=request.GET.get('ecode','')
    except:
        nextecode=''

    nextdate_s = request.GET.get('nextdate','')
    print('nextdate_s',nextdate_s)
    nextdate = datetime.datetime.strptime(nextdate_s,'%Y-%m-%d')
    print('nextdate',nextdate)

    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,a.status," \
          "  a.vipuuid, b.vcode,b.vname, b.mtcode "\
          "  from vipcasedetail a, vip b"\
          "  where 1=1 and a.flag='Y' and b.flag='Y' " \
          "  and a.company=b.company and a.vipuuid = b.uuid"\
          "  and a.company = %s AND a.nextecode = %s  and nextdate=date(%s)" \
          "  order by a.create_time desc  "\

    params =  (company+' '+ nextecode +' '+ nextdate_s ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_vipcasedetail(request):
    uuid = request.GET.get('uuid')
    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,status"\
          "  from vipcasedetail a"\
          "  where 1=1 and a.flag='Y' "\
          "  and a.uuid = %s  " \
          "  order by a.create_time desc  "\

    params =  (uuid  ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def update_vipcasedetail(request):
    uuid = request.GET.get('uuid').replace('-','')
    company=request.GET.get('company')
    storecode=request.GET.get('storecode')
    ecode =request.GET.get('ecode')
    casetype = request.GET.get('casetype')
    detail = request.GET.get('detail')
    vipuuid = request.GET.get('vipuuid').replace('-','')
    try:
        nextdate = request.GET.get('nextdate')
    except:
        nextdate= None

    try:
        nextecode=request.GET.get('nextecode')
    except:
        nextecode=''


    if len(uuid)==32:
        vipcasedetail = VipCaseDetail.objects.get(uuid=uuid)
        vipcasedetail.ecode=ecode
        vipcasedetail.casetype=casetype
        vipcasedetail.detail=detail
        vipcasedetail.last_modified=datetime.datetime.now()
        vipcasedetail.creater=ecode
        vipcasedetail.nextdate=nextdate
        vipcasedetail.nextecode=nextecode
        vipcasedetail.status='20'

        vipcasedetail.save()
        return HttpResponse('200', content_type="application/json")
    else:
        try:
            vip = Vip.objects.get(company=company,uuid=vipuuid)
            vipcasedetail = VipCaseDetail.objects.create(company=company,storecode=storecode,creater=ecode,ecode=ecode,flag='Y',vipuuid=vip,detail=detail,
                                                         nextdate=nextdate,nextecode=nextecode,status='20')
            return HttpResponse('200', content_type="application/json")
        except:
            # raise ValueError;
            return HttpResponse('500', content_type="application/json")

def get_crmcaselist(request):
    bytype = request.GET['bytype']
    company = request.GET['company']
    storecode = request.GET['storecode']
    status = request.GET['status']

    if bytype =='vipcrmcase':
        vipuuid = request.GET['vipuuid']
        if company in common.constants.COMPANYLIST_WITHOUT_MTCODE:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, '' mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename, a.status status, finishedate, planbegindate, planfinishdate,casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s  and a.status=%s and a.vipuuid=%s" \
                  " order by casetype, planfinishdate"

        else:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, c.mtcode mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename, a.status status, finishedate, planbegindate, planfinishdate,casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s  and a.status=%s and a.vipuuid=%s" \
                  " order by casetype, planfinishdate"

        params =  (company+' '+ storecode + ' ' + status+ ' '+ vipuuid).split()
        print(sql,params)
        json_data = sql_to_json(sql,params)
        print(json_data)
        return HttpResponse(json_data, content_type="application/json")

    if bytype =='crmcase':
        ecode = request.GET['ecode']
        planbegindate = request.GET['planbegindate']
        if company in common.constants.COMPANYLIST_WITHOUT_MTCODE:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, '' mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename," \
                  " a.status status, finishedate, planbegindate,planfinishdate, casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s and a.ecodelist like  concat('%%',%s,'%%') and a.planbegindate <= %s and a.planfinishdate >= %s and a.status=%s" \
                  " order by casetype, planfinishdate"
        else:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, c.mtcode mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename," \
                  " a.status status, finishedate, planbegindate,planfinishdate, casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s and a.ecodelist like  concat('%%',%s,'%%') and a.planbegindate <= %s and a.planfinishdate >= %s and a.status=%s" \
                  " order by casetype, planfinishdate"
        params =  (company+' '+ storecode +' ' + ecode +'  ' + planbegindate +' ' + planbegindate + ' '+ status).split()
        print(sql,params)
        json_data = sql_to_json(sql,params)
        # print(json_data)
        return HttpResponse(json_data, content_type="application/json")

def get_vipconsumelist(request):
    company = request.GET['company']
    vipuuid = request.GET['vipuuid'].replace('-','')
    try:
        fromdate = request.GET['fromdate']
    except:
        fromdate = '20180101'

    try:
        todate = request.GET['todate']
    except:
        todate = '20991231'
    fromdate='201801011'
    todate='20991231'

    sql = "  select a.uuid transuuid, a.ccode ccode, getcardtypename(getcardtype(a.ccode,a.company),a.company) cardname, a.vsdate vsdate, "\
          "  f_getnamebysrvcode(b.srvcode, b.ttype, b.company) itemname, b.s_qty s_qty, b.s_price s_price, b.SECDISC secdisc, "\
          "  b.s_mount amount, b.pmcode pmcode, b.ASSCODE1 seccode, b.ASSCODE2 thrcode, "\
          "  getemplinfo(a.company,b.pmcode,'ename') pmname,getemplinfo(a.company,b.asscode1,'ename') secname, getemplinfo(a.company,b.asscode2,'ename') thrname,"\
          " ( case b.ttype when 'S' then '服务' when 'G' then '商品' when 'C' then '售卡' when 'I' then '充值' else '其他' end ) ttype," \
          " ( case b.stype when 'N' then '正常' when 'P' then '赠送' else '其他' end ) stype ,Getexptxpaydesc2(a.uuid, a.storecode, a.company) exptxpaydesc" \
          "  from expvstoll a, expense b, vip c"\
          "  where 1=1 and a.valiflag='Y' "\
          "  and a.uuid = b.transuuid and a.vipuuid = c.uuid"\
          "  and a.company = %s AND a.vipuuid = %s and vsdate between %s and %s" \
          "  order by a.vsdate desc, a.ccode "

    params =  (company+' '+ vipuuid +' ' + fromdate +'  ' + todate ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    print(json_data)
    return HttpResponse(json_data, content_type="application/json")



def get_vip_crmcasedetail(request):
    company = request.GET['company']
    vipuuid = request.GET['vipuuid']
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']

    sql = " SELECT b.uuid crmcasedetailuuid, c.vcode, c.vname, b.storecode storeocode, casetype, a.status casestatus, planbegindate,planfinishdate, finishedate, casedesc, b.create_time,b.creater, detaildescription "\
            " FROM crmcase a, crmcasedetail b, vip c, empl d "\
            " where a.uuid = b.caseid_id and a.vipuuid = c.uuid and a.ecode = d.ecode "\
            " and a.company=d.company and a.company = %s and a.vipuuid = %s "\
            " order by b.create_time"

    params =  (company+' '+ vipuuid  ).split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_crmcasedetail_bycaseid(request):
    company = request.GET['company']
    uuid = request.GET['uuid']
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']

    sql = "   SELECT a.uuid crmcaseuuid, a.vipuuid vipuuid, a.casedesc, b.uuid uuid,  b.create_time,b.creater, detaildescription ,c.vname vname"\
            " FROM crmcase a, crmcasedetail b, vip c"\
            " where 1=1 and a.uuid = b.caseid_id AND a.vipuuid = c.uuid"\
            " and a.company = %s and b.uuid = %s "\
            " order by b.create_time"

    params =  (company+' '+ uuid  ).split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_viplist_bycrmrptid(request):
    # datedelta = datetime.datedelta(days=-7)
    delta = datetime.timedelta(days=-90)
    now = datetime.datetime.now()
    defaultfromdate = datetime.datetime.strftime((now + delta),'%Y%m%d')
    defaulttodate = datetime.datetime.strftime( now  ,'%Y%m%d')

    try:
        company=request.GET['company']
    except:
        company=''

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        fromdate=request.GET['fromdate'].replace('-','')
        if len(fromdate)==0:
            fromdate=defaultfromdate

    except:
        fromdate=defaultfromdate

    try:
        todate = request.GET['todate'],replace('-','')
        if len(todate)==0:
            todate=defaulttodate
    except:
        todate =defaulttodate

    try:
        minileftmoney = request.GET['minileftmoney']
    except:
        minileftmoney= 0

    try:
        maxleftmoney = request.GET['maxleftmoney']
    except:
        maxleftmoney= 5000

    try:
        ecode = request.GET['ecode']
    except:
        ecode=''

    try:
        crmrptid = request.GET['crmrptid']
    except:
        crmrptid ='1'
    print('crmrptid=',crmrptid)

    if crmrptid == '1'  :
        sql = crm.crmsql.CRM_SQL101
        print('sql=',sql)
        params = (company+'  '+ storecode +'  '+ fromdate +'  '+ todate+' '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)

        return HttpResponse(json_data, content_type="application/json")

    if crmrptid =='2':
        sql = crm.crmsql.CRM_SQL102
        params = (company+'  '+ storecode +'  '+ fromdate +'  '+ todate+' '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '3':
        sql = crm.crmsql.CRM_SQL103
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '4':
        sql = crm.crmsql.CRM_SQL104
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人卡余额查询
    if crmrptid == '5':
        sql = crm.crmsql.CRM_SQL105
        params = (company + '  ' + storecode + ' '+ str(minileftmoney)  + ' '+ str(maxleftmoney) + '  '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '6':
        sql = crm.crmsql.CRM_SQL105
        params = (company + '  ' + storecode + ' '+ str(minileftmoney)  + ' '+ str(maxleftmoney) + '  '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人生日
    if crmrptid == '8':
        fromdate=str(fromdate).replace('-','')
        todate = str(todate).replace('-','')
        sql = crm.crmsql.CRM_SQL108
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人生日
    if crmrptid == '9':
        fromdate=str(fromdate).replace('-','')
        todate = str(todate).replace('-','')
        sql = crm.crmsql.CRM_SQL109
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

def get_crmsubreport(request):
    company = request.GET['company']
    crmsubreport = CrmSubReport.objects.filter(company=company,flag='Y').values_list('id','crmsubreportName')
    sql = "  select id, crmsubreportname from crmsubreport " \
          "  where flag='Y' and company = %s "

    params =  (company+' ').split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")