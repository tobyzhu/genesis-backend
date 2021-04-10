#-*-coding:utf-8 -*-
from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import datetime
from django.core import serializers
from django.db.models import Avg,Sum,Count
import pymysql,pymssql
import uuid

from jmj.models import ReportPeriod,PeriodData,OldData
from baseinfo.models import Appoption,Goods,Serviece,Cardtype,Vip,Storeinfo,Wharehouse,Cardtype,Servieceprice,Empl,Promotions,Promotionsdetail
from adviser.models import Cardinfo
from cashier.models import Expvstoll,Expense
import adviser.models
from goods.models import Goodstranslog
from .models import OldCardTypeItemDetail
import baseinfo.tools
import common.constants

from baseinfo.models import Appoption,Storeinfo,Paymode, Hdsysuser,Cardsupertype,Position,Srvtopty,Wharehouse,Servieceprice
# Create your views here.

def init_baseinfo(request):
    company=request.GET['company']
    print('company=',company)
    # Appoption
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='vipcrossshop',itemvalues='Y')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='pmname',itemvalues='顾问')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='secname',itemvalues='美疗师')
    # appoption001= Appoption.objects.get_or_create(company=company,seg='common',itemname='thrname',itemvalues='美疗师')

    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='010', itemvalues='生日')[0]
    appoption001.save()
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='011', itemvalues='阴历生日')[0]
    appoption001.save()
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='020', itemvalues='入会日期')[0]
    appoption001.save()
    appoption001 = Appoption.objects.get_or_create(company=company, seg='vipspecdatetype', itemname='021', itemvalues='结婚纪念日')[0]
    appoption001.save()

    # 00 storecode
    storecode00 = Storeinfo.objects.get_or_create(company=company,storecode='00',storename='总部',hdflag='Y')[0]
    print('storecode00',storecode00.storename)
    storecode00.save()
    storecode88 = Storeinfo.objects.get_or_create(company=company,storecode='88',storename='练习',hdflag='N')[0]
    print('storecode00',storecode88.storename)
    storecode88.save()
    # paymode
    paymode= Paymode.objects.get_or_create(company=company,pcode='A',pname='现金',iscash='1',sysflag='Y',changfalg=10,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='A1',pname='银联',iscash='1',sysflag='N',changfalg=11,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='A2',pname='支付宝',iscash='1',sysflag='N',changfalg=12,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='A3',pname='微信',iscash='1',sysflag='N',changfalg=13,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='A4',pname='美团',iscash='1',sysflag='N',changfalg=14,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='B',pname='储值卡付',iscash='0',sysflag='Y',changfalg=30,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='B1',pname='疗程卡付',iscash='0',sysflag='N',changfalg=31,currency='RMB',rate=1,guideperc=1)[0]
    paymode.save()
    paymode= Paymode.objects.get_or_create(company=company,pcode='Z',pname='免单/赠送',iscash='2',sysflag='N',changfalg=41,currency='RMB',rate=1,guideperc=0)[0]
    paymode.save()
    paymode = Paymode.objects.get_or_create(company=company, pcode='Z1', pname='赠送储值卡付', iscash='2', sysflag='N',
                                         changfalg=30, currency='RMB', rate=1, guideperc=1)[0]
    paymode.save()
    paymode = Paymode.objects.get_or_create(company=company, pcode='Z2', pname='赠送疗程卡付', iscash='2', sysflag='N',
                                         changfalg=30, currency='RMB', rate=1, guideperc=1)[0]
    paymode.save()
    # hdsysuser
    hdsysadmin = Hdsysuser.objects.get_or_create(company=company,storecode='00',sys_userid='admin',sys_passwd='12345',sys_userstatus=0,sys_fullname='admin',sys_adm='Y',storelist='00,')[0]
    hdsysadmin.save()
    # Cardsupertype
    cardtype = Cardsupertype.objects.get_or_create(company=company,code='10',name='储值卡',pcode='B')[0]
    cardtype.save()
    cardtype = Cardsupertype.objects.get_or_create(company=company,code='20',name='疗程卡',pcode='B1')[0]
    cardtype.save()
    cardtype = Cardsupertype.objects.get_or_create(company=company,code='30',name='赠送储值',pcode='Z1')[0]
    cardtype.save()
    cardtype = Cardsupertype.objects.get_or_create(company=company,code='40',name='赠送疗程',pcode='Z2')[0]
    cardtype.save()
    # Position
    position = Position.objects.get_or_create(company=company,positioncode='100',positiondesc='美疗师',bookingflag='Y')[0]
    position.save()
    position = Position.objects.get_or_create(company=company,positioncode='200',positiondesc='顾问',bookingflag='N')[0]
    position.save()
    position = Position.objects.get_or_create(company=company,positioncode='300',positiondesc='库管',bookingflag='N')[0]
    position.save()
    position = Position.objects.get_or_create(company=company,positioncode='400',positiondesc='其他',bookingflag='N')[0]
    position.save()
    # Srvtopty
    srvtop = Srvtopty.objects.get_or_create(company=company,topcode='100',ttname='按会员卡折扣')[0]
    srvtop.save()

    srvtop = Srvtopty.objects.get_or_create(company=company, topcode='200', ttname='不折扣')[0]
    srvtop.save()
    # Wharehouse
    whcode00=Wharehouse.objects.get_or_create(company=company,storecode='00',wharehousecode='00',wharehousename='总仓')[0]
    whcode00.save()

    return HttpResponse("完成！", content_type="application/json")

def init_demo_items(request):
    company='demo'

    items = Serviece.objects.filter(company='yfy',flag='Y',saleflag='Y',valiflag='Y',topcode='100')
    for item in items:
        print('s_item',item.svrcdoe,item.svrname )
        newitem = Serviece.objects.get_or_create(company=company,svrcdoe=item.svrcdoe,svrname=item.svrname, price=item.price)[0]
        newitem.save()

        cardtype = Cardtype.objects.get_or_create(company=company,cardtype=item.svrcdoe,cardname=item.svrname,comptype='times',prncomptype='times')[0]
        cardtype.save()

        servieceprice = Servieceprice.objects.get_or_create(company=company,srvcode=item.svrcdoe, srvuuid=item,qty=1,price=item.price,amount=item.price)[0]
        servieceprice.save()

    items = Goods.objects.filter(company='yfy',flag='Y',saleflag='Y',valiflag='Y',brand='AEB')
    for item in items:
        print('g_item',item.gcode,item.gname )
        newitem = Goods.objects.get_or_create(company='demo',gcode=item.gcode,gname=item.gname, price=item.price)[0]
        newitem.save()

    items = Cardtype.objects.filter(company='yfy',flag='Y',saleflag='Y',valiflag='Y',comptype='amount')
    for item in items:
        print('c_item',item.cardtype,item.cardname )
        newitem = Cardtype.objects.get_or_create(company='demo',cardtype=item.cardtype,cardname=item.cardname, price=item.price)[0]
        newitem.save()

    return HttpResponse("完成！", content_type="application/json")

def transappoptionstolist(request):
    print(common.constants.BRAND)
    segs = ['brand','displayclass1']
    for item in segs:
        print(item)
        seg = item
        appoption = Appoption.objects.filter(company=common.constants.COMPANYID).filter(seg=seg).values_list('itemname','itemvalues')
        print(appoption)

    return HttpResponse("完成！", content_type="application/json")

def listtoappoption(request):
    tags = common.constants.TAGS
    for tag in tags:
        print(tag)
        print(tag[0],tag[1])
        try:
            app = Appoption.objects.get(company=common.constants.COMPANYID, seg='tags', itemname=tag[0],itemvalues=tag[1])
            print(app ,' skipped')
        except:
            app = Appoption.objects.create(company=common.constants.COMPANYID,seg='tags',itemname=tag[0],itemvalues=tag[1])
            app.save()
            print(app ,' created')

    return HttpResponse("完成！", content_type="application/json")

def fromsql_to_appoption(request):
    company='youlan'
    read = connectdb('mysql')
    Rcursor = read.cursor()

    getclass_sql =   " select parent,value,name " \
                     " from srvclass " \
                     " where  value in ('1','2','3','4','5','6','7','8')"
    seg ='displayclass1'

    Rcursor.execute(getclass_sql)
    readResult = Rcursor.fetchall()

    for value in readResult:
        try:
            app = Appoption.objects.get(company=common.constants.COMPANYID, seg=seg, itemname=value[1])
            print(app ,' skipped')
        except:
            app = Appoption.objects.create(company=common.constants.COMPANYID,seg=seg,itemname=value[1],itemvalues=value[2])
            app.save()
            print(app ,' created')

    disconnectdb(read)
    return HttpResponse("完成！", content_type="application/json")

def connectdb(server):
    if server == 'mysql':
        read = pymysql.connect("youlan.softweb.net.cn", "sa", "shgv2014", "youlan")

    if server =='mssql':
        read = pymssql.connect(server='localhost', user='sa',password='shgv2014', database='BigideaR')

    return read

def disconnectdb(read):
    read.close()

    return 0

def ReadAndWrite(request):
    return 0

# for youlan
def GoodsReadAndWrite(request):
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
        try:
            goods = Goods.objects.get(company=company,gcode=value[0])
            print(goods.gcode,goods.gname,'skipped！')
        except:
            goods = Goods.objects.create(gcode=value[0],gname=value[1],spec=value[2],rptcode1=value[3],buyprc=value[4],price=value[5],minivalues=value[6],maxvalues=value[7],company=company)
            goods.save()
            print(goods.gcode,goods.gname,'created')

    disconnectdb(read)
    return HttpResponse("完成！", content_type="application/json")

# for youlan
def ServieceReadAndWrite(request):
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 服务基本信息
    readsql =   " select fldItemcode,fldItemname1,flditemtype,fldremark,fldtag,fldstandardprice,fldexperienceprice,fldtimelen " \
                " from  viewItem  " \
                " where 1=1 and  fldcompanycode='000' "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    # print(readResult.count())

    for value in readResult:
        try:
            srv = Serviece.objects.get(company=company,svrcdoe=value[0])
            print(srv.svrcdoe,srv.svrname,'skipped！')
        except:
            srv = Serviece.objects.create(svrcdoe=value[0],svrname=value[1],rptcode1=value[2],price=value[5],price2=value[6],stdmins=value[7],company=company)
            srv.save()
            print(srv.svrcdoe,srv.svrname,'created')

    disconnectdb(read)


    return HttpResponse("完成！", content_type="application/json")

# for youlan
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
    return HttpResponse("完成！", content_type="application/json")

# for youlan
def CardinfoReadAndWrite(request):
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
                cardtype = Cardtype.objects.get(company=common.constants.COMPANYID, cardtype=value[3])
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
    return HttpResponse("完成！", content_type="application/json")


# for youlan
def EmplReadAndWrite(request):
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 员工信息
    readsql =   " select fldCompanyCode,fldEmployeeCode,fldName1,fldEmployeeStatus,fldIdentityNo,fldDepartmentCode,fldPositionCode" \
                " from  tblHREmployee  " \
                " where fldEmployeeStatus <> 1"


    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        print(value)
        empl = Empl.objects.update_or_create(company=common.constants.COMPANYID,storecode=value[0],ecode=value[1],ename=value[2],status=value[3],cardno=value[4],team=value[5],position=value[6])
        print(empl,' finished')
        # try:
        #     cardtype = Cardtype.objects.get(company=company,cardtype=value[0])
        #     print(cardtype.cardtype,cardtype.cardname,'skipped！')
        # except:
        #     print(value,'will be created')
        #     cardtype= Cardtype.objects.create(cardtype=value[0],cardname=value[1],suptype=value[2],mnemoniccode=value[3],leftmoney=value[4],price=value[5] ,price2=value[6],cardnote=value[7],company=company)
        #     cardtype.save()
        #     print(cardtype.cardtype,cardtype.cardname,'created')

    disconnectdb(read)
    return HttpResponse("完成！", content_type="application/json")

# for youlan
def CardtypeReadAndWrite(request):
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 卡类信息
    readsql =   " select fldmembercardtypecode, flddescription1, fldCategoryCode, fldmnemoniccode, fldamounts,  fldStandardPrice, fldActualPrice, fldmemo" \
                " from  viewMemberCardType  " \
                " where  fldcompanycode='000' and fldstatus=0  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()
    print(len(readResult))

    for value in readResult:
        cardtype = Cardtype.objects.update_or_create(cardtype=value[0], cardname=value[1], suptype=value[2],
                                           mnemoniccode=value[3][:15], leftmoney=value[4], price=value[5], price2=value[6],
                                           cardnote=value[7], company=company)
        # cardtype.save()
        print(cardtype, 'finished')

        # print(value)
        # try:
        #     cardtype = Cardtype.objects.get(company=company,cardtype=value[0])
        #     print(cardtype.cardtype,cardtype.cardname,'skipped！')
        # except:
        #     print(value,'will be created')
        #     cardtype= Cardtype.objects.create(cardtype=value[0],cardname=value[1],suptype=value[2],mnemoniccode=value[3],leftmoney=value[4],price=value[5] ,price2=value[6],cardnote=value[7],company=company)
        #     cardtype.save()
        #     print(cardtype.cardtype,cardtype.cardname,'created')

    disconnectdb(read)
    return HttpResponse("完成！", content_type="application/json")

# for youlan
def CardtypeItemDetailReadandWrite(request):
    company='youlan'
    read = connectdb('mssql')
    Rcursor = read.cursor()

    # 卡类信息
    readsql =   " select fldmembercardtypecode, flddescription1, fldCategoryCode, fldmnemoniccode, fldamounts,  fldStandardPrice, fldActualPrice, fldmemo" \
                " from  viewMemberCardType  " \
                " where  fldcompanycode='000'  "

    readsql1 = " SELECT 'P' stype, 'itemtype' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemType itemcode, b.fldMaxTimes times, b.fldAveragePrice price, b.fldPerformance "\
               " FROM tblmembercardtype a, tblMemberCardTypeFavourItemType b "\
               " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode"

    readsql2 =  " SELECT 'N'stype, 'itemtype' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemType itemcode, b.fldMaxTimes times, b.fldAveragePrice price, b.fldPerformance"\
                " FROM tblmembercardtype a, tblMemberCardTypeDefaultItemType b"\
                " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode "

    readsql3=   " SELECT 'P' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance "\
                " FROM tblmembercardtype a, [BigideaR].[dbo].[tblMemberCardTypeFavourItemDetails] b " \
                " where a.fldMemberCardTypeCode = b.fldMemberCardTypeCode"

    readsql4=   " SELECT 'N' stype, 'itemcode' codetype, a.fldMemberCardTypeCode, a.fldDescription1, b.fldLineNumber, b.fldItemCode itemcode, b.fldTimes times, b.fldStandardPrice price, b.fldPerformance "\
                " FROM tblMemberCardType a, tblMemberCardTypeDefaultItemDetails b where 1 = 1 and a.fldMemberCardTypeCode = b.fldMemberCardTypeCode"

    sqls = (readsql1,readsql2,readsql3,readsql4)
    for sql in sqls:
        readsql = sql
        print(readsql)
        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()
        print(len(readResult))

        for value in readResult:
            print(value)
            # by sql update
            # srv = Serviece.objects.get(company=common.constants.COMPANYID,rptcode6=value[5])
            # update youlan.oldcardtypeitemdetail a, serviece b
            # set a.itemcode = b.svrcdoe
            # where a.codetype = 'itemcode' and a.itemcode = b.rptcode6 and b.svrcdoe <> b.rptcode6;
            # print(srv)

            oldcardtypeitemdetail = OldCardTypeItemDetail.objects.update_or_create(stype=value[0],codetype=value[1],cardtype=value[2], cardname=value[3],linenumber=value[4],
                                               itemcode=value[5],times=value[6], price=value[7], performance=value[7],company=company)
            print(oldcardtypeitemdetail, 'finished')

            # try:
            #     promotions = Promotions.objects.get(company=common.constants.COMPANYID,promotionsid=value[2])
            #     print(promotions,'is exists')
            # except:
            #     promotions =  Promotions.objects.create(company=common.constants.COMPANYID,promotionsid=value[2],promotionsname=value[3])
            #     print(promotions,'is created')
            #
            #
            # promotionsdetails = Promotionsdetail.update_or_create(company=common.constants.COMPANYID,flag='Y',ttype='C',
            #                                                           sgccode=oldcardtypeitemdetail.newitemcode,s_qty=value[6],s_price=value[7],s_amount=value[6]*value[7])
            # print(promotionsdetails,'is finished!')
            # print(value)
            # try:
            #     cardtype = OldCardTypeItemDetail.objects.get(stype=value[0],codetype=value[1],cardtype=value[2], cardname=value[3],linenumber=value[4],
            #                                    itemcode=value[5],times=value[6], price=value[7], performance=value[7],company=company)
            #     print(cardtype.cardtype,cardtype.cardname,'skipped！')
            # except:
            #     print(value,'will be created')
            # oldcardtypeitemdetail = OldCardTypeItemDetail.objects.update_or_create(stype=value[0], codetype=value[1],
            #                                                                        cardtype=value[2], cardname=value[3],
            #                                                                        linenumber=value[4],
            #                                                                        itemcode=value[5], times=value[6],
            #                                                                        price=value[7], performance=value[7],
            #                                                                        company=company)
            #     cardtype.save()
            #     print(cardtype.cardtype,cardtype.cardname,'created')

    disconnectdb(read)

    return HttpResponse("完成！", content_type="application/json")

# for youlan
def  InitPromotionsInfo(request):
    company='youlan'
    oldcardtypeitems = OldCardTypeItemDetail.objects.filter(company=company,codetype='itemcode').filter(linenumber__gt=1).values('cardtype','cardname').distinct()
    print(oldcardtypeitems)
    for item in oldcardtypeitems:
        print(item)
        promotionsid = item['cardtype']
        promotionsname = item['cardname']
        mainttype='30'
        try:
            promotions = Promotions.objects.get(company=company,promotionsid=promotionsid,promotionsname=promotionsname,mainttype=mainttype)
        except:
            promotions = Promotions.objects.create(company=company,promotionsid=promotionsid,promotionsname=promotionsname,mainttype=mainttype)
            promotions.save()

        itemdetails = OldCardTypeItemDetail.objects.filter(company=company,cardtype=promotionsid).order_by('linenumber')
        for itemdetail in itemdetails:
            print(itemdetail,itemdetail.newitemcode)
            try:
                promotionsdetail = Promotionsdetail.objects.get(company=company,promotionsuuid=promotions,promotionsid=promotions.promotionsid,
                                                                promotionsseq=itemdetail.linenumber,ttype='C',sgcode=itemdetail.newitemcode,
                                                                s_qty = itemdetail.times,s_price = itemdetail.price,
                                                                promotionsqty=itemdetail.times,
                                                                promotionsprice=itemdetail.price,
                                                                promotionsamount= itemdetail.times * itemdetail.price,
                                                                stype=itemdetail.stype)
                print(promotionsdetail, ' is skipped')
            except:
                promotionsdetail = Promotionsdetail.objects.create( company=company,promotionsuuid=promotions,promotionsid=promotionsid,
                                                                    promotionsseq=itemdetail.linenumber,ttype='C',sgcode=itemdetail.newitemcode,
                                                                    s_qty = itemdetail.times,s_price = itemdetail.price, s_amount=itemdetail.times*itemdetail.price,
                                                                    promotionsqty=itemdetail.times,
                                                                    promotionsprice=itemdetail.price,
                                                                    promotionsamount=itemdetail.times * itemdetail.price,
                                                                    stype=itemdetail.stype)
                promotionsdetail.save()
                print(promotionsdetail,' is created')

    return HttpResponse("完成！", content_type="application/json")

# 根据服务项目，产生相应的疗程卡信息
def GenerateCardTypeByServiece(request):
    company=request.GET['company']
    servieces = Serviece.objects.filter(company=company).filter(flag='Y',valiflag='Y',saleflag='Y').filter(topcode='100')
    COMPTYPE='times'
    SUPTYPE='20'
    for srv in servieces:
        try:
            cardtype = Cardtype.objects.get(company=company, cardtype=srv.svrcdoe)
            cardtype.ttype='S'
            cardtype.price=srv.price,
            cardtype.leftmoney=srv.price,
            cardtype.brand=srv.brand
            cardtype.displayclass1=srv.displayclass1
            cardtype.displayclass2=srv.displayclass2
            cardtype.financeclass1=srv.financeclass1
            cardtype.financeclass2=srv.financeclass2
            cardtype.marketclass1=srv.marketclass1
            cardtype.marketclass2=srv.marketclass2
            cardtype.marketclass3=srv.marketclass3
            cardtype.marketclass4=srv.marketclass4
            cardtype.mnemoniccode=srv.mnemoniccode
            cardtype.saleflag=srv.saleflag,
            cardtype.valiflag=srv.valiflag,
            cardtype.sguuid=srv.uuid,
            cardtype.valdatetype='10'
            cardtype.save()
            print(srv.svrcdoe,srv.svrname,cardtype, ' is updated!')
        except:
            cardtype = Cardtype.objects.create(company=company,cardtype=srv.svrcdoe,cardname=srv.svrname,ttype='S',valiflag=srv.valiflag,saleflag=srv.saleflag,
                                               brand=srv.brand,displayclass1=srv.displayclass1,displayclass2=srv.displayclass2,financeclass1=srv.financeclass1,financeclass2=srv.financeclass2,
                                               marketclass1=srv.marketclass1,marketclass2=srv.marketclass2,marketclass3=srv.marketclass3,mnemoniccode=srv.mnemoniccode,
                                               comptype=COMPTYPE,prncomptype=COMPTYPE,suptype=SUPTYPE,sguuid=srv.uuid,tags=srv.tags,valdatetype='10')
            cardtype.price=srv.price
            cardtype.leftmoney=srv.price
            cardtype.save()
            print(srv.svrcdoe,srv.svrname,cardtype, ' is created')

        try:
            servieceprice = Servieceprice.objects.get(company=company,srvcode=srv.svrcdoe,qty=1)
            print(servieceprice,' is skipped')
        except:
            servieceprice = Servieceprice.objects.create(company=company,srvuuid=srv,srvcode=srv.svrcdoe,qty=1,price=srv.price,amount=srv.price)
            servieceprice.save()
            print(servieceprice,' is created')

    return HttpResponse("完成！", content_type="application/json")

# 把导入的会员信息重新编号
def reordervip(request):
    company=request.GET['company']
    cnt=1
    codelength=5

    print('company',company)

    if company=='yiren':
        vips = Vip.objects.filter(company='yiren', flag='Y', storecode='03',viptype='10', vcode__isnull=False).order_by('vcode')
        print('vips',len(vips))
        for vip in vips:
            print('vip',vip.vcode, vip.vname)
            vcode = vip.storecode + ('000000' + str(cnt + 1))[-codelength:]
            print(vcode)
            cnt = cnt + 1
            vip.vcode = vcode
            vip.save()

        return HttpResponse("完成！", content_type="application/json")
    else:
        vips=Vip.objects.filter(company=company,flag='Y',storecode='01',vcode__isnull=False).order_by('vcode')
        for vip in vips:
            vcode = vip.storecode + ('000000'+ str(cnt+1))[-codelength:]
            print(vcode)
            cnt =cnt+1
            vip.vcode=vcode
            vip.save()

        return HttpResponse("完成！", content_type="application/json")

# 把导入的会员信息重新编号
def reorderitem(request):
    company=request.GET['company']
    # ttype=request.GET['ttype']
    cnt=1
    codelength=5

    BRANDLIST=Appoption.objects.filter(company=company,flag='Y',seg='brand').values_list('itemname')

    # print('company',company,BRANDLIST)

    if company=='yiren':
        for brand in BRANDLIST:
            print('brand',brand[0])
            # srvs = Serviece.objects.filter(company='yiren',  displayclass1='20',displayclass2='20').order_by('displayclass1','displayclass2','brand','svrcdoe')
            items = Goods.objects.filter(company='yiren',flag='Y',brand=brand[0]).order_by('brand')
            print('items',len(items))
            for item in items:
                print('item',item.gcode, item.gname)
                itemcode = item.brand + ('000000' + str(cnt + 1))[-codelength:]
                print(itemcode)
                cnt = cnt + 1
                item.gcode = itemcode
                item.save()

        return HttpResponse("完成！", content_type="application/json")
    else:
        # vips=Vip.objects.filter(company=company,flag='Y',storecode='88',vcode__isnull=False).order_by('vcode')
        # for vip in vips:
        #     vcode = vip.storecode + ('000000'+ str(cnt+1))[-codelength:]
        #     print(vcode)
        #     cnt =cnt+1
        #     vip.vcode=vcode
        #     vip.save()

        return HttpResponse("完成！", content_type="application/json")

class CheckData(object):
    def __init__(self,**kwargs):
        self.company = kwargs.get('company','demo')
        self.storecode = kwargs.get('storecode','88')
        self.fromdate = kwargs.get('fromdate','')
        self.todate = kwargs.get('todate','')
        self.transuuid = kwargs.get('transuuid','')
        self.exptxserno = kwargs.get('exptxserno','')

    def checkbytransuuid(self):
        try:
            expvstoll = Expvstoll.objects.get(company=self.company, uuid=self.transuuid)
            expvstoll.set_oldcustflag()
            expvstoll.set_paymoderatio()
            expvstoll.set_cardhistory()
            expvstoll.set_transgoodstranslog()
            expvstoll.set_vipiteminfo()

            # expenses = Expense.objects.filter(company=self.company,transuuid=expvstoll)
        except:
            print('error')



def dailycheck(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    fromdate =  request.GET['fromdate']
    todate =  request.GET['todate']

    trans = Expvstoll.objects.filter(flag='Y',valiflag='Y',company=company, storecode=storecode,vsdate__gte=fromdate,vsdate__lte=todate).order_by('create_time','exptxserno')
    for tran in trans:
        # tran.set_oldcustflag()
        # tran.set_paymoderatio()
        # tran.set_cardhistory()
        # tran.set_transgoodstranslog()
        tran.set_vipiteminfo()
        # param={
        #     'company':tran.company,
        #     'storecode':tran.storecode,
        #     'transuuid':tran.uuid
        # }
        # check = CheckData(**param)
        # check.checkbytransuuid()

    return HttpResponse("完成！", content_type="application/json")