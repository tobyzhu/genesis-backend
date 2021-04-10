
from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from datetime import datetime
from django.core import serializers
from django.db.models import Avg,Sum,Count
import pymysql
import uuid

from jmj.models import ReportPeriod,PeriodData,OldData
from baseinfo.models import Goods,Storeinfo,Wharehouse,Vip
from cashier.models import Expvstoll,Expense
from goods.models import Goodstranslog,Salehead,Saledtl,Transhead,Transdtl
import common.constants

# Create your views here.

def ReadAndWrite(fromdate, todate):
    # for i in range(len(readDB)):
    #     fromdate ='20190101'
    #     todate ='20190102'

        read = pymysql.connect("qdxhz.imwork.net", "sa", "shgv2014", "genesis")
        Rcursor = read.cursor()
        # readsql = "  select sukid,saleatr, vdate,tmount, '1-2' storecode, '1-2' whcode, seqbar,a.gcode gcode, disc, qty1,qty2,qty3, price1, amount1 "\
        #           "  from goodstranslog a, goods b "\
        #           "  where 1=1 "\
        #           "  and a.vdate between "+ fromdate +" and " + todate + "  "\
        #           "  and a.gcode = b.gcode "\
        #           "  and b.brand='900' "


        readsql = "  select sukid,saleatr, vdate,tmount, '1' storecode, '1-2' whcode, seqbar,a.gcode gcode, disc, qty1,qty2,qty3, price1, amount1 " \
                  "  from goodstranslog a, goods b " \
                  "  where 1=1 " \
                  "and  a.saleatr = 'G' and a.vdate between " + fromdate + " and " + todate + "  " \
                                                                           "  and a.gcode = b.gcode " \
                                                                           "  and b.brand='900' and sukid='01_EXPVSTOLL_28504' "

        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()
        for value in readResult:
            write = pymysql.connect("101.200.55.5", "sa", "shgv2014", "multistore")
            Wcursor = write.cursor()
            getgcodemirrorsql = "select gcode2011 from gcodemirror where gcode ='" +value[7]+"'"
            print(getgcodemirrorsql)
            Wcursor.execute(getgcodemirrorsql)
            gcode = Wcursor.fetchone()[0]
            print('gcodemirror',value[2],value[7],gcode)
            checkcdr = "select sukid from goodstranslog where sukid='"+value[0]+"' and seqbar='"+ value[6]+"' and saleatr='G' and storecode= '" + value[4] +"' "
            print(checkcdr)
            Wcursor.execute(checkcdr)
            print(Wcursor.fetchone()[0],Wcursor.rownumber,Wcursor.rowcount,Wcursor.connecti)
            cnt = Wcursor.rowcount
            print('cnt,gcode,len',cnt,gcode,len(gcode))
            if cnt == 0 and len(gcode) > 0:
                print('before writesql')
                writeSql = "INSERT INTO goodstranslog(sukid,saleatr,vdate,tmount,storecode,whcode,seqbar,gcode,disc,qty1,qty2,qty3,price1,amount1,company,companyid) " \
                           " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', '%s'  )" %\
                           (value[0], value[1], value[2], value[3], value[4],value[5], value[6], gcode, value[8], value[9],value[10], value[11], value[12], value[13],'JMJ','JMJ' )
                print('after writesq;',writeSql)
                try:
                    Wcursor.execute(writeSql)
                    print('before commit')
                    write.commit()
                    print('1','1-2',value[2],value[5],value[6],'inserted')
                except:
                    write.rollback()
                    print('2','1-2',value[2],value[5],value[6],'rollback')
                print('before close')
                write.close()
                print('after close')
            else:
                print('skip')
        read.close()
        return 0

# 补传销售单据到goodstranslog
def FillSalesTransToLog(company,storecode,fromdate, todate):
    trans2 = Expvstoll.objects.filter(company=company,storecode=storecode,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate,exptxserno='yfy03_EXPVSTOLL_12870').order_by('vsdate')

    for tran2 in trans2:
        vip = Vip.objects.get(company=company, flag='Y', uuid=tran2.vipuuid.uuid)
        if vip.vcode ==None:
            vip.vcode=''
        if vip.vname==None:
            vip.vname=''

        try:
            tx = Goodstranslog.objects.get(company=company,storecode=tran2.storecode,sukid=tran2.exptxserno)
            # tx =  Goodstranslog.objects.get(company=company,storecode=tran2.storecode,transuuid=tran2.uuid)
            print(tran2.exptxserno,tran2.vsdate,'skipped')
        except:
            items = Expense.objects.filter(company=company).filter(storecode=tran2.storecode,ttype='G',transuuid=tran2)
            store = Storeinfo.objects.get(company=company,storecode=tran2.storecode)
            for item in items:
                try:
                    # goodstranslog = Goodstranslog.objects.get(company=company,transuuid=item.transuuid,seqbar=item.ditem)
                    goodstranslog = Goodstranslog.objects.get(company=company,exptxserno=item.exptxserno,seqbar=item.ditem)
                    print('1')
                    print('2',str(uuid.uuid4()).replace('-','') )
                    # print('2')
                    goodstranslog.uuid =str(uuid.uuid4()).replace('-','')
                    print('goodstranslog.uuid',goodstranslog.uuid)
                    # goodstranslog.vdate=tran2.vsdate
                    # goodstranslog.sumdisc=tran2.sumdisc
                    # goodstranslog.tmount=tran2.totmount
                    # goodstranslog.ecode=tran2.ecode
                    # goodstranslog.companyid=tran2.company
                    # goodstranslog.storecode=tran2.storecode
                    # goodstranslog.whcode=store.salewhcode
                    # goodstranslog.gcode=item.srvcode
                    # goodstranslog.qty1=item.s_qty
                    # goodstranslog.price1=item.s_price
                    # goodstranslog.amount1=item.s_mount
                    # goodstranslog.company=tran2.company
                    # goodstranslog.creater=tran2.creater
                    # goodstranslog.transuuid=tran2.uuid
                    # goodstranslog.transdesc=vip.vname+'-'+vip.vcode
                    goodstranslog.save()
                    print(goodstranslog.sukid,goodstranslog.gcode,'is skipped!')
                except:
                    goodstranslog = Goodstranslog.objects.create(sukid=tran2.exptxserno,saleatr=item.ttype,vdate=tran2.vsdate,sumdisc=tran2.sumdisc,
                                                 tmount=tran2.totmount,ecode=tran2.ecode,
                                                 companyid=tran2.company,storecode=tran2.storecode,whcode=store.salewhcode,
                                                 seqbar=item.ditem,gcode=item.srvcode,qty1=item.s_qty,price1=item.s_price,amount1=item.s_mount,uuid=str(uuid.uuid4()).replace('-',''),
                                                 company=tran2.company,creater=tran2.creater,transuuid=tran2.uuid,transdesc=vip.vname+'-'+vip.vcode,ioflag='1')
                    goodstranslog.set_qty2()
                    goodstranslog.set_qty3()
                    print(goodstranslog.sukid,goodstranslog.gcode,'is created!')



    return 0

# 从goodstranslog中删除掉作废的商品销售单记录
def DelInvaildTrans(company, fromdate,todate):
    trans2 = Expvstoll.objects.filter(company=company,flag='N').filter(valiflag='N').filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate)
    print(trans2)

    for tran2 in trans2:
        try:
            txs = Goodstranslog.objects.filter(company=company, storecode=tran2.storecode, sukid=tran2.exptxserno)
            for tx in txs:
                tx.delete()
                # tx.save()
                print(tran2.exptxserno, ' deleted')
        except:
            print(tran2.exptxserno,  'skipped!')

    return 0

# 已经转出确认，但goodstranglog中没有记录，目前yfy总部转出经常出现这个问题
# def FillTransdtl(request):
def FillTransdtl(company, fromdate):
    # try:
    #     fromdate=request.GET['fromdate']
    # except:
    #     fromdate='20190901'

    uuid=''
    saleatr='TO'
    doccode=''
    trans2 = Transhead.objects.filter(flag='Y',company=company,vdate__gte=fromdate,status='20')
    print(fromdate,trans2)

    for tran2 in trans2:
        print(tran2.company,tran2.outstore,tran2.outwhcode,saleatr,tran2.sukid, tran2.doccode)

        logs = Goodstranslog.objects.filter(company=tran2.company,storecode=tran2.outstore,whcode=tran2.outwhcode,sukid=tran2.sukid,saleatr=saleatr).count()
        print('logs exists counts:',logs)
        if logs==0:
            print('create:', tran2.outstore, tran2.outwhcode, tran2.sukid, tran2.doccode)
            items = Transdtl.objects.filter(company=tran2.company).filter(transheadid_id=tran2.uuid)
            for item in items:
                print('create:',tran2.outstore,tran2.outwhcode,tran2.sukid,tran2.doccode,item.seqbar,item.gcode,item.qty)
                goodstranslog = Goodstranslog.objects.create(sukid=tran2.sukid,doccode=tran2.doccode,saleatr=saleatr,vdate=tran2.vdate,sumdisc=tran2.smndisc,
                                             tmount=tran2.tmount,ecode=tran2.ecode,
                                             companyid=tran2.company,storecode=tran2.outstore,whcode=tran2.outwhcode,
                                             seqbar=item.seqbar,gcode=item.gcode,qty1=item.qty,price1=item.price,amount1=item.mount,
                                             company=tran2.company,creater='sys_filler')
                print('created:',goodstranslog.gcode,goodstranslog.saleatr)
                goodstranslog.set_qty2()
                goodstranslog.set_qty3()
                # goodstranslog.save()

    return HttpResponse(0, content_type="application/json")

def ProcessDupGoodstranslog(request):
    company=request.GET['company']
    presukid=''
    preseqbar=''
    cnt=0
    saleatr='G'
    # sukid='00_salehead_72'
    trans = Goodstranslog.objects.filter(company=company,saleatr=saleatr,create_time__gte='2021-03-19').order_by('sukid','seqbar')
    for tran in trans:
        # print(tran.sukid,tran.seqbar)
        thissukid=tran.sukid
        thistransuuid = tran.transuuid
        thisseqbar=tran.seqbar
        trans2= Goodstranslog.objects.filter(company=company,saleatr=saleatr,transuuid=tran.transuuid,seqbar=tran.seqbar).order_by('gtranukid')
        cnt=1
        for tran2 in trans2:
            if cnt >1:
                tran2.areacode='N'
                print(tran2.sukid,tran2.seqbar,tran2.gcode,tran2.gtranukid,'is dup!')
                tran2.save()
            cnt =cnt+1

    return HttpResponse(0, content_type="application/json")

def RecalcuteGoodsTransLog(company, storecode, fromdate,todate):
    whcodes = Wharehouse.objects.filter(flag='Y',company=company,storecode=storecode)
    # print(whcodes)
    for whcode in whcodes:
        print(whcode)

        goodstranslogs = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,vdate__gte=fromdate,vdate__lte=todate).order_by('gtranukid')
        for goodstranslog in goodstranslogs:
            goodstranslog.set_qty2()
            goodstranslog.set_qty3()

        # goods2 = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode).values('whcode','gcode').distinct().order_by('gcode')
        # for i in range(len(goods2)):
        #     gcode = goods2[i]['gcode']
        #     transqty2logs =Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode).filter(gcode=gcode).filter(vdate__gte=fromdate).filter(vdate__lte=todate).order_by('gtranukid')
        #     for transqty2log in transqty2logs:
        #         transqty2log.set_qty2()
        #         print(whcode.wharehousename,transqty2log.gcode,transqty2log.gtranukid,'set qty2 finished!')
        #
        #     goodswithvaldate = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,gcode=gcode).values('gcode','goodsvaldate').distinct().order_by('gcode','goodsvaldate')
        #     # print(goodswithvaldate)
        #     for i in range(len(goodswithvaldate)):
        #         transqty3logs = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode).filter(vdate__gte=fromdate).filter(vdate__lte=todate).filter(gcode=goodswithvaldate[i]['gcode']).filter(goodsvaldate=goodswithvaldate[i]['goodsvaldate']).order_by('gtranukid')
        #         for transqty3log in transqty3logs:
        #             transqty3log.set_qty3()
        #             print(whcode.wharehousename,transqty3log.gcode,'set qty3 finished!')


    return HttpResponse(0, content_type="application/json")

# 按门店重新计算goodstranslog的库存数据
def RecalcuteGoodsTransLogByStorecode(request):
    try:
        company=request.GET['company']
    except:
        company='demo'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='00'

    try:
        fromdate= request.GET['fromdate']
    except:
        fromdate= datetime.strftime(datetime.today(),'%Y%m%d')
        print(datetime.strftime(datetime.today(),'%Y%m%d'))

    try:
        todate= request.GET['todate']
    except:
        todate= datetime.strftime(datetime.today(),'%Y%m%d')
        print(datetime.strftime(datetime.today(),'%Y%m%d'))

    whcodes = Wharehouse.objects.filter(flag='Y',company=company,storecode=storecode)
    for whcode in whcodes:
        print(whcode)
        goodstranslogs = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,vdate__gte=fromdate,vdate__lte=todate).order_by('gtranukid')
        for goodstranslog in goodstranslogs:
            goodstranslog.set_qty2()
            goodstranslog.set_qty3()

        # goods2 = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode).values('whcode','gcode').distinct().order_by('gcode')
        # for i in range(len(goods2)):
        #     # print('good',goods2[i]['gcode'])
        #     gcode = goods2[i]['gcode']
        #     transqty2logs =Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode).filter(gcode=gcode).filter(vdate__gte=fromdate).order_by('gtranukid')
        #     for transqty2log in transqty2logs:
        #         transqty2log.set_qty2()
        #         print(whcode.wharehousename,transqty2log.gcode,transqty2log.gtranukid,'set qty2 finished!')
        #
        #     goodswithvaldate = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,gcode=gcode).values('gcode','goodsvaldate').distinct().order_by('gcode','goodsvaldate')
        #     # print(goodswithvaldate)
        #     for i in range(len(goodswithvaldate)):
        #         transqty3logs = Goodstranslog.objects.filter(whcode=whcode.wharehousecode).filter(vdate__gte=fromdate).filter(gcode=goodswithvaldate[i]['gcode']).filter(goodsvaldate=goodswithvaldate[i]['goodsvaldate']).order_by('gtranukid')
        #         for transqty3log in transqty3logs:
        #             transqty3log.set_qty3()
        #             print(whcode.wharehousename,transqty3log.gcode,'set qty3 finished!')

    return HttpResponse(0, content_type="application/json")

def daily():
    company='yiren'
    fromdate = ( datetime.date.today() + datetime.timedelta(days=-1) ).strftime('%Y%m%d')
    todate = datetime.date.today().strftime('%Y%m%d')

    trans = Expvstoll.objects.filter(company=company, flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    for tran in trans:
        tran.set_oldcustflag()

    return 0

def ProcessGoods(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storelist = request.GET['storelist']
    except:
        storelist = ['00','01','02','03','04']

    fromdate = request.GET['fromdate']
    todate = request.GET['todate']

    # trans = Expvstoll.objects.filter(company=company, flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)

    # for tran in trans:
    #     tran.set_oldcustflag()
    print(company,fromdate,todate)

    if company=='JMJ':
        # 从营业部取吉祥物销售数据 到JMJ系统
        ReadAndWrite(fromdate,todate)
        #
        # 把JMJ作废的交易，从GOODSTRANSLOG中取消

        DelInvaildTrans(company,fromdate,todate)

    # 把未记录goodstranslog的销售记录，补充进去
    FillSalesTransToLog(company,'05',fromdate,todate)


    # 作废的交易，从GOODSTRANSLOG中取消
    # DelInvaildTrans(company,fromdate,todate)

    #重新计算GOODSTRANSLOG中qty2, qty3
    for storecode in storelist:
    #    RecalcuteGoodsTransLog(company,storecode,fromdate,todate)
        print(storecode)
    return HttpResponse("完成！", content_type="application/json")

def tmp_f(request):
    company='yiren'
    storelist =('01','02','03','04')
    fromdate = '20200510'
    todate = '20200612'
    goodstrans = Goodstranslog.objects.filter(company=company,storecode__in=storelist,saleatr='G',vdate__gte=fromdate,vdate__lte=todate,qty2__lt=0)
    for goodstx in goodstrans:
        tranx = Expvstoll.objects.get(company=company,uuid=goodstrans.transuuid)
        gcodetransdetail = Goodstranslog.objects.filter(company=company,storecode=goodstx.storecode,vdate__gte=fromdate)
        # if

