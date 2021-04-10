from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.db import models
from django.db.models import Sum
import sys
import uuid


# import baseinfo.models, adviser.models

# import common.constants
from baseinfo.models import Appoption,Storeinfo,Paymode, Hdsysuser,Cardsupertype,Position,Srvtopty,Wharehouse


def init_common_base_info(request):
    company=request.GET['company']
    appoption = Appoption.objects.get_or_create(company=company,seg='stype',itemname='N',itemvalues='正常')
    appoption = Appoption.objects.get_or_create(company=company,seg='stype',itemname='P',itemvalues='赠送')

    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='010', itemvalues='生日')
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='011', itemvalues='阴历生日')
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='020', itemvalues='入会日期')
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='021', itemvalues='结婚纪念日')

    appoption001 = Appoption.objects.get_or_create(flag='Y', company='common', seg='company_pay_period',itemname='1',itemvalues='日')
    appoption001 = Appoption.objects.get_or_create(flag='Y', company='common', seg='company_pay_period',itemname='2',itemvalues='周')
    appoption001 = Appoption.objects.get_or_create(flag='Y', company='common', seg='company_pay_period',itemname='3',itemvalues='月')
    appoption001 = Appoption.objects.get_or_create(flag='Y', company='common', seg='company_pay_period',itemname='4',itemvalues='季')
    appoption001 = Appoption.objects.get_or_create(flag='Y', company='common', seg='company_pay_period',itemname='5',itemvalues='年')
    print('appoption001',appoption001)
    init_baseinfo(company)
    return HttpResponse("完成！", content_type="application/json")

# def init_baseinfo(request):
def init_baseinfo(company):
    # company=request.GET['company']
    print('company',company)
    # Appoption
    # appoption001= Appoption.objects.get_or_create(company=company,)

    # 00 storecode
    storecode00 = Storeinfo.get_or_create(company=company,storecode='00',storename='总部',hdflag='Y')

    # paymode
    paymodeA= Paymode.objects.get_or_create(company=company,pcode='A',pname='现金',iscash='1',sysflag='Y',changfalg=10,currency='RMB',rate=1,guideperc=1)
    paymodeA1= Paymode.objects.get_or_create(company=company,pcode='A1',pname='银联',iscash='1',sysflag='N',changfalg=11,currency='RMB',rate=1,guideperc=1)
    paymodeA2= Paymode.objects.get_or_create(company=company,pcode='A2',pname='支付宝',iscash='1',sysflag='N',changfalg=12,currency='RMB',rate=1,guideperc=1)
    paymodeA3= Paymode.objects.get_or_create(company=company,pcode='A3',pname='微信',iscash='1',sysflag='N',changfalg=13,currency='RMB',rate=1,guideperc=1)
    paymodeA4= Paymode.objects.get_or_create(company=company,pcode='A4',pname='美团',iscash='1',sysflag='N',changfalg=14,currency='RMB',rate=1,guideperc=1)

    paymodeB= Paymode.objects.get_or_create(company=company,pcode='B',pname='储值卡付',iscash='0',sysflag='Y',changfalg=30,currency='RMB',rate=1,guideperc=1)
    paymodeB1= Paymode.objects.get_or_create(company=company,pcode='B1',pname='疗程卡付',iscash='0',sysflag='N',changfalg=31,currency='RMB',rate=1,guideperc=1)

    paymodeZ= Paymode.objects.get_or_create(company=company,pcode='Z',pname='免单/赠送',iscash='2',sysflag='N',changfalg=41,currency='RMB',rate=1,guideperc=0)
    paymodeZ1 = Paymode.objects.get_or_create(company=company, pcode='Z1', pname='赠送储值卡付', iscash='2', sysflag='N',
                                         changfalg=30, currency='RMB', rate=1, guideperc=1)
    paymodeZ2 = Paymode.objects.get_or_create(company=company, pcode='Z2', pname='赠送疗程卡付', iscash='2', sysflag='N',
                                         changfalg=30, currency='RMB', rate=1, guideperc=1)

    # hdsysuser
    hdsysadmin = Hdsysuser.objects.get_or_create(company=company,storecode='00',sys_userid='admin',sys_passwd='12345',sys_userstatus=0,sys_fullname='admin',sys_adm='Y',storelist='00,')

    # Cardsupertype
    cardtype10 = Cardsupertype.objects.get_or_create(company=company,code='10',name='储值卡',pcode='B')
    cardtype20 = Cardsupertype.objects.get_or_create(company=company,code='20',name='疗程卡',pcode='B1')
    cardtype30 = Cardsupertype.objects.get_or_create(company=company,code='30',name='赠送储值',pcode='Z1')
    cardtype40 = Cardsupertype.objects.get_or_create(company=company,code='40',name='赠送疗程',pcode='Z2')

    # Position
    position100 = Position.objects.get_or_create(company=company,positioncode='100',positiondesc='美疗师',bookingflag='Y')
    position200 = Position.objects.get_or_create(company=company,positioncode='200',positiondesc='顾问',bookingflag='N')
    position300 = Position.objects.get_or_create(company=company,positioncode='300',positiondesc='库管',bookingflag='N')
    position400 = Position.objects.get_or_create(company=company,positioncode='400',positiondesc='其他',bookingflag='N')

    # Srvtopty
    srvtop100 = Srvtopty.objects.get_or_create(company=company,topcode='100',ttname='按会员卡折扣')
    srvtop200 = Srvtopty.objects.get_or_create(company=company, topcPode='200', ttname='不折扣')

    # Wharehouse
    whcode00=Wharehouse.objects.get_or_create(company=company,storecode='00',wharehousecode='00',wharehousename='总仓')

    return HttpResponse("完成！", content_type="application/json")

# init_baseinfo('dsdemo')