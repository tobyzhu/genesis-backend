#coding = utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.db.models import Q

# Create your views here.
from django.contrib import auth
from rest_framework import  pagination,viewsets,filters
from rest_framework.views import APIView
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import uuid as UUID
import datetime
import json

# from baseinfo.models import Hdsysuser

from django.db import connection

import common.constants

# from adviser.views import sql_to_json
from baseinfo.models import Appoption,Storeinfo,Paymode, Hdsysuser,Cardsupertype,Position,Srvtopty,Wharehouse,Serviece,Empl
#from wechat.models import WechatAppFunctions
from .models import WifiList,Sequence  #,CompanyItem,CompanyOrderItem,CompanyOrder
from .serializers import WifiListSerializer   #,CompanyOrderSerializer,CompanyItemSerializer


def getserno(company,storecode, tablecode):
    try:
        sequence = Sequence.objects.get(company=company, storecode=storecode, tablecode=tablecode)
    except:
        sequence = Sequence.objects.create(company=company, storecode=storecode, tablecode=tablecode, sequence=0)
    print('sequence', sequence)
    sequence.sequence = sequence.sequence + 1
    sequence.save()

    return company  + storecode +'_'+ tablecode+'_' + str(sequence.sequence)


def sql_to_json(sql,params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)

        list_data = []
        desc = cursor.description
        if desc == None:
            return []
        columns = [col[0] for col in desc]
        for row in cursor.fetchall():
            list_data.append(dict(zip(columns, row)))
        # return cardtypelist

        json_data = json.dumps(list_data,cls=DjangoJSONEncoder)
        # print('json_data',json_data)
        cursor.close()
        # connection.close()
        connection.close()
        return json_data

# 初始化一家公司的基础设定
def init_baseinfo(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID
    print('company=',company)

    # Appoption
    # appoption001= Appoption.objects.get_or_create(company='common',seg='company',itemname=company)
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass1',itemname='A',itemvalues='A:明星项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass1',itemname='B',itemvalues='B:金牛项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass1',itemname='C',itemvalues='C:瘦狗项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass1',itemname='D',itemvalues='D:问题项目')
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass2',itemname='A',itemvalues='A:基础项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass2',itemname='B',itemvalues='B:大项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass2',itemname='C',itemvalues='C:合作项目')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='marketclass2',itemname='D',itemvalues='D:医美')
    #
    # for item in common.constants.MARKET_ITEM_CLASS1:
    #     print(item[0],item[1])
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='100',itemvalues='面部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='110',itemvalues='眼部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='200',itemvalues='身体')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='205',itemvalues='肩颈')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='210',itemvalues='胸部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='220',itemvalues='腹部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='230',itemvalues='背部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='240',itemvalues='腿部')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='300',itemvalues='肝胆')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='bodyparts1',itemname='400',itemvalues='肠道')
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='A++',itemvalues='A++')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='A+',itemvalues='A+')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='A',itemvalues='A')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='B+',itemvalues='B+')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='B',itemvalues='B')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='C',itemvalues='C')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='viplevel',itemname='D',itemvalues='D')
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='vipstatus',itemname='10',itemvalues='活跃')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='vipstatus',itemname='20',itemvalues='休眠')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='vipstatus',itemname='30',itemvalues='流失')
    #
    #
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='pmname',itemvalues='准店长')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='secname',itemvalues='护理师')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='thrname',itemvalues='护理师')
    #
    # appoption001 = Appoption.objects.get_or_create(company=company,seg='common',itemname='recal_emplarch_url',itemvalues='')
    # appoption001 = Appoption.objects.get_or_create(company=company,seg='common',itemname='dailyprocess',itemvalues='')

    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='10',itemvalues='已开单')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='20',itemvalues='配料完成')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='30',itemvalues='配料确认')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='40',itemvalues='服务完成确认')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='50',itemvalues='客户确认')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='60',itemvalues='挂账')
    appoption001= Appoption.objects.get_or_create(company=company,seg='psstatus',itemname='70',itemvalues='结帐完成')

    # # 00 storecode
    # storecode00 = Storeinfo.objects.get_or_create(company=company,storecode='00',storename='总部',hdflag='Y')
    # print('storecode00',storecode00)
    # # storecode00.save()
    #
    # # paymode
    # paymodeA= Paymode.objects.get_or_create(company=company,pcode='A',pname='现金',iscash='1',sysflag='Y',changfalg=10,currency='RMB',rate=1,guideperc=1)
    # # paymodeA.save()
    #
    #
    #
    # paymodeA1= Paymode.objects.get_or_create(company=company,pcode='A1',pname='银联',iscash='1',sysflag='N',changfalg=11,currency='RMB',rate=1,guideperc=1)
    # paymodeA2= Paymode.objects.get_or_create(company=company,pcode='A2',pname='支付宝',iscash='1',sysflag='N',changfalg=12,currency='RMB',rate=1,guideperc=1)
    # paymodeA3= Paymode.objects.get_or_create(company=company,pcode='A3',pname='微信',iscash='1',sysflag='N',changfalg=13,currency='RMB',rate=1,guideperc=1)
    # paymodeA4= Paymode.objects.get_or_create(company=company,pcode='A4',pname='美团',iscash='1',sysflag='N',changfalg=14,currency='RMB',rate=1,guideperc=1)
    #
    # paymodeB= Paymode.objects.get_or_create(company=company,pcode='B',pname='储值卡付',iscash='0',sysflag='Y',changfalg=30,currency='RMB',rate=1,guideperc=1)
    # paymodeB1= Paymode.objects.get_or_create(company=company,pcode='B1',pname='疗程卡付',iscash='0',sysflag='N',changfalg=31,currency='RMB',rate=1,guideperc=1)
    #
    # paymodeZ= Paymode.objects.get_or_create(company=company,pcode='Z',pname='免单/赠送',iscash='2',sysflag='N',changfalg=41,currency='RMB',rate=1,guideperc=0)
    # paymodeZ1 = Paymode.objects.get_or_create(company=company, pcode='Z1', pname='赠送储值卡付', iscash='2', sysflag='N',
    #                                      changfalg=30, currency='RMB', rate=1, guideperc=1)
    # paymodeZ2 = Paymode.objects.get_or_create(company=company, pcode='Z2', pname='赠送疗程卡付', iscash='2', sysflag='N',
    #                                      changfalg=30, currency='RMB', rate=1, guideperc=1)
    #
    # # hdsysuser
    # # hdsysadmin = Hdsysuser.objects.get_or_create(company=company,storecode='00',sys_userid='admin',sys_passwd='12345',sys_userstatus=0,sys_fullname='admin',sys_adm='Y',storelist='00,')
    #
    # # Cardsupertype
    # cardtype10 = Cardsupertype.objects.get_or_create(company=company,code='10',name='储值卡',pcode='B')
    # cardtype20 = Cardsupertype.objects.get_or_create(company=company,code='20',name='疗程卡',pcode='B1')
    # cardtype30 = Cardsupertype.objects.get_or_create(company=company,code='30',name='赠送储值',pcode='Z1')
    # cardtype40 = Cardsupertype.objects.get_or_create(company=company,code='40',name='赠送疗程',pcode='Z2')
    #
    # # Position
    # position100 = Position.objects.get_or_create(company=company,positioncode='100',positiondesc='美疗师',bookingflag='Y')
    # position100 = Position.objects.get_or_create(company=company,positioncode='110',positiondesc='美体师',bookingflag='Y')
    #
    # position200 = Position.objects.get_or_create(company=company,positioncode='200',positiondesc='顾问',bookingflag='N')
    # position300 = Position.objects.get_or_create(company=company,positioncode='300',positiondesc='库管',bookingflag='N')
    # position400 = Position.objects.get_or_create(company=company,positioncode='400',positiondesc='其他',bookingflag='N')
    # position400 = Position.objects.get_or_create(company=company,positioncode='210',positiondesc='店长',bookingflag='N')
    #
    # # Srvtopty
    # srvtop100 = Srvtopty.objects.get_or_create(company=company,topcode='100',ttname='按会员卡折扣')
    # srvtop200 = Srvtopty.objects.get_or_create(company=company, topcode='200', ttname='不折扣')
    #
    # # Wharehouse
    # whcode00=Wharehouse.objects.get_or_create(company=company,storecode='00',wharehousecode='00',wharehousename='总仓')

    wxfunctions = WechatAppFunctions.objects.filter(company='common',flag='Y')

    return HttpResponse("完成！", content_type="application/json")

def init_baseinfo_bystore(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID
    print('company=',company)

    stores = Storeinfo.objects.filter(company=company)

    for store in stores:
        print('store',store.storecode)
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='usedriver',itemvalues='Y')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='printer',itemvalues='')
        options = Appoption.objects.get_or_create(company=company, storecode=store.storecode, seg='invoicetype',
                                              itemname='invoicetype', itemvalues='80')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='invoicecopys',itemvalues='1')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='width',itemvalues='80')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='title',itemvalues='')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='footer',itemvalues='扫一扫 关注公众号 了解更多活动详情！')
        options = Appoption.objects.get_or_create(company=company,storecode=store.storecode,seg='invoicetype',itemname='qrcode',itemvalues='images/qrcode.jpg')

    return HttpResponse("完成！", content_type="application/json")


def init_baseinfo_salon(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID
    print('company=',company)
    # Appoption
    appoption001= Appoption.objects.get_or_create(company='common',seg='company',itemname=company)

    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='pmname',itemvalues='发型师')
    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='secname',itemvalues='技师')
    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='thrname',itemvalues='助工')

    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='10',itemvalues='洗吹')
    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='20',itemvalues='剪发')
    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='30',itemvalues='烫发')
    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='40',itemvalues='染发')
    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='50',itemvalues='护理')
    appoption001= Appoption.objects.get_or_create(company=company,seg='displayclass1',itemname='60',itemvalues='其他')

    paymodeA1= Paymode.objects.get_or_create(company=company,pcode='A1',pname='银联',iscash='1',sysflag='N',changfalg=11,currency='RMB',rate=1,guideperc=1)
    paymodeA2= Paymode.objects.get_or_create(company=company,pcode='A2',pname='支付宝',iscash='1',sysflag='N',changfalg=12,currency='RMB',rate=1,guideperc=1)
    paymodeA3= Paymode.objects.get_or_create(company=company,pcode='A3',pname='微信',iscash='1',sysflag='N',changfalg=13,currency='RMB',rate=1,guideperc=1)
    paymodeA4= Paymode.objects.get_or_create(company=company,pcode='A4',pname='美团',iscash='1',sysflag='N',changfalg=14,currency='RMB',rate=1,guideperc=1)
    paymodeB= Paymode.objects.get_or_create(company=company,pcode='B',pname='储值卡付',iscash='0',sysflag='Y',changfalg=30,currency='RMB',rate=1,guideperc=1)
    paymodeZ= Paymode.objects.get_or_create(company=company,pcode='Z',pname='免单/赠送',iscash='2',sysflag='N',changfalg=41,currency='RMB',rate=1,guideperc=0)

    # Srvtopty
    srvtop100 = Srvtopty.objects.get_or_create(company=company,topcode='100',ttname='按会员卡折扣')
    srvtop200 = Srvtopty.objects.get_or_create(company=company, topcode='200', ttname='不折扣')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='10001',topcode='100',svrname='洗发',displayclass1='10')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='20001',topcode='100',svrname='剪发',displayclass1='20')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='30001',topcode='100',svrname='洗发',displayclass1='30')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='40001',topcode='100',svrname='洗发',displayclass1='40')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='50001',topcode='100',svrname='护理',displayclass1='50')
    srv = Serviece.objects.get_or_create(company=company,svrcdoe='60001',topcode='100',svrname='其他',displayclass1='60')

    position = Position.objects.get_or_create(company=company,positioncode='100',positiondesc='发型师',valideflag='Y',bookingflag='Y')
    position = Position.objects.get_or_create(company=company,positioncode='200',positiondesc='技师',valideflag='Y',bookingflag='Y')
    position = Position.objects.get_or_create(company=company,positioncode='300',positiondesc='助工',valideflag='Y',bookingflag='Y')

    return HttpResponse("完成！", content_type="application/json")

def init_demo(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID
    print('company=', company)
    # Appoption
    demostorecode='88'
    stores = Storeinfo.objects.get_or_create(company=company,storecode=demostorecode,storename='演示门店')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='888',ename='demo')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='06',ename='Tsir',position='100')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='07',ename='Eddie',position='100')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='08',ename='Stephanie',position='100')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='20',ename='20号',position='20')
    empl = Empl.objects.get_or_create(company=company, storecode=demostorecode,ecode='21',ename='21',position='20')
    hdsysuser = Hdsysuser.objects.get_or_create(company=company,storecode=demostorecode,sys_userid='888',sys_passwd='12345',sys_fullname='demo',sys_userstatus='10',sys_idtype='10',sys_adm='Y',storelist=demostorecode+',',costpriceflag='N')
    hdsysuser = Hdsysuser.objects.get_or_create(company=company,storecode=demostorecode,sys_userid='06',sys_passwd='12345',sys_fullname='demo',sys_userstatus='10',sys_idtype='10',sys_adm='Y',storelist=demostorecode+',',costpriceflag='N')

    return HttpResponse("完成！", content_type="application/json")

class WifiListViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = WifiList.objects.filter(company=common.constants.COMPANYID,flag='Y',valiflag='Y')
    serializer_class = WifiListSerializer

# class CompanyItemViewSet(viewsets.ModelViewSet):
#     # lookup_field = 'uuid'
#     queryset = CompanyItem.objects.filter(flag='Y')
#     serializer_class = CompanyItemSerializer
#
# class CompanyOrderViewSet(viewsets.ModelViewSet):
#     lookup_field = 'id'
#
#     filter_backends = (filters.SearchFilter,)
#     queryset = CompanyOrder.objects.filter(order_status='10')
#     serializer_class = CompanyOrderSerializer
#     filter_fields=('openid','order_status')
#     search_fields=('openid','order_status')


@csrf_exempt
def query_CompanyOrder(request):
    try:
        openid=request.GET['openid']
    except:
        raise  ValueError('not find openid')

    sql = "  SELECT id, payed_datetime,order_status,order_amount " \
          "  FROM youlan.companyorder " \
          "   where openid =%s"

    params = (openid  + ' ' ).split()
    print(sql, params)
    json_data = sql_to_json(sql, params)
    # return HttpResponse(json_data, content_type="application/json")
    return HttpResponse(json_data,content_type='application /json;charset=utf-8')



@csrf_exempt
def check_WifiList(request):
    # try:
    #     company=request.GET['company']
    # except:
    #     company='demo'
    #
    # try:
    #     storecode= request.GET['storecode']
    # except:
    #     storecode='demo'

    try:
        networktype = request.GET['networktype']

    except:
        networktype='4G'
        ssid = ''
        bssid=''

    try:
        ecode=request.GET['ecode']
    except:
        ecode=''

    print('networktype:',networktype)
    if networktype=='wifi':
        ssid = request.GET['ssid']
        bssid = request.GET['bssid']
        wifi = WifiList.objects.get_or_create(SSID=ssid,BSSID=bssid)


        #     print('wifi:',wifi.company,wifi.creater)
        #     data = json.dumps(list(wifi))
        #     return HttpResponse(data, content_type="application/json")
        # print(company,storecode,ssid,bssid)

    if networktype=='wifi':
        sql = " select company, storecode from wifilist where flag='Y' and valiflag='Y' and bssid =%s "
        params = (' '+ bssid).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)

        wifi = WifiList.objects.get(flag='Y',valiflag='Y',BSSID=bssid)

        try:
            company = wifi.company
            companyname = Appoption.objects.get(company='common',seg='company',itemname=wifi.company).itemvalues
        except:
            company = common.constants.DEMO_COMPANY
            companyname = common.constants.DEMO_COMPANYNAME

        try:
            store = Storeinfo.objects.get(company=company,storecode=wifi.storecode)
            storecode = store.storecode
            storename = store.storename
        except:
            storecode = common.constants.DEMO_STORECODE
            storename = common.constants.DEMO_STORENAME

        json_data={
            "company":company,
            "companyname":companyname,
            "storecode":storecode,
            "storename":storename
        }
        print(json_data)
        return JsonResponse(json_data)
        # return HttpResponse(json_data, content_type="application/json")
    #
    # if networktype=='4G':
    #     sql = " select 'yfy' company,'88' storecode  from wifilist "
    #     params = (  ).split()
    #     print(sql, params)
    #     json_data = sql_to_json(sql, params)
    #     return HttpResponse(json_data, content_type="application/json")

    if networktype=='4G':
        sql = " select 'salon' company,'健康绚烂连锁（演示）' companyname,'88' storecode '天上人家（演示）'  from wifilist "
        # params = (  ).split()
        params=[]
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

def applyNetwork(request):
    try:
        company=request.GET['company']
    except:
        company='anymounse'

    try:
        storecode= request.GET['storecode']
    except:
        storecode='anymouse'

    try:
        networktype = request.GET['networktype']
        ssid = request.GET['ssid']
        bssid = request.GET['bssid']
    except:
        networktype='4G'
        ssid = ''
        bssid=''

    try:
        ecode=request.GET['ecode']
    except:
        ecode=''

    if networktype=='wifi':
        wifi = WifiList.objects.create(company=company,storecode=storecode, SSID=ssid,BSSID=bssid)
        print('wifi:',wifi.company,wifi.creater)
        return HttpResponse('200',content_type='application /x-www-form-urlencoded;charset=utf-8')

        # data = json.dumps(list(wifi))
        # return HttpResponse(data, content_type="application/json")
    # print(company,storecode,ssid,bssid)
    return HttpResponse('500',content_type='application /x-www-form-urlencoded;charset=utf-8')


def check_userpwd(request):
    try:
        company=request.GET['company']
    except:
        company='yfy'

    try:
        storecode= request.GET['storecode']
    except:
        storecode='88'

    try:
        usercode = request.GET['usercode']
    except:
        usercode='demo'

    try:
        password = request.GET['password']
    except:
        password=''

    if company=='yfy':
        print('88')


    # sql = " select * " \
    #       " from hdsysuser " \
    #       " where flag='Y' " \
    #       " and company=%s and storecode =%s and sys_userid =%"

    try:
        print('1',company,storecode,usercode,password)
        sysuser = Hdsysuser.objects.filter(company=company,storecode=storecode,flag='Y',sys_userid=usercode,sys_passwd=password).values('sys_userid')[0]
        print('2',sysuser)
        return HttpResponse('200',content_type='application /x-www-form-urlencoded;charset=utf-8')
    except:
        sysuser={}
        print('3',sysuser)
        return HttpResponse('500',content_type='application /x-www-form-urlencoded;charset=utf-8')









