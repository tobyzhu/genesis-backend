#coding = utf-8

import io
import sys
import urllib
#import urllib2
import re
import string
from common.legacy_db import connect_dieshang_sync
import time
import random
from urllib.request import urlopen
from  requests import request
from decimal import *

from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import date,datetime,timedelta
from django.core import serializers
from django.db.models import Avg,Sum,Count

#from baseinfo.models import Goods,Serviece,Vip,Cardtype,Goodsprice,Servieceprice,Appoption,Goodsct,Empl,Position,Promotions,Promotionsdetail,ItemType,Cardvsdi,CardtypeVsDiscountClass
from baseinfo.models import *
from adviser.models import Cardinfo
import baseinfo.tools
import common.constants
from .models import OldCardTypeItemDetail

company='dieshang'

def connectdb(server):
    if server == 'mysql':
        read = connect_dieshang_sync()

    if server =='mssql':
        raise RuntimeError("MSSQL 连接已暂时禁用")

    return read

def disconnectdb(read):
    read.close()

    return 0



def get_ds_goods(request):
    company='dieshang'
    read = connectdb('mysql')
    Rcursor = read.cursor()

    # 商品类别
    # readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
    #           " from ds_g_item a" \
    #           " where 1=1 and a.fldkey = 3  "

    readsql=    " select  ttype, brand, displayclass1, gcode_old, gcode_new, gname, spec, price, price2, price3, price4, buyprice, puchaseflage, pychaseqty, puchasedays, weijian, supply, standardqty, maxqty, minqty, zhutui, zhutui1, xinxiangm, zhixiao, intervaldays, historyprice, salesflag, changeableflag, discountdesc, pmperc, pmamount, secperc, secamount, storelist, stype "\
                " from ds_g_items"
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print('readresuld',readResult)
    for value in readResult:
        try:
            ttype_desc = value[0]
            try:
                if len(ttype_desc) > 0 :
                    a= ttype_desc.find('-')
                    ttype_name = ttype_desc[0:a]
                    ttype_code = ttype_desc[a+1:100]
            except Exception as e:
                print('ttype error', ttype_desc, e)



            brand_desc = value[1]
            try:
                if len(brand_desc) > 0 :
                    a= brand_desc.find('-')
                    brand_name = brand_desc[0:a]
                    brand_code = brand_desc[a+1:100]
                    print('brand info',brand_desc,a, brand_code, brand_name)
                    brand = Appoption.objects.get_or_create(flag='Y',company=company,seg='brand',itemname=brand_code)[0]
                    brand.itemvalues=brand_name
                    brand.save()

            except Exception as e:
                print('goods brand_desc error', brand_desc, e)

            displayclass1_desc = brand_name
            try:
                if len(displayclass1_desc) > 0:
                    # a = displayclass1_desc.find('-')
                    # displayclass1_name = displayclass1_desc[0:a]
                    displayclass1_name=brand_name
                    # displayclass1_code = displayclass1_desc[a + 1:100]
                    displayclass1_code = value[4][:3]
                    print('displayclass1_ info', displayclass1_desc, a, displayclass1_code, displayclass1_name)
                    displayclass1 = Appoption.objects.get_or_create(flag='Y', company=company, seg='displayclass1', itemname=displayclass1_code)[0]
                    displayclass1.itemvalues = value[4][1:3]+'-'+ displayclass1_name
                    displayclass1.itemvalues2='G'
                    displayclass1.save()

            except Exception as e:
                print('goods displayclass1 error', brand_desc, e)

            displayclass2_desc = value[2]
            try:
                if len(displayclass2_desc) > 0:
                    a = displayclass2_desc.find('-')
                    displayclass2_name = displayclass2_desc[0:a]
                    # displayclass1_code = displayclass1_desc[a + 1:100]
                    displayclass2_code = value[4][:5]
                    print('displayclass2_ info', displayclass1_desc, a, displayclass2_code, displayclass2_name)
                    displayclass2 = Appoption.objects.get_or_create(flag='Y', company=company, seg='displayclass2', itemname=displayclass2_code)[0]
                    displayclass2.itemvalues = value[4][3:5]+'-'+displayclass2_name
                    displayclass2.itemvalues2='G'
                    displayclass2.save()

            except Exception as e:
                print('goods displayclass1 error', brand_desc, e)

            goods = Goods.objects.get_or_create(flag='Y',company=company, gcode=value[4])[0]
            goods.gname = value[5]
            goods.spec = value[6]
            goods.price = value[7]
            goods.maxvalues=value[18]
            goods.minivalues=value[19]
            goods.saleflag=value[26]
            goods.pricechangeable = value[27]
            goods.brand = brand_code
            goods.displayclass1= displayclass1_code
            goods.displayclass2= displayclass2_code

            try:
                # a = value[29].find('%')
                # pmperc = Decimal(value[29][:a])/100
                pmperc=value[29]
                if pmperc== None:
                    pmperc=0
                goods.pmperc=pmperc
            except Exception as e:
                print('goods pmperc error',goods, e,)

            try:
                # a = value[31].find('%')
                # secperc = Decimal(value[31][:a]) / 100
                secperc = value[31]
                if secperc== None:
                    secperc=0
                goods.secperc = secperc
            except Exception as e:
                print('goods secperc errpr',goods, e)

            try:
                secamount = value[32]
                if secamount == None:
                    secamount=0
                goods.secamount =secamount

            except Exception as e:
                print('goods secperc errpr',goods, e)

            goods.displayclass1=displayclass1_code
            # goods.brand = brand_code
            goods.save()
            goods.set_qtybyspec()

            # 产品
            print('gcode',goods.gcode,goods.gcode[0],value[4],value[4][0])

            if goods.gcode[0]=='2':
                try:
                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=1)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[7]) / 1
                    goodsprice.amount = Decimal(value[7])
                    goodsprice.save()

                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=3)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[10]) / 3
                    goodsprice.amount = Decimal(value[10])
                    goodsprice.save()

                except Exception as e:
                    print('set goodsprice error', e, goods.gcode)

            if goods.gcode[0]=='3':
                try:
                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=1)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[7]) / 1
                    goodsprice.amount = Decimal(value[7])
                    goodsprice.save()

                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=5)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[8]) / 5
                    goodsprice.amount = Decimal(value[8])
                    goodsprice.save()

                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=10)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[9]) / 10
                    goodsprice.amount = Decimal(value[9])
                    goodsprice.save()

                    goodsprice = Goodsprice.objects.get_or_create(flag='Y',company=company, goodsuuid=goods, qty=20)[0]
                    goodsprice.gcode = goods.gcode
                    goodsprice.price = Decimal( value[10]) / 20
                    goodsprice.amount = Decimal(value[10])
                    goodsprice.save()
                except Exception as e:
                    print('set goodsprice error', e, goods.gcode)

            print(goods, goods.gcode, value[5],value[6],goods.gname, 'existed！')
        except Exception as e:
            print('goods error', value, e)
            # goods =  Goods.objects.create(flag='Y',company=company, gcode=value[5])
            # goods.gname = value[6]
            # goods.spec = value[7]
            # goods.price = value[8]
            # print(goods, goods.gcode, goods.gname, 'created！')

    return 0


def get_ds_servieces(request):
    company='dieshang'
    read = connectdb('mysql')
    Rcursor = read.cursor()

    # 商品类别
    # readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
    #           " from ds_g_item a" \
    #           " where 1=1 and a.fldkey = 3  "

    readsql=    " select  ttype, brand, displayclass1, srvcode, srvname, spec, price, price2, price3, price4, zhutui, xinxiangmu, zhixiao, xiangliang, usemanage, pricehistory, saleflag, pricechangeflag, discountdesc, pmperc, pmamount, secperc, secamount, storelist, stype"\
                " from ds_s_items"
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print('readresuld',readResult)
    for value in readResult:
        try:
            brand_desc = value[1]
            try:
                if len(brand_desc) > 0 :
                    a= brand_desc.find('-')
                    brand_name = brand_desc[0:a]
                    brand_code = brand_desc[a+1:100]
                    print('brand info',brand_desc,a, brand_code, brand_name)
                    brand = Appoption.objects.get_or_create(flag='Y',company=company,seg='brand',itemname=brand_code)[0]
                    brand.itemvalues=brand_name
                    brand.save()

            except Exception as e:
                print('goods brand_desc error', brand_desc, e)

                # 原菌系列 - 01
            displayclass1_desc = value[2]
            # displayclass1_desc =value[3]
            try:
                if len(displayclass1_desc) > 0:
                    a = displayclass1_desc.find('-')
                    displayclass1_name = brand_name
                    displayclass1_code = '4'+ brand_code
                    print('displayclass1_ info', displayclass1_desc, a, displayclass1_code, displayclass1_name)
                    displayclass1 = Appoption.objects.get_or_create(flag='Y', company=company, seg='displayclass1', itemname=displayclass1_code)[0]
                    displayclass1.itemvalues = brand_code + '-'+displayclass1_name
                    displayclass1.itemvalues2='S'
                    displayclass1.save()

                    displayclass2_name = displayclass1_desc[0:a]
                    displayclass2_code = '4'+brand_code + displayclass1_desc[a + 1:100]
                    print('displayclass2_ info', displayclass1_desc, a, displayclass2_code, displayclass2_name)
                    displayclass2 = Appoption.objects.get_or_create(flag='Y', company=company, seg='displayclass2', itemname=displayclass2_code)[0]
                    displayclass2.itemvalues = displayclass1_desc[a + 1:100]+'-'+displayclass2_name
                    displayclass2.itemvalues2='S'
                    displayclass2.save()

            except Exception as e:
                print('serviece brand_desc error', brand_desc, e)


            serviece = Serviece.objects.get_or_create(flag='Y',company=company, svrcdoe=value[3])[0]
            serviece.svrname = value[4]
            # serviece.spec = value[6]
            serviece.price = value[6]
            serviece.brand = brand_code
            serviece.displayclass1 = displayclass1_code
            serviece.displayclass2 = displayclass2_code

            serviece.saleflag=value[16]
            serviece.pricechangeable = value[17]

            try:
                # a = value[29].find('%')
                # pmperc = Decimal(value[29][:a])/100
                pmperc=value[19]
                if pmperc== None:
                    pmperc=0
                serviece.pmperc=pmperc
            except Exception as e:
                print('serviece pmperc error',serviece, e,)

            try:
                # a = value[31].find('%')
                # secperc = Decimal(value[31][:a]) / 100
                secperc = value[21]
                if secperc== None:
                    secperc=0
                serviece.secperc = secperc
            except Exception as e:
                print('serviece secperc errpr',serviece, e)

            try:
                secamount = value[22]
                if secamount == None:
                    secamount=0
                serviece.secamount =secamount

            except Exception as e:
                print('serviece secperc errpr',serviece, e)

            serviece.displayclass1=displayclass1_code
            serviece.save()


        except Exception as e:
            print('serviece error', value, e)
            # goods =  Goods.objects.create(flag='Y',company=company, gcode=value[5])
            # goods.gname = value[6]
            # goods.spec = value[7]
            # goods.price = value[8]
            # print(goods, goods.gcode, goods.gname, 'created！')

    return 0


def get_ds_empl(request):

    company='dieshang'
    read = connectdb('mysql')
    Rcursor = read.cursor()

    readsql = " select  code1, code2, code3, ecode, ename, indate, storecode, status, storelist, positiocode, positionname, bookingflag, valiflag, user_id, user_name, passoword, adminflag, costflag, rights, storelist2 "\
              " from ds_empl where 1=2"

    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print('readresuld',readResult)
    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='pmname',itemvalues='销售')
    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='secname',itemvalues='操作师')
    appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='thrname',itemvalues='操作师')


    for value in readResult:
        try:
            positioncode = value[9]
            positionname = value[10]
            bookingdesc= value[11]

            if bookingdesc =='可预约':
                bookingflag='Y'
            else:
                bookingflag='N'

            try:
                positioncode = value[9]
                positiondesc = value[10]
                if len(positioncode) > 0 :

                    position = Position.objects.get_or_create(flag='Y',company=company,positioncode=positioncode)[0]
                    position.positiondesc = positiondesc
                    position.bookingflag = bookingflag
                    position.save()

            except Exception as e:
                print('positiondesc error', positioncode, e)

            try:
                ecode= value[3]
                ename = value[4]
                indate = value[5]
                storecode=value[6]
                empl = Empl.objects.get_or_create(flag='Y',company=company, ecode=value[3])[0]
                empl.ename = value[4]
                empl.status='Y'
                if len(indate)>=8:
                    empl.indate = indate.replace('-','')
                empl.storecode=storecode
                # serviece.spec = value[6]
                empl.save()

                try:
                    hdsysuser = Hdsysuser.objects.get_or_create(flag='Y', company=company, sys_userid=empl.ecode,sys_userstatus=1)[0]
                    hdsysuser.sys_fullname = empl.ename
                    hdsysuser.sys_passwd='12345'
                    # hdsysuser.sys_userstatus=1
                    hdsysuser.save()

                except Exception as e:
                    print('hdsysuser error',e)

                print('empl add',empl.ecode, empl.ename)

            except Exception as e:
                print('positiondesc error', positioncode, e)

        except Exception as e:
            print('empl error', value, e)
            # goods =  Goods.objects.create(flag='Y',company=company, gcode=value[5])
            # goods.gname = value[6]
            # goods.spec = value[7]
            # goods.price = value[8]
            # print(goods, goods.gcode, goods.gname, 'created！')

    return 0

