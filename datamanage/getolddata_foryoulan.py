
#coding = utf-8
import io
import sys
import urllib
#import urllib2
import re
import string
import pymysql,pymssql
import time
import random
from urllib.request import urlopen
from  requests import request

from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import date,datetime,timedelta
from django.core import serializers
from django.db.models import Avg,Sum,Count

from baseinfo.models import Goods,Serviece,Vip,Cardtype,Servieceprice,Appoption,Goodsct,Promotions,Promotionsdetail,ItemType,Cardvsdi,CardtypeVsDiscountClass
from adviser.models import Cardinfo
import baseinfo.tools
import common.constants
from .models import OldCardTypeItemDetail

company='orlane'
# Create your views here.
#from jmj.views import SetPrecentData
#   blMemberCardType    所有卡类明细
#   tblMemberCardTypeDefaultItemDetails] 疗程卡类对应的服务项目编号
#   tblMemberCardTypePresentItemTypeLimitDetails 赠送储值卡  原价赠送使用项目类别设定
#   tblMemberCardTypePresentItemLimitDetails] 赠送储值卡   使用项目明细设定
#   tblMemberCardTypeDefaultItemType  所有疗程卡卡类  按项目类别对应
#   tblMemberCardTypeDefaultItemDetails 所有疗程卡卡类 按具体项目明细对应
#   tblMemberCardTypeComboGoodsDetails  所有疗程卡卡类  保含的单个产品明细
#   tblMemberCardTypeComboGoodsTypeDetails 所有卡类  包含的产品类别明细
#   tblMemberCardTypeFavourItemDetails  所有卡类  包含的赠送项目明细
#   tblMemberCardTypeFavourItemType     所有卡类 包含的赠送项目类型
#   tblMemberCardTypeGoodsTypeLimitDetails  产品卡 限定可消费产品类别
#   tblMemberCardTypeItemDiscount   卡类对应项目明细折扣
#   tblMemberCardTypeItemLimitDetails 卡类对应限定项目明细
#   tblMemberCardTypeItemTypeDiscount  卡类对应项目类别折扣
#   tblMemberCardTypeItemTypeLimitDetails   卡类可以消费服务项目类别 限定   --储值卡
#   tblMemberCardTypePresentGoodsLimitDetails   卡类包含原价赠送金额  可消费商品明细
#   tblMemberCardTypePresentGoodsTypeLimitDetails   卡类包含原价赠送金额 可消费商品类别
#   blMemberCardTypePresentItemLimitDetails  卡类包含原价赠送金额  可消费项目明细
#   tblMemberCardTypePresentItemTypeLimitDetails    卡类包含原价赠送金额  可消费项目类别明细
#   tblMemberCardTypePriceDetails   卡类对应标准售价、实际售价 及可否修改
#   tblMemberCardTypeSubCardDetails 卡类包含的子卡明细
#


# tblMemberCard所有卡清单
# [tblMemberCardItemDetails]  所有疗程卡及对应项目清单



def connectdb(server):
    if server == 'mysql':
        read = pymysql.connect("youlan.softweb.net.cn", "sa", "shgv2014", "youlan")

    if server =='mssql':
        read = pymssql.connect(server='localhost', user='sa',password='shgv2014', database='BigideaR')

    return read

def disconnectdb(read):
    read.close()

    return 0



def GetVipData():

    # period = '05'

    # get Vip
    host='http://localhost:8080/'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    # 抓取VIP信息
    url= host+ 'datamanage/VipReadAndWrite'
    req =urllib.request.Request(url=url,headers=headers)
    urllib.request.urlopen(req)

    # 设置VIP 姓名首拼
    url= host+ 'baseinfo/set_vip_pinyin'
    req =urllib.request.Request(url=url,headers=headers)
    urllib.request.urlopen(req)

    return 'Get Vip Finished'

# GetVipData()

def getItemType():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 商品类别
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 3  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            itemtype = ItemType.objects.get(company=company,ttype='G', itemtypecode=value[0])
            itemtype.itemname = value[1]
            itemtype.parentitemtype = value[2]
            itemtype.save()
            print(itemtype.itemtypecode, itemtype.itemtypename, 'skipped！')
        except:
            itemtype = ItemType.objects.create(company=company,ttype='G', itemtypecode=value[0],itemtypename=value[1], parentitemtype=value[2])
            print(itemtype.itemtypecode, itemtype.itemtypename, ' created！')

    # 服务项目类别
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 4  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            itemtype = ItemType.objects.get(company=company,ttype='S', itemtypecode=value[0])
            itemtype.itemname = value[1]
            itemtype.parentitemtype = value[2]
            itemtype.save()
            print(itemtype.itemtypecode, itemtype.itemtypename, 'skipped！')
        except:
            itemtype = ItemType.objects.create(company=company,ttype='S', itemtypecode=value[0],itemtypename=value[1], parentitemtype=value[2])
            print(itemtype.itemtypecode, itemtype.itemtypename, ' created！')

    #卡项类别
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 13  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            itemtype = ItemType.objects.get(company=company,ttype='C', itemtypecode=value[0])
            itemtype.itemname = value[1]
            itemtype.parentitemtype = value[2]
            itemtype.save()
            print(itemtype.itemtypecode, itemtype.itemtypename, 'skipped！')
        except:
            itemtype = ItemType.objects.create(company=company,ttype='C', itemtypecode=value[0],itemtypename=value[1], parentitemtype=value[2])
            print(itemtype.itemtypecode, itemtype.itemtypename, ' created！')

    return 0

def getGoodsDisplayclass():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 商品displaycalss1
    readsql =   " select a.fldvalue, fldDescription1, a.fldParentValue" \
                " from [tblDictionary] a" \
                " where 1=1 and a.fldkey = 3 and a.fldParentValue=-1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company,seg='goodsdisplayclass1',itemname=value[0])
            appoption.itemvalues=value[1]
            appoption.itemvalues2=value[2]
            appoption.save()
            print(appoption.itemname,appoption.itemvalues,'skipped！')
        except:
            appoption = Appoption.objects.create(company=company,seg='goodsdisplayclass1',itemname=value[0],itemvalues=value[1],itemvalues2=value[2])
            print(appoption.itemname,appoption.itemvalues,'created！')
    # disconnectdb(read)

    # 商品displaycalss2
    readsql =   " select a.fldvalue, fldDescription1, a.fldParentValue" \
                " from [tblDictionary] a" \
                " where 1=1 and a.fldkey = 3 and a.fldParentValue<>-1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company,seg='goodsdisplayclass2',itemname=value[0])
            appoption.itemvalues=value[1]
            appoption.itemvalues2=value[2]
            appoption.save()
            print(appoption.itemname,appoption.itemvalues,'skipped！')
        except:
            appoption = Appoption.objects.create(company=company,seg='goodsdisplayclass2',itemname=value[0],itemvalues=value[1],itemvalues2=value[2])
            print(appoption.itemname,appoption.itemvalues,'skipped！')



    # # 商品类别
    # readsql =   " select a.fldvalue, fldDescription1, a.fldParentValue" \
    #             " from [tblDictionary] a" \
    #             " where 1=1 and a.fldkey = 3 "
    # Rcursor.execute(readsql)
    # readResult = Rcursor.fetchall()
    #
    # for value in readResult:
    #     try:
    #         goodsct = Goodsct.objects.get(company=company,goodsct=value[0])
    #         goodsct.goodsctname=value[1]
    #         goodsct.parent=value[2]
    #         goodsct.save()
    #         print(goodsct.goodsct,goodsct.goodsctname,'skipped！')
    #     except:
    #         goodsct = Goodsct.objects.create(goodsct=value[0],goodsctname=value[1],parent=value[2],company=company)
    #         print(goodsct.goodsct,goodsct.goodsctname,'created')
    #
    disconnectdb(read)

    return 0
    # return HttpResponse("完成！", content_type="application/json")
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()


    # 服务项目类别
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 4  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            itemtype = ItemType.objects.get(company=company,ttype='S', itemtypecode=value[0])
            itemtype.itemname = value[1]
            itemtype.parentitemtype = value[2]
            itemtype.save()
            print(itemtype.itemtypecode, itemtype.itemtypename, 'skipped！')
        except:
            itemtype = ItemType.objects.create(company=company,ttype='S', itemtypecode=value[0],itemtypename=value[1], itemtypeparent=value[2])
            print(itemtype.itemtypecode, itemtype.itemtypename, ' created！')

def getSrvDisplayclass():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()


    # 服务项目类别
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 4  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            itemtype = ItemType.objects.get(company=company,ttype='S', itemtypecode=value[0])
            itemtype.itemname = value[1]
            itemtype.parentitemtype = value[2]
            itemtype.save()
            print(itemtype.itemtypecode, itemtype.itemtypename, 'skipped！')
        except:
            itemtype = ItemType.objects.create(company=company,ttype='S', itemtypecode=value[0],itemtypename=value[1], itemtypeparent=value[2])
            print(itemtype.itemtypecode, itemtype.itemtypename, ' created！')

    # 服务项目displaycalss1
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 4 and a.fldParentValue=-1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company, seg='srvdisplayclass1', itemname=value[0])
            appoption.itemvalues = value[1]
            appoption.itemvalues2 = value[2]
            appoption.save()
            print(appoption.itemname, appoption.itemvalues, 'skipped！')
        except:
            appoption = Appoption.objects.create(company=company, seg='srvdisplayclass1', itemname=value[0],
                                                 itemvalues=value[1], itemvalues2=value[2])
            print(appoption.itemname, appoption.itemvalues, '！')

    # 服务项目displaycalss2
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 4 and a.fldParentValue<>-1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company, seg='srvdisplayclass2', itemname=value[0])
            appoption.itemvalues = value[1]
            appoption.itemvalues2 = value[2]
            appoption.save()
            print(appoption.itemname, appoption.itemvalues, 'skipped！')
        except:
            appoption = Appoption.objects.create(company=company, seg='srvdisplayclass2', itemname=value[0],
                                                 itemvalues=value[1], itemvalues2=value[2])
            print(appoption.itemname, appoption.itemvalues, 'created！')


    disconnectdb(read)

    return 0
    # return HttpResponse("完成！", content_type="application/json")

def getCardDisplayclass():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 卡类displaycalss1
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 13 and a.fldParentValue<=1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company, seg='srvdisplayclass1', itemname=value[0])
            appoption.itemvalues = value[1]
            appoption.itemvalues2 = value[2]
            appoption.save()
            print(appoption.itemname, appoption.itemvalues, 'skipped！')
        except:
            appoption = Appoption.objects.create(company=company, seg='srvdisplayclass1', itemname=value[0],
                                                 itemvalues=value[1], itemvalues2=value[2])
            print(appoption.itemname, appoption.itemvalues, 'created！')

    # 卡类displaycalss2
    readsql = " select a.fldvalue, fldDescription1, a.fldParentValue" \
              " from [tblDictionary] a" \
              " where 1=1 and a.fldkey = 13 and a.fldParentValue>1 "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            appoption = Appoption.objects.get(company=company, seg='srvdisplayclass2', itemname=value[0])
            appoption.itemvalues = value[1]
            appoption.itemvalues2 = value[2]
            appoption.save()
            print(appoption.itemname, appoption.itemvalues, 'skipped！')
        except:
            appoption = Appoption.objects.create(company=company, seg='srvdisplayclass2', itemname=value[0],
                                                 itemvalues=value[1], itemvalues2=value[2])
            print(appoption.itemname, appoption.itemvalues, 'created！')


    disconnectdb(read)

    return 0
    # return HttpResponse("完成！", content_type="application/json")

# for youlan
def GoodsReadAndWrite_Orlane():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 商品基本信息
    readsql =   " select a.fldgoodscode, fldgoodsname1, a.fldspec, a.fldgoodstype, b.fldstandardprice, b.fldsalesprice, fldsafetyqty, fldmaxqty " \
                " from tblgoods a, tblgoodspricedetails b " \
                " where 1=1 and a.fldgoodscode = b.fldgoodscode and b.fldcompanycode='000' "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        print('value',value[3])
        try:
            displayclass = Appoption.objects.get(company=company,seg='goodsdisplayclass2',itemname=str(value[3]))
            displayclass1 =displayclass.itemvalues2
            displayclass2 = displayclass.itemname
        except:
            displayclass = Appoption.objects.get(company=company,seg='goodsdisplayclass1',itemname=str(value[3]))
            displayclass1=displayclass.itemname
            displayclass2=''
        print('displayclass',displayclass.itemvalues,displayclass.itemvalues2)
        try:
            goods = Goods.objects.get(company=company,gcode=value[0])
            goods.gname=value[1]
            goods.spec=value[2]
            goods.rptcode1=value[3]
            goods.buyprc=value[4]
            goods.price=value[5]
            goods.minivalues=value[6]
            goods.maxvalues=value[7]
            goods.displayclass1=displayclass1
            goods.displayclass2=displayclass2
            goods.save()
            print(goods.gcode,'updated！')
        except:
            goods = Goods.objects.create(gcode=value[0],gname=value[1],spec=value[2],displayclass1=displayclass1,displayclass2=displayclass2,rptcode1=value[3],buyprc=value[4],price=value[5],minivalues=value[6],maxvalues=value[7],company=company)
            # goods.save()
            print(goods.gcode,'created')

    disconnectdb(read)
    return '0'
    # return HttpResponse("完成！", content_type="application/json")

# for youlan
def ServieceReadAndWrite_Orlane():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 服务基本信息
    readsql =   " select fldItemcode,fldItemname1,flditemtype,fldremark,fldtag,fldstandardprice,fldexperienceprice,fldtimelen ,fldMnemonicCode" \
                " from  viewItem  " \
                " where 1=1 and  fldcompanycode='000' "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    # print(readResult.count())

    for value in readResult:
        print('value', value[2])
        try:
            displayclass = Appoption.objects.get(company=company, seg='srvdisplayclass2', itemname=str(value[2]))
            displayclass1 = displayclass.itemvalues2
            displayclass2 = displayclass.itemname
        except:
            displayclass = Appoption.objects.get(company=company, seg='srvdisplayclass1', itemname=str(value[2]))
            displayclass1 = displayclass.itemname
            displayclass2 = ''
        print('displayclass', displayclass.itemvalues, displayclass.itemvalues2)

        try:
            srv = Serviece.objects.get(company=company,svrcdoe=value[0])
            srv.svrname=value[1]
            rptcode1=value[2]
            srv.price=value[5]
            srv.price2=value[6]
            srv.stdmins=value[7]
            srv.mnemoniccode=value[8]
            srv.displayclass1=displayclass1
            srv.displayclass2=displayclass2
            srv.topcode='10'
            print(srv.svrcdoe,srv.svrname,'updated！')
        except:
            srv = Serviece.objects.create(svrcdoe=value[0],svrname=value[1],rptcode1=value[2],price=value[5],price2=value[6],stdmins=value[7],topcode='10',displayclass1=displayclass1,displayclass2=displayclass2,company=company)
            # srv.save()
            print(srv.svrcdoe,srv.svrname,'created')

        # 建立项目的servieceprice
        try:
            srvprice =Servieceprice.objects.get(company=company,srvuuid=srv,srvcode=srv.svrcdoe,qty=1)
            srvprice.price=srv.price
            srvprice.amount=srv.price
            srvprice.saleflag='Y'
            srvprice.stype='N'
            srvprice.save()
            print(srvprice.srvcode,srv.svrname,'servieceprice updated！')
        except:
            srvprice =Servieceprice.objects.create(company=company,srvuuid=srv,srvcode=srv.svrcdoe,qty=1,price=srv.price,amount=srv.price,saleflag='Y',stype='N')
            print(srvprice.srvcode, srv.svrname, 'servieceprice created！')

        # 建立项目的疗程卡信息
        try:
            cardtype = Cardtype.objects.get(company=company,  cardtype=srv.svrcdoe)
            cardtype.price = srv.price
            cardtype.leftmoney = srv.price
            cardtype.comptype='times'
            cardtype.prncomptype='times'
            cardtype.suptype='20'
            cardtype.valdatetype='10'
            cardtype.validays=9999
            cardtype.sguuid=str(srv.uuid)
            cardtype.displayclass1=displayclass1
            cardtype.displayclass2=displayclass2
            cardtype.save()
            print(cardtype.cardtype, cardtype.cardname, 'cardtype updated！')
        except:
            cardtype = Cardtype.objects.create(company=company, cardtype=srv.svrcdoe, cardname=srv.svrname,
                                                    price=srv.price, leftmoney=srv.price, comptype='times',prncomptype='times',suptype='20',flag='Y',sguuid=str(srv.uuid))
            print(cardtype.cardtype, cardtype.cardname, 'cardtype created！')
    disconnectdb(read)
    return 0
    # return HttpResponse("完成！", content_type="application/json")

# for youlan
def CardtypeReadAndWrite_orlane():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    amountcardtypelist=['4','32','43','45','51','68','47','60','61','62','67','20','41','44','48','53','69','2']
    # 卡类信息CategoryCode=1 储值卡   2：赠送卡   3  疗程卡
    readsql =   " select fldmembercardtypecode, flddescription1, fldCategoryCode, substring(fldmnemoniccode,1,12) fldmnemoniccode, fldamounts,   fldmemo, fldPresentAmount  " \
                " from  tblMemberCardType  " \
                " where   fldCategoryCode =1 "
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        try:
            cardtype = Cardtype.objects.get(company=company,cardtype=value[0])
            cardtype.cardname =value[1]
            # cardtype.suptype=value[2]
            cardtype.mnemoniccode=value[3][:15]
            cardtype.leftmoney=value[4]
            cardtype.comptype='amount'
            cardtype.prncomptype='amount'
            cardtype.suptype='10'
            cardtype.price=value[4]
            cardtype.price2=value[4]
            # cardtype.cardnote=value[]
            print(cardtype.cardtype,cardtype.cardname,'update！')
        except:
            cardtype= Cardtype.objects.create(cardtype=value[0],cardname=value[1],suptype='10',comptype='amount',prncomptype='amount',mnemoniccode=value[3],leftmoney=value[4],price=value[4] ,price2=value[4],company=company)
            cardtype.save()
            print(cardtype.cardtype,cardtype.cardname,'created')

        if value[6] > 0 :
            try:
                cardtype = Cardtype.objects.get(company=company,cardtype='Z-'+value[0])
                cardtype.cardname ='赠金-'+ value[1]
                # cardtype.suptype=value[2]
                cardtype.mnemoniccode=value[3][:15]
                cardtype.leftmoney=value[6]
                cardtype.comptype='amount'
                cardtype.prncomptype='amount'
                cardtype.suptype='30'
                cardtype.price=value[0]
                cardtype.price2=value[0]
                # cardtype.cardnote=value[7]
                cardtype.save()
                print('Z-',cardtype.cardtype,cardtype.cardname,'update！')
            except:
                cardtype = Cardtype.objects.create(cardtype='Z-'+value[0], cardname='赠金-'+value[1], suptype='30',
                                                   comptype='amount', prncomptype='amount', mnemoniccode=value[3],
                                                   leftmoney=value[6], price=0, price2=0,
                                                    company=company)
                print('Z-',cardtype.cardtype, cardtype.cardname, 'created')

    readsql =   " select fldmembercardtypecode, flddescription1, fldCategoryCode, substring(fldmnemoniccode,1,12) fldmnemoniccode, fldamounts,  fldStandardPrice, fldActualPrice, fldmemo" \
                " from  viewMemberCardType  " \
                " where  fldcompanycode='000'  and fldCategoryCode =2 "
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        try:
            cardtype = Cardtype.objects.get(company=company,cardtype=value[0])
            cardtype.cardname =value[1]
            # cardtype.suptype=value[2]
            cardtype.mnemoniccode=value[3][:15]
            cardtype.leftmoney=value[4]
            cardtype.comptype='amount'
            cardtype.prncomptype='amount'
            cardtype.suptype='30'
            cardtype.price=value[5]
            cardtype.price2=value[6]
            cardtype.cardnote=value[7]
            print(cardtype.cardtype,cardtype.cardname,'update！')
        except:
            print(value,'will be created')
            cardtype= Cardtype.objects.create(cardtype=value[0],cardname=value[1],suptype='30',comptype='amount',prncomptype='amount',mnemoniccode=value[3],leftmoney=value[4],price=value[5] ,price2=value[6],cardnote=value[7],company=company)
            cardtype.save()
            print(cardtype.cardtype,cardtype.cardname,'created')


    readsql =   " select fldmembercardtypecode, flddescription1, fldCategoryCode, substring(fldmnemoniccode,1,12) fldmnemoniccode, fldamounts,  fldStandardPrice, fldActualPrice, fldmemo" \
                " from  viewMemberCardType  " \
                " where  fldcompanycode='000'  and fldCategoryCode =3 "
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        try:
            cardtype = Cardtype.objects.get(company=company,cardtype=value[0])
            cardtype.cardname =value[1]
            # cardtype.suptype=value[2]
            cardtype.mnemoniccode=value[3][:15]
            cardtype.leftmoney=value[4]
            cardtype.comptype='times'
            cardtype.prncomptype='times'
            cardtype.suptype='20'
            cardtype.price=value[5]
            cardtype.price2=value[6]
            cardtype.cardnote=value[7]
            print(cardtype.cardtype,cardtype.cardname,'update！')
        except:
            print(value,'will be created')
            cardtype= Cardtype.objects.create(cardtype=value[0],cardname=value[1],suptype='20',comptype='times',prncomptype='times',mnemoniccode=value[3],leftmoney=value[4],price=value[5] ,price2=value[6],cardnote=value[7],company=company)
            cardtype.save()
            print(cardtype.cardtype,cardtype.cardname,'created')

    disconnectdb(read)
    return 0
    # return HttpResponse("完成！", content_type="application/json")

# for youlan
def PromotionsReadandWrite_orlane():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 卡类信息
    readsql0 =  " select fldmembercardtypecode, flddescription1, fldCategoryCode, substring(fldmnemoniccode,1,12) fldmnemoniccode, fldamounts,   fldmemo, fldPresentAmount " \
                " from  tblMemberCardType " \
                " where   fldCategoryCode=1  "

    # readsql0 =  " select fldmembercardtypecode, flddescription1, fldCategoryCode, fldmnemoniccode, fldamounts,  fldStandardPrice, fldActualPrice, fldmemo, fldPresentAmount " \
    #             " from  viewMemberCardType " \
    #             " where   fldCategoryCode=3 "

    # readsql1 = " SELECT 'S' ttype,'P' stype, 'itemtype' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemType itemcode, b.fldMaxTimes times, b.fldAveragePrice price, b.fldPerformance "\
    #            " FROM tblmembercardtype a, tblMemberCardTypeFavourItemType b "\
    #            " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3"
    #
    # readsql2 =  " SELECT 'S' ttype,'N'stype, 'itemtype' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemType itemcode, b.fldMaxTimes times, b.fldAveragePrice price, b.fldPerformance"\
    #             " FROM tblmembercardtype a, tblMemberCardTypeDefaultItemType b"\
    #             " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3"
    #
    # readsql3=   " SELECT 'S' ttype,'P' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance "\
    #             " FROM tblmembercardtype a, [BigideaR].[dbo].[tblMemberCardTypeFavourItemDetails] b " \
    #             " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3"
    #
    # readsql4=   " SELECT 'S' ttype,'N' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance "\
    #             " FROM tblMemberCardType a, tblMemberCardTypeDefaultItemDetails b " \
    #             " where 1 = 1 and a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3"




    print('readsql0',readsql0)
    Rcursor.execute(readsql0)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        print('value',value[2],value)
        try:
            promotions = Promotions.objects.get(company=company,promotionsid=value[0])
            promotions.mainttype='30'
            promotions.s_price=0
            promotions.emplperc=1
            promotions.sendqty=0
            promotions.mainqty=1
            promotions.disc=1
            promotions.promotionsstatus='active'
            promotions.fromdate='20200101'
            promotions.todate='20201231'
            promotions.save()
            print(promotions.promotionsid,promotions,'is update!')
        except:
            promotions =  Promotions.objects.create(company=company,promotionsid=value[0],promotionsname=value[1],mainttype='30',s_price=0,emplperc=1,sendqty=0,mainqty=1,disc=1,promotionsstatus='acvtive')
            print(promotions.promotionsid,promotions,'is created')

        readsql3 = " SELECT 'C' ttype,'P' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance " \
                   " FROM tblmembercardtype a, [BigideaR].[dbo].[tblMemberCardTypeFavourItemDetails] b " \
                   " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3 and a.fldMemberCardTypeCode='"+promotions.promotionsid+"'"

        readsql4 = " SELECT 'C' ttype,'N' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance " \
                   " FROM tblMemberCardType a, tblMemberCardTypeDefaultItemDetails b " \
                   " where 1 = 1 and a.fldMemberCardTypeCode = b.fldMemberCardTypeCode and a.fldCategoryCode=3 and a.fldMemberCardTypeCode='"+promotions.promotionsid+"'"

        readsql5 = " SELECT 'G' ttype,'N' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldGoodsCode itemcode, b.fldQty times, b.fldStandardPrice price,0 fldPerformance " \
                   " FROM tblMemberCardType a, tblMemberCardTypeComboGoodsDetails b " \
                   " where 1 = 1 and a.fldMemberCardTypeCode = b.fldMemberCardTypeCode  and a.fldMemberCardTypeCode='"+promotions.promotionsid+"'"

        sqls = (readsql3,readsql4,readsql5)
        for sql in sqls:
            readsql = sql
            # print('readsql', readsql)
            Rcursor.execute(readsql)
            readResult2 = Rcursor.fetchall()
            # print('len(readResult2)',len(readResult2))
            for value2 in readResult2:
                print('value2',value2)
                try:
                    print(1,company,promotions.promotionsid,value2[0],value2[1],value2[6],value2[7],value2[8])
                    promotionsdetail =Promotionsdetail.objects.get(company=company,promotionsid=promotions.promotionsid,ttype=value2[0],stype=value2[1],sgcode=value2[6],promotionsqty=value2[7],promotionsprice=value2[8])
                    promotionsdetail.promotionsuuid=promotions
                    # promotionsdetail.stype=value2[0]
                    # promotionsdetail.ttype.value2[1]
                    # promotionsdetail.sgcode=value2[6]
                    promotionsdetail.detailtype='P'
                    promotionsdetail.promotionsqty= value2[7]
                    promotionsdetail.promotionsprice=value2[8]
                    promotionsdetail.promotionsamount =value2[7]*value2[8]
                    promotionsdetail.save()
                    print(promotionsdetail.promotionsid,promotionsdetail.stype,promotionsdetail.ttype,promotionsdetail.sgcode,'is updated')

                except:
                    promotionsdetail = Promotionsdetail.objects.create(company=company,promotionsuuid=promotions,promotionsid=promotions.promotionsid,detailtype='P',ttype=value2[0],stype=value2[1],sgcode=value2[6],promotionsqty=value2[7],promotionsprice=value2[8])
                    print(promotionsdetail.promotionsid,promotionsdetail.stype,promotionsdetail.ttype,promotionsdetail.sgcode,'is created')
    disconnectdb(read)
    return  0
    # return HttpResponse("完成！", content_type="application/json")

def setCardTypeInfo():
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()


    # 卡 购买疗程卡折扣
    readsql =   " select [fldMemberCardTypeCode], [fldCardType], [fldDiscount], [fldLineNumber], [fldIsDiscount]  " \
                " from  tblMemberCardTypeCardTypeDiscount  "
    print('readsql',readsql)
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        print(value[0])
        try:
            cardvsdi= Cardvsdi.objects.get(company=company,ttype='C',cardtype=value[0],topcode=value[1])
            cardvsdi.pricetype='DISCOUNT'
            cardvsdi.cardvsdisc=value[2]
            cardvsdi.topcode=value[1]
            cardvsdi.save()
            print(cardvsdi.cardtype, cardvsdi.pricetype,'is updated')
        except:
            cardvsdi= Cardvsdi.objects.create(company=company,ttype='C',cardtype=value[0],topcode=value[1],pricetype='DISCOUNT',cardvsdisc=value[2])
            print(cardvsdi.cardtype, cardvsdi.pricetype, 'is created')

    # 卡 可消费项目类别设定   针对每个项目类别，设定一个-001的项目
    readsql1 =   " select [fldMemberCardTypeCode] ,[fldItemType],[fldRecordID],[fldLineNumber],[fldMaxTimes],[fldAveragePrice],[fldPerformance] ,'N' stype" \
                " from  [tblMemberCardTypeDefaultItemType]  "

    readsql2 =  " select [fldMemberCardTypeCode] ,[fldItemType],[fldRecordID],[fldLineNumber],[fldMaxTimes],[fldAveragePrice],[fldPerformance] ,'P' stype" \
                " from  [tblMemberCardTypeFavourItemType]  "

    sqls = (readsql1, readsql2)
    for readsql in sqls:
        print('readsql',readsql)
        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()

        for value in readResult:
            print(value[0])
            try:
                displayclass = Appoption.objects.get(company=company, seg='srvdisplayclass2', itemname=str(value[1]))
                displayclass1 = displayclass.itemvalues2
                displayclass2 = displayclass.itemname
            except:
                displayclass = Appoption.objects.get(company=company, seg='srvdisplayclass1', itemname=str(value[1]))
                displayclass1 = displayclass.itemname
                displayclass2 = ''

            try:
                srv = Serviece.objects.get(company=company,svrcdoe=value[0]+'-001' )
                srv.svrname=displayclass.itemvalues
                srv.displayclass1=displayclass1
                srv.displayclass2=displayclass2
                srv.topcode='10'
                srv.save()
                print(srv.svrcdoe,srv.svrname,srv.displayclass1,' is updated')
            except:
                srv = Serviece.objects.create(company=company,svrcdoe=value[0]+'-001',svrname=displayclass.itemvalues,displayclass1=displayclass1,displayclass2=displayclass2,topcode='10')
                print(srv.svrcdoe,srv.svrname,srv.displayclass1,' is created')

            try:
                srvprice =Servieceprice.objects.get(company=company,srvuuid=srv,srvcode=srv.svrcdoe,qty=value[4])
                srvprice.price=value[5]
                srvprice.amount=value[4]*value[5]
                srvprice.saleflag='Y'
                srvprice.stype='N'
                srvprice.save()
                print(srvprice.srvcode,srv.svrname,'servieceprice updated！')
            except:
                srvprice =Servieceprice.objects.create(company=company,srvuuid=srv,srvcode=srv.svrcdoe,qty=value[4],price=value[5],amount=value[4]*value[5],saleflag='Y',stype='N')
                print(srvprice.srvcode, srv.svrname, 'servieceprice created！')

            try:
                print(1, company,  value[0], value[1], value[6], value[7], value[8])
                promotionsdetail = Promotionsdetail.objects.get(company=company, promotionsid=value[0],
                                                                ttype='C', sgcode=srv.svrcdoe,
                                                                promotionsqty=value[4], promotionsprice=value[5],stype=value[7])
                # promotionsdetail.promotionsuuid = promotions
                # promotionsdetail.stype=value2[0]
                # promotionsdetail.ttype.value2[1]
                # promotionsdetail.sgcode=value2[6]
                promotionsdetail.detailtype = 'P'
                promotionsdetail.promotionsqty = value[4]
                promotionsdetail.promotionsprice = value[5]
                promotionsdetail.promotionsamount = value[4] * value[5]
                promotionsdetail.save()
                print(promotionsdetail.promotionsid, promotionsdetail.stype, promotionsdetail.ttype,
                      promotionsdetail.sgcode, 'is updated')

            except:
                promotionsdetail = Promotionsdetail.objects.create(company=company,  promotionsid=value[0], detailtype='P', ttype='C', sgcode=srv.svrcdoe,
                                                                   promotionsqty=value[4], promotionsprice=value[5],promotionsamount=value[4]*value[5],stype=value[7])
                print(promotionsdetail.promotionsid, promotionsdetail.stype, promotionsdetail.ttype,
                      promotionsdetail.sgcode, 'is created')
    return 0


# for youlan
# tblMemberCommentDetails   会员备注信息
def VipReadAndWrite(request):
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    storecodes = ('000','001','002','003')
    codelength = 5
    for store in storecodes:
        # 会员基本信息
        readsql =   " select fldmemberno,fldname1,fldaddressa1,fldmobileno, fldmembercardcode, fldconsultantno, fldbirthdayyear, fldbirthdaymonth, fldimportantinfo, fldstatisticfreq, fldcompanycode " \
                    " from  tblmember  " \
                    " where 1=1 and fldcompanycode = " + store + " order by fldcompanycode,fldmemberno "
        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()
        # print(readResult)
        cnt = 0
        for value in readResult:
            cnt = cnt + 1
            vcode = store + ('000000' + str(cnt))[-codelength:]
            print(value)
            try:
                vip = Vip.objects.get(company=company,vcode=vcode,vipcode=value[0])
                print(vip.vcode,vip.vname,'skipped！')
            except:
                if value[6] == None:
                    birthyear=''
                else:
                    birthyear=value[6]
                if value[7] == None:
                    birthmonth =''
                else:
                    strlist = value[7].split('-')  # 用逗号分割str字符串，并保存到列表
                    if len(strlist)==2:
                        if len(strlist[0])==0:
                            strlist[0] ='0'+strlist[0]

                        if len(strlist[1])==0:
                            strlist[1]='0'+strlist[1]

                        birthmonth=strlist[0]+strlist[1]
                    else:
                        birthmonth='0101'

                birth = birthyear + birthmonth

                vip= Vip.objects.create(viptype='10',vcode=vcode,vipcode=value[0],vname=value[1],addr=value[2],mtcode=value[3],othercha=value[4],ecode=value[5],birth=birth ,vdesc=value[8],viplevel=value[9],storecode=value[10],valiflag='Y',company=company)
                vip.pinyin = baseinfo.tools.main(vip.vname)
                vip.save()
                print(vip.vcode,vip.vname,'created')

    disconnectdb(read)
    return 0
    # return HttpResponse("完成！", content_type="application/json")

# for youlan
def CardinfoReadAndWrite():
    company='youlan'
    read = connectdb('mssql')
    vipcode='B00000038'
    codelength = 4
    # suptype=request.GET['suptype']
    Rcursor = read.cursor()

    vips = Vip.objects.filter(company=company).filter(flag='Y').filter(vipcode=vipcode)
    for vip in vips:
        vcode = vip.vcode
        cnt = 0
        # 储值卡卡基本信息
        readsql1 =  " select  a.fldCompanyCode, a.fldMemberNo,  b.fldMemberCardCode, b.fldMemberCardTypeCode,b.fldStandardPrice,  b.fldOutstanding, b.fldOutstandingTimes " \
                    " from  tblMember a, tblMemberCard b  " \
                    " where 1=1  and a.fldMemberNo = b.fldMemberNo and b.fldOutstanding > 0 and b.fldCategoryCode = '1' and b.fldstatus = '1' "\
                    " and a.fldmemberno= '"+vipcode +"' "\
                    " order by a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode"
        print(readsql1)
        Rcursor.execute(readsql1)
        readResult = Rcursor.fetchall()
        suptype='10'
        for value in readResult:
            try:
                cardtype = Cardtype.objects.get(company=company, cardtype=value[3])
                print('cardtype=',cardtype,cardtype.cardtype,cardtype.cardname)
                cnt = cnt +1
                ccode = vcode + '-' + ('000000' + str(cnt))[-codelength:]

                print(value)
                try:
                    cardinfo = Cardinfo.objects.get(company=company,cardnote=value[2])
                    print('1',cardinfo,'is skipped！')
                except:
                    cardinfo= Cardinfo.objects.create(storecode=value[0],vcode=vcode,vipuuid=vip,ccode=ccode,cardnote=value[2],cardtype=cardtype.cardtype,
                                                      s_price=value[4],leftmoney=value[5],leftqty=value[6],suptype=suptype,cardtypeuuid=cardtype,status='O',company=company)
                    cardinfo.save()
                    print('1',cardinfo,'is created')
            except:
                print('1',vip,value[3],'cardtype not exists!')

        print('1',vip, ' suptype=10 is finished')

        # 疗程卡-对应具体项目的卡
        readsql2 =  " select a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode, b.fldMemberCardTypeCode, c.fldItemCode,   c.fldOutstandingTimes, c.fldOriginPrice, b.fldStandardPrice, b.fldAmount" \
                    " from  tblMember a, tblMemberCard b, tblMemberCardItemDetails c  " \
                    " where 1=1  and a.fldMemberNo = b.fldMemberNo and b.fldMemberCardCode = c.fldMemberCardCode  " \
                     "and c.fldOutstandingtimes > 0 and b.fldCategoryCode = '3' and b.fldstatus = '1' "\
                    " and a.fldmemberno= '"+vipcode +"' "\
                    " order by a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode"

        print(readsql2)
        Rcursor.execute(readsql2)
        readResult = Rcursor.fetchall()

        suptype='20'
        for value in readResult:
            cnt = cnt + 1
            ccode = vcode + '-' + ('000000' + str(cnt))[-codelength:]
            srvcode_old = value[4]
            print('itemcode=',srvcode_old)
            vip = Vip.objects.get(company=common.constants.COMPANYID,vipcode=value[1])
            try:
                srv = Serviece.objects.get(company=company,rptcode6=srvcode_old)
                cardtype = Cardtype.objects.get(company=company,cardtype=srv.svrcdoe)
                print('2',value,srv.svrcdoe,srv.svrname)
                try:
                    cardinfo = Cardinfo.objects.get(company=company,vcode=vcode,cardnote=value[2])
                    print('2',cardinfo,'is skipped！')
                except:
                    cardinfo= Cardinfo.objects.create(storecode=value[0],vcode=vcode,vipuuid=vip,ccode=ccode,cardnote=value[2],cardtype=cardtype.cardtype,promotionsid=value[3],leftqty=value[5],s_price=value[6],leftmoney=value[5]*value[6],cardtypeuuid=cardtype,suptype=suptype,status='O',company=company)
                    cardinfo.save()
                    print('2',cardinfo,'is created')
            except:
                print('2','服务项目:',value[4],srv,'not found')
        print('2',vip, ' suptype=20 is finished')

        # 疗程卡-对应项目类别的
        readsql3 =   " select  a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode, b.fldMemberCardTypeCode, c.flditemtype itemcode, c.fldOriginPrice , c.fldOutstandingTimes" \
                    " from  tblMember a, tblMemberCard b ,tblMemberCardDefaultItemType c " \
                    "  where 1=1  and a.fldMemberNo = b.fldMemberNo and c.fldOutstandingtimes > 0 " \
                    " and b.fldstatus = '1' " \
                    " and b.fldMemberCardCode = c.fldMemberCardCode "\
                    " and a.fldmemberno= '"+vipcode +"' "\
                    " order by a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode"

        print(readsql3)
        Rcursor.execute(readsql3)
        readResult = Rcursor.fetchall()
        suptype='10'

        # for value in readResult:
        #     try:
        #         cardtype = Cardtype.objects.get(company=company, cardtype=value[3])
        #         cnt = cnt +1
        #         ccode = vcode + '-' + ('000000' + str(cnt))[-codelength:]
        #         try:
        #             cardinfo = Cardinfo.objects.get(company=company,vcode=value[1],ccode=value[2])
        #             print(cardinfo,'is skipped！')
        #         except:
        #             cardinfo= Cardinfo.objects.create(storecode=value[0],vcode=value[1],vipuuid=vip,ccode=ccode,cardnote=value[2],cardtype=cardtype.cardtype,s_price=value[5],leftqty=value[6],leftmoney=value[5]*value[6],suptype=suptype,status='O',company=company)
        #             cardinfo.save()
        #             print(cardinfo,'is created')
        #     except:
        #         print(vip,value[3],'cardtype not exists!')

        print('3',vip, ' suptype=10-2 is finished')

       # 赠送卡项目-对应项目明细类别的
        readsql4 =  " select  a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode, b.fldMemberCardTypeCode, b.fldCategoryCode, c.flditemcode, c.fldStandardPrice , c.fldOutstandingTimes" \
                    " from  tblMember a, tblMemberCard b, tblMemberCardFavourItemDetails c " \
                    " where 1=1  and a.fldMemberNo = b.fldMemberNo and c.fldOutstandingtimes > 0 " \
                    " and b.fldstatus = '1' and a.fldCompanyCode = b.fldCompanyCode   and a.fldCompanyCode = c.fldCompanyCode  and a.fldMemberNo = b.fldMemberNo" \
                    " and b.fldMemberCardCode = c.fldMemberCardCode       " \
                    " and c.fldOutstandingtimes > 0"\
                    " and a.fldmemberno= '"+vipcode +"' "\
                    " order by a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode"

        print(readsql4)
        Rcursor.execute(readsql4)
        readResult = Rcursor.fetchall()
        suptype='40'

        for value in readResult:
            srvcode_old = value[5]
            try:
                srv = Serviece.objects.get(company=company,rptcode6=srvcode_old)
                cardtype = Cardtype.objects.get(company=company,cardtype=srv.svrcdoe)
                vip = Vip.objects.get(company=common.constants.COMPANYID, vipcode=value[1])
                print('4',srv,cardtype)
                cnt = cnt +1
                ccode = vcode + '-' + ('000000' + str(cnt))[-codelength:]
                try:
                    cardinfo = Cardinfo.objects.get(company=company,vcode=vcode,cardnote=value[2])
                    # srv = Serviece.objects.get(company=company, rptcode6=srvcode_old)
                    print('4',cardinfo,'is skipped！')
                except:
                    cardinfo= Cardinfo.objects.create(storecode=value[0],vcode=vcode,vipuuid=vip,ccode=ccode,cardnote=value[2],cardtype=cardtype.cardtype,promotionsid=value[3],s_price=value[5],leftqty=value[6],suptype=suptype,status='O',company=company)
                    cardinfo.save()
                    print('4',cardinfo,'is created')
            except:
                print('4',vip,srv,value[5],'cardtype not exists!')

        print('4',vip, ' suptype=40 is finished')


       # 赠送卡项目-对应项目明细类别的
        readsql5 =  " select  a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode, b.fldMemberCardTypeCode, b.fldCategoryCode, c.flditemtype itemcode, c.fldAveragePrice , c.fldOutstandingTimes" \
                    " from  tblMember a, tblMemberCard b, tblMemberCardFavourItemType c " \
                    " where 1=1  and a.fldMemberNo = b.fldMemberNo and c.fldOutstandingtimes > 0 " \
                    " and b.fldstatus = '1' and a.fldCompanyCode = b.fldCompanyCode   and a.fldCompanyCode = c.fldCompanyCode  and a.fldMemberNo = b.fldMemberNo" \
                    " and b.fldMemberCardCode = c.fldMemberCardCode       " \
                    " and c.fldOutstandingtimes > 0"\
                    " and a.fldmemberno= '"+vipcode +"' "\
                    " order by a.fldCompanyCode, a.fldMemberNo, b.fldMemberCardCode"

        print(readsql5)
        Rcursor.execute(readsql5)
        readResult = Rcursor.fetchall()
        suptype='50'

        for value in readResult:
            srvcode_old = value[5]
            try:
                srv = Serviece.objects.get(company=company,rptcode6=srvcode_old)
                cardtype = Cardtype.objects.get(company=company,cardtype=srv.svrcdoe)
                print('5',srv,cardtype)
                cnt = cnt +1
                ccode = vcode + '-' + ('000000' + str(cnt))[-codelength:]
                try:
                    cardinfo = Cardinfo.objects.get(company=company,vcode=vcode,cardnote=value[2])
                    # srv = Serviece.objects.get(company=company, rptcode6=srvcode_old)
                    print('5',cardinfo,'is skipped！')
                except:
                    cardinfo= Cardinfo.objects.create(storecode=value[0],vcode=vcode,vipuuid=vip,ccode=ccode,cardnote=value[2],cardtype=cardtype.cardtype,s_price=value[5],leftqty=value[6],suptype=suptype,status='O',company=company)
                    cardinfo.save()
                    print('5',cardinfo,'is created')
            except:
                print('5',vip,srv,value[5],'cardtype not exists!')

        print('50',vip, ' suptype=40 is finished')


    disconnectdb(read)
    return 0
    # return HttpResponse("完成！", content_type="application/json")


def GetOldData(request):
    # getItemType()
    # getGoodsDisplayclass()
    # getSrvDisplayclass()
    # getCardDisplayclass()

    # GoodsReadAndWrite_Orlane()
    # ServieceReadAndWrite_Orlane()
    # CardtypeReadAndWrite_orlane()

    setCardTypeInfo()

    # PromotionsReadandWrite_orlane()
    # CardinfoReadAndWrite()


    return HttpResponse("完成！", content_type="application/json")
