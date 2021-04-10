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
from baseinfo.models import Goods,Storeinfo,Wharehouse
from cashier.models import Expvstoll,Expense
from goods.models import Goodstranslog,Salehead,Saledtl


REPORTYEAR='2021'
RPTCODE1='2021'
YEARFROMDATE='20201219'
REPORTFROMDATE='20201201'

def ReadAndWrite(request):
        fromdate=request.GET['fromdate']
        todate=request.GET['todate']

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
                                                                           "  and b.brand='900'"
        print('readsql',readsql)
        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()
        for value in readResult:
            # write = pymysql.connect("localhost", "sa", "shgv2014", "multistore")
            write = pymysql.connect("101.200.55.5", "sa", "shgv2014", "multistore")
            Wcursor = write.cursor()
            getgcodemirrorsql = "select gcode2011 from gcodemirror where gcode ='" +value[7]+"'"
            print('value[7]=',value[7],getgcodemirrorsql)
            Wcursor.execute(getgcodemirrorsql)
            gcode = Wcursor.fetchone()[0]
            print(value[2],value[7],'gcode',gcode,'value[4]',value[4])
            checkcdr = "select sukid from goodstranslog where sukid='"+value[0]+"' and seqbar='"+ value[6]+"' and saleatr='G' and storecode= '" + value[4] +"' "
            print('checkcdr',checkcdr)
            Wcursor.execute(checkcdr)
            cnt = Wcursor.rowcount
            print('cnt=',cnt,'gcode=',gcode)

            if cnt == 0 and len(gcode)>0:
                writeSql = "INSERT INTO goodstranslog(sukid,saleatr,vdate,tmount,storecode,whcode,seqbar,gcode,disc,qty1,qty2,qty3,price1,amount1) " \
                           " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', '%s'  )" %\
                           (value[0], value[1], value[2], value[3], value[4],value[5], value[6], gcode, value[8], value[9],value[10], value[11], value[12], value[13] )
                print(writeSql)
                try:
                    Wcursor.execute(writeSql)
                    write.commit()
                except:
                    write.rollback()
                write.close()
            else:
                print('skip')
        read.close()
        # return 0
        return HttpResponse('Finished！', content_type="application/json")


# 从goodstranslog中删除掉作废的商品销售单记录
def DelInvaildTrans(request):
    company=request.GET['company']
    fromdate=request.GET['fromdate']
    todate=request.GET['todate']

    # company = 'JMJ'
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

    # return 0

    return HttpResponse('Finished！', content_type="application/json")
# def InitPeriodData(company,reportyear, rptcode1):

def InitPeriodData(request):
    company = request.GET['company']
    reportyear = request.GET['reportyear']
    rptcode1= request.GET['rptcode1']

    stores = Storeinfo.objects.filter(company=company)
    print('stores',stores)
    for store in stores:
        # goodslist=['20721']
        goods = Goods.objects.filter(company=company,rptcode1=rptcode1)
        # print('goods',goods)
        for good in goods:
            print('goods:', good.gcode)
            reportperiods = ReportPeriod.objects.filter(reportyear=reportyear)
            for reportperiod in reportperiods:
                if good.buyprc == None:
                    good.buyprc = 0

                if good.price == None:
                    good.price = 0
                print('goods', goods,store.storecode,good.gcode,good.rptcode2,good.rptcode3)
                pd =PeriodData.objects.get_or_create(reportperiod=reportperiod,company=company,storecode=store.storecode,gcode=good.gcode,rptcode2=good.rptcode2,rptcode3=good.rptcode3)
                # pd.rptcode2=good.rptcode2
                # pd.rptcode3=good.rptcode3
                # pd.save()
                print(reportperiod.id)

    return HttpResponse('Finished！', content_type="application/json")

def GetReportPeriod(reportyear,reportname,thisdate):
    reportperiod = ReportPeriod.objects.get(reportyear=reportyear,reportname=reportname,fromdate__lte=thisdate,todate__gte=thisdate)
    return reportperiod


def SetPeriodData(request):
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']
    company = 'JMJ'
    reportyear = REPORTYEAR
    rptcode1 = RPTCODE1
    reportname = '阶段性销售报表'
    yearfromdate = YEARFROMDATE
    goods = Goods.objects.filter(valiflag='Y').filter(rptcode1=rptcode1,gcode='21601').order_by('gcode')
    InitPeriodData(company, reportyear, rptcode1)
    stores = Storeinfo.objects.filter(company=company).filter(storecode__in=('1','1-2','2','3','5'))
    for store in stores:
        print(datetime.strptime(fromdate, '%Y%m%d'))
        for good in goods:
            reportperiod = GetReportPeriod(reportyear, '阶段性销售报表', datetime.strptime(fromdate, '%Y%m%d'))
            print(store.storecode,good.gcode)
            perioddataitem = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storeocde,
                                                    gcode=good.gcode,rptcode2=good.rptcode2,rptcode3=good.rptcode3)
            # perioddataitem = PeriodData.objects.get_or_create(reportperiod=reportperiod,company=company,storecode=store,gcode=good.gcode,rptcode2=good.rptcode2,rptcode3=good.rptcode3)
            thisperiodsaleqty = 0
            thisperiodsaleamount = 0

            trans = Expvstoll.objects.filter(valiflag='Y').filter(vsdate__gte=fromdate).filter(vsdate__lte=todate).filter(storecode=store.storecode)
            for trx in trans:
                items = Expense.objects.filter(exptxserno=trx.exptxserno).filter(srvcode=good.gcode)
                for item in items:
                    thisperiodsaleqty = thisperiodsaleqty + item.s_qty
                    thisperiodsaleamount = thisperiodsaleamount + item.s_mount

            perioddataitem.thisperiodsalesqty = thisperiodsaleqty
            perioddataitem.thisperiodsalesamount = thisperiodsaleamount
            if reportperiod.period=='01':
                perioddataitem.totalsalesqty = thisperiodsaleqty
                perioddataitem.totalsalesamount = thisperiodsaleamount
            else:
                lastperiod = reportperiod.period - 1
                print(lastperiod)
                lastreportperiod = ReportPeriod.objects.Get(reportyear=reportyear,reportname=reportname,period=lastperiod)
                lastperioddataitem =  PeriodData.objects.get(reportperiod=lastreportperiod, company='JMJ', storecode=store,
                                                    gcode=good.gcode)
                perioddataitem.totalsalesqty = lastperioddataitem.totalsalesqty + thisperiodsaleqty
                perioddataitem.totalsalesamount = lastperioddataitem.totalsalesamount + thisperiodsaleamount

            print(perioddataitem.storecode, perioddataitem.gcode, good.gname, perioddataitem.thisperiodsalesqty,perioddataitem.totalsalesqty)
            perioddataitem.save()



    return HttpResponse(0, content_type="application/json")

def SetPrecentData(period,reportname):
# def  SetPrecentData(request):
    # period = request.GET['fromdate']
    # period=request.GET['period']
    company = 'JMJ'
    reportyear = '2021'
    reportyear = REPORTYEAR
    # rptcode1 = '2017'
#    reportname = '阶段性销售报表'
#     reportname = '关键阶段销售报表'

    stores = Storeinfo.objects.filter(company=company)
    for store in stores:
        reportperiods = ReportPeriod.objects.filter(reportyear=reportyear).filter(reportname=reportname).filter(period=period)
        for reportperiod in reportperiods:
            print('reporteriod=',reportperiod,'storecode=',store.storecode)
            # reportperiod = ReportPeriod.objects.Get(company=company,reportyear=reportyear,storecode=store,reportname=reportname,period=reportperiod)
            perioddataitem101 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='101')
            perioddataitem102 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='102')
            perioddataitem103 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='103')
            perioddataitem104 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='104')
            perioddataitem105 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='105')
            perioddataitem106 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='106')
            perioddataitem107 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='107')
            perioddataitem108 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='108')
            perioddataitem109 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='109')
            perioddataitem112 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='112')
            perioddataitem113 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='113')
            perioddataitem117 = PeriodData.objects.get(reportperiod=reportperiod, company='JMJ', storecode=store.storecode,rptcode3='117')

            print(store.storecode,reportperiod.id,reportperiod.period,'109')
            print(perioddataitem109.totalsalesqty,perioddataitem109.iqty)
            print(perioddataitem108.totalsalesqty,perioddataitem108.iqty)
            if perioddataitem101.orderqty == None:
                perioddataitem101.orderqty = 0

            if perioddataitem102.orderqty == None:
                perioddataitem102.orderqty = 0

            if perioddataitem103.orderqty == None:
                perioddataitem103.orderqty = 0

            if perioddataitem104.orderqty == None:
                perioddataitem104.orderqty = 0

            if perioddataitem105.orderqty == None:
                perioddataitem105.orderqty = 0

            if perioddataitem106.orderqty == None:
                perioddataitem106.orderqty = 0

            if perioddataitem107.orderqty == None:
                perioddataitem107.orderqty = 0

            if perioddataitem108.orderqty == None:
                perioddataitem108.orderqty = 0

            if perioddataitem109.orderqty == None:
                perioddataitem109.orderqty = 0

            if perioddataitem112.orderqty == None:
                perioddataitem112.orderqty = 0

            if perioddataitem113.orderqty == None:
                perioddataitem113.orderqty = 0

            if perioddataitem117.orderqty == None:
                perioddataitem117.orderqty = 0

            if perioddataitem108.iqty==0 :
                perioddataitem101.rativeiqtypercen =0
                perioddataitem104.rativeiqtypercen =0
                perioddataitem106.rativeiqtypercen =0
                perioddataitem107.rativeiqtypercen =0
                perioddataitem109.rativeiqtypercen =0
            else:
                perioddataitem101.retiveiqtypercent = float((perioddataitem101.iqty + perioddataitem101.orderqty) / (perioddataitem108.iqty+perioddataitem108.orderqty) )
                perioddataitem104.retiveiqtypercent = float((perioddataitem104.iqty + perioddataitem104.orderqty) / (perioddataitem108.iqty+perioddataitem108.orderqty) )
                perioddataitem106.retiveiqtypercent = float((perioddataitem106.iqty + perioddataitem106.orderqty) / (perioddataitem108.iqty+perioddataitem108.orderqty) )
                perioddataitem107.retiveiqtypercent = float((perioddataitem107.iqty + perioddataitem107.orderqty) / (perioddataitem108.iqty+perioddataitem108.orderqty) )
                perioddataitem109.retiveiqtypercent = float((perioddataitem109.iqty + perioddataitem109.orderqty) / (perioddataitem108.iqty+perioddataitem108.orderqty) )
                print('109',perioddataitem109.retiveiqtypercent)

            if perioddataitem108.totalsalesqty==0 :
                perioddataitem101.rativesalesqtypercent =0
                perioddataitem104.rativesalesqtypercent =0
                perioddataitem106.rativesalesqtypercent =0
                perioddataitem107.rativesalesqtypercent =0
                perioddataitem109.rativesalesqtypercent =0
            else:
                perioddataitem101.rativesalesqtypercent = float(perioddataitem101.totalsalesqty / perioddataitem108.totalsalesqty)
                perioddataitem104.rativesalesqtypercent = float(perioddataitem104.totalsalesqty/perioddataitem108.totalsalesqty)
                perioddataitem106.rativesalesqtypercent = float(perioddataitem106.totalsalesqty / perioddataitem108.totalsalesqty)
                perioddataitem107.rativesalesqtypercent = float(perioddataitem107.totalsalesqty/perioddataitem108.totalsalesqty)
                perioddataitem109.rativesalesqtypercent = float(perioddataitem109.totalsalesqty/perioddataitem108.totalsalesqty)

            print(store.storecode,reportperiod.period,  perioddataitem109.retiveiqtypercent)

            if perioddataitem105.orderqty == None:
                perioddataitem105.orderqty =0

            if perioddataitem105.iqty == 0:
                perioddataitem112.retiveiqtypercent = 0
            else:
                perioddataitem112.retiveiqtypercent = float((perioddataitem112.iqty + perioddataitem112.orderqty)/ (perioddataitem105.iqty +perioddataitem105.orderqty))

            if perioddataitem105.totalsalesqty == 0:
                perioddataitem112.rativesalesqtypercent = 0
            else:
                perioddataitem112.rativesalesqtypercent = float(perioddataitem112.totalsalesqty / perioddataitem105.totalsalesqty)

            if perioddataitem102.orderqty==None:
                perioddataitem102.orderqty=0

            if perioddataitem102.iqty == 0:
                perioddataitem105.retiveiqtypercent = 0
                perioddataitem113.retiveiqtypercent = 0
            else:
                perioddataitem105.retiveiqtypercent = float( (perioddataitem105.iqty + perioddataitem105.orderqty) / (perioddataitem102.iqty + perioddataitem102.orderqty))
                perioddataitem113.retiveiqtypercent = float( (perioddataitem113.iqty + perioddataitem113.orderqty)/ (perioddataitem102.iqty + perioddataitem102.orderqty))

            if perioddataitem102.totalsalesqty == 0:
                perioddataitem113.rativesalesqtypercent = 0
            else:
                perioddataitem105.rativesalesqtypercent = float(perioddataitem105.totalsalesqty / perioddataitem102.totalsalesqty)
                perioddataitem113.rativesalesqtypercent = float(perioddataitem113.totalsalesqty / perioddataitem102.totalsalesqty)

            tmptotaliqty = perioddataitem101.iqty  + perioddataitem106.iqty + perioddataitem108.iqty + perioddataitem101.orderqty  + perioddataitem106.orderqty + perioddataitem108.orderqty
            if tmptotaliqty == 0:
                perioddataitem117.retiveiqtypercent = 0
            else:
                perioddataitem117.retiveiqtypercent = float( (perioddataitem117.iqty +perioddataitem117.orderqty)/ tmptotaliqty)

            tmptotalsalesqty =  perioddataitem101.totalsalesqty +  perioddataitem106.totalsalesqty +  perioddataitem108.totalsalesqty
            if tmptotalsalesqty == 0:
                perioddataitem117.rativesalesqtypercent = 0
            else:
                perioddataitem117.rativesalesqtypercent = float(perioddataitem117.totalsalesqty / tmptotalsalesqty)

            perioddataitem101.save()
            perioddataitem102.save()
            perioddataitem103.save()
            perioddataitem104.save()
            perioddataitem105.save()
            perioddataitem106.save()
            perioddataitem107.save()
            perioddataitem108.save()
            perioddataitem109.save()
            perioddataitem112.save()
            perioddataitem113.save()
            perioddataitem117.save()

    return HttpResponse(0, content_type="application/json")

def ProcessInvalidTrans():
    trans = Expvstoll.objects.filter(valiflag='N')
    for tran in trans:
        Goodstranslog.objects.filter(sukid=tran.exptxserno).delete()

    # return HttpResponse('Finished！', content_type="application/json")
    return 0

def SetPeriodIqty(request):
    period= request.GET['period']
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    report = request.GET['report']
    company = 'JMJ'
    reportyear = REPORTYEAR
    rptcode1 =  RPTCODE1
    # reportname = '阶段性销售报表'

    if report == '1' :
        reportname = '阶段性销售报表'

    if report == '2':
        reportname = '关键阶段销售报表'

    yearfromdate = '20201201'
    firstindate ='20201228'
    yearfromdate = YEARFROMDATE
    firstindate = ''

    stores = Storeinfo.objects.filter(company=company,flag='Y').order_by('storecode')
    for store in stores:
        print('store',store.storename)
        # store=item.storecode
        goods = Goods.objects.filter(valiflag='Y').filter(rptcode1=rptcode1,gcode='21601').order_by('gcode')
        for good in goods:
            print('goods',good,good.gname,reportname,period)
            reportperiods = ReportPeriod.objects.filter(reportyear=reportyear).filter(reportname=reportname).filter(period=period)
            totaliqty =0
            thisperiodsaleqty = 0
            thisperiodsaleamount = 0
            totalsalesqty =0
            totalsalesamount =0
            for reportperiod in reportperiods:
                fromdate = datetime.strftime(reportperiod.fromdate,'%Y%m%d')
                todate = datetime.strftime(reportperiod.todate,'%Y%m%d')
                print('period data 2',reportname,reportperiod.id,company,store.storecode,good.gcode,good.rptcode2,good.rptcode3)
                perioddataitem = PeriodData.objects.get_or_create(reportperiod=reportperiod,company=company,storecode=store.storecode,gcode=good.gcode,rptcode2=good.rptcode2,rptcode3=good.rptcode3)[0]

                thisqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(thisqty=Sum('qty1')).filter(
                    storecode=store.storecode).filter(gcode=good.gcode).filter(vdate__gte=fromdate).filter(
                    vdate__lte=todate).filter(saleatr='G')
                print('thisqty',store.storecode, good.gcode, fromdate,todate, thisqty,len(thisqty))
                thisamount = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(
                    thisamount=Sum('amount1')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(
                    vdate__gte=fromdate).filter(vdate__lte=todate).filter(saleatr='G')

                # print('total 1:', store.storecode,good.gcode,yearfromdate, todate)
                totalqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(sumqty=Sum('qty1')).filter(
                    storecode=store.storecode).filter(gcode=good.gcode).filter(vdate__gte=yearfromdate).filter(
                    vdate__lte=todate).filter(saleatr='G')
                print(good.gcode,'totalqty=',totalqty,'yearfromdate=',yearfromdate,'todate=',todate)
                totalamount = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(
                    sumamount=Sum('amount1')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(
                    vdate__gte=yearfromdate).filter(vdate__lte=todate).filter(saleatr='G')

                iqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(sumiqty=Sum('qty1')).filter(
                    storecode=store.storecode).filter(gcode=good.gcode).filter(saleatr='I')

                if len(iqty) != 0:
                    totaliqty = iqty[0]['sumiqty']

                fqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(
                    sumfqty=Sum('qty1')).filter(
                    storecode=store.storecode).filter(gcode=good.gcode).filter(saleatr='F')

                if len(fqty) != 0:
                    totalfqty = fqty[0]['sumfqty']

                tiqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(sumtiqty=Sum('qty1')).filter(
                     storecode=store.storecode).filter(gcode=good.gcode).filter(saleatr='TI')

                # tiqty = 0
                toqty = Goodstranslog.objects.values('storecode', 'gcode', 'saleatr').annotate(sumtoqty=Sum('qty1')).filter(
                    storecode=store.storecode).filter(gcode=good.gcode).filter(saleatr='TO')
                # toqty = 0
                print(store.storecode,good.gcode,tiqty, toqty)

                if len(thisqty) != 0:
                    thisperiodsaleqty = thisqty[0]['thisqty']
                    thisperiodsaleamount = thisamount[0]['thisamount']
                    print('this period', period,thisqty[0]['thisqty'], thisamount[0]['thisamount'])
                else:
                    thisperiodsaleqty = 0
                    thisperiodsaleamount = 0
                    # print(0)

                if len(totalqty) != 0:
                    # print(totalqty)
                    totalsalesqty = totalqty[0]['sumqty']
                    totalsalesamount = totalamount[0]['sumamount']
                    print('total:', period,totalqty[0]['sumqty'], totalamount[0]['sumamount'])
                else:
                    totalsalesqty = 0
                    totalsalesamount = 0
                    # print(0)

                if len(iqty) != 0:
                    totaliqty = iqty[0]['sumiqty']
                else:
                    totaliqty = 0

                if len(fqty) != 0:
                    totalfqty = fqty[0]['sumfqty']
                else:
                    totalfqty =0

                if len(tiqty) != 0:
                    totaltiqty = tiqty[0]['sumtiqty']
                else:
                    totaltiqty =0

                if len(toqty) != 0:
                    totaltoqty = toqty[0]['sumtoqty']
                else:
                    totaltoqty =0

                if store.storecode =='1-2':
                    totaliqty =0
                    totaltiqty=0
                    totaltoqty=0
                    totalfqty =0
                    print(store.storecode,'iqty=',totaliqty)

                # 转入转出要检查是否平衡
                # if store.storecode =='1':
                #     totaltiqty = 0
                #     totaltoqty = 0
                #     print(store.storecode,'tiqty,toqty=0,',totaliqty)


                # if len(tiqty) != 0:
                #     totaliqty = tiqty[0]['sumiqty']
                #
                # if len(toqty) != 0:
                #     totaliqty = toqty[0]['sumiqty']
                # print(perioddataitem.id,good.gcode,perioddataitem.period,'totaliqty',totaliqty,'this period sales qty:', thisperiodsaleqty,'totalsaleqty:',totalsalesqty)

                perioddataitem.iqty = totaliqty

                perioddataitem.tiqty = totaltiqty
                perioddataitem.toqty = totaltoqty + totalfqty
                # print(perioddataitem.id,perioddataitem.iqty)
                perioddataitem.thisperiodsalesqty = thisperiodsaleqty
                perioddataitem.thisperiodsalesamount = thisperiodsaleamount
                perioddataitem.totalsalesqty = totalsalesqty
                perioddataitem.totalsalesamount = totalsalesamount
                perioddataitem.save()

                if perioddataitem.iqty == None:
                    perioddataitem.iqty = 0

                if perioddataitem.tiqty == None:
                    perioddataitem.tiqty = 0

                if perioddataitem.toqty == None:
                    perioddataitem.toqty = 0

                if perioddataitem.totalsalesqty == None:
                    perioddataitem.totalsalesqty = 0

                perioddataitem.orderqty=0
                perioddataitem.stockqty = perioddataitem.iqty + perioddataitem.tiqty - perioddataitem.toqty - perioddataitem.totalsalesqty

                tmpiqty = (perioddataitem.iqty + perioddataitem.tiqty - perioddataitem.toqty +perioddataitem.orderqty)
                if tmpiqty == 0 :
                    perioddataitem.salespercent = 0.0
                elif tmpiqty == None:
                    perioddataitem.salespercent = 0.0
                else:
                    if perioddataitem.totalsalesqty == 0 or perioddataitem.totalsalesqty ==None:
                        perioddataitem.salespercent =0
                    else:
                        perioddataitem.salespercent = float(perioddataitem.totalsalesqty / (perioddataitem.iqty + perioddataitem.tiqty - perioddataitem.toqty +perioddataitem.orderqty))
                    # print(perioddataitem.salespercent)

                print(perioddataitem.storecode, perioddataitem.gcode, good.gname, perioddataitem.thisperiodsalesqty,perioddataitem.totalsalesqty)
                perioddataitem.save()


        # 计算该期订货商品数量
    print('Begin Set Period Order Qty:',period,reportname)
    SetPeriodOrderQty(period,reportname)
    #
    print('begin set PrecentData',period,reportname)
    SetPrecentData(period,reportname)

    return HttpResponse('Finished！', content_type="application/json")

def SetPeriodOrderQty(pd,reportname):
    reportyear=REPORTYEAR
    company='JMJ'
    # pd ='04'
    # reportname='阶段性销售报表'
    stores = Storeinfo.objects.filter(company=company)
    for store in stores:
        whcodes = Wharehouse.objects.filter(storecode=store.storecode)
        for whcode in whcodes:
            periods = ReportPeriod.objects.filter(reportyear=reportyear).filter(reportname=reportname).filter(period=pd)
            for period in periods:
                fromdate = datetime.strftime(period.fromdate,'%Y%m%d')
                todate = datetime.strftime(period.todate,'%Y%m%d')

                # saleheads = Salehead.objects.filter(company=company).filter(instorecode=store.storecode).filter(inwhcode=whcode.wharehousecode).filter(status='10').filter(vdate__gte=fromdate).filter(vdate__lte=todate)
                saleheads = Salehead.objects.filter(company=company).filter(instorecode=store.storecode).filter(inwhcode=whcode.wharehousecode).filter(status='10')
                for salehead in saleheads:
                    orderqty = salehead.get_qty()
                    # print('order qty:',orderqty[item]['gcode'], 'order qty:', orderqty[item]['qty'], period.id)
                    for item in range(orderqty.count()):
                        print( 'Set OrderQty',whcode.wharehousecode,orderqty[item]['gcode'],'order qty:', orderqty[item]['qty'],period.id)
                        if Goods.objects.get(company=company,gcode=orderqty[item]['gcode']).rptcode1 == reportyear:
                            perioddata = PeriodData.objects.get(company=company, storecode=store.storecode,
                                                                reportperiod_id=period.id,
                                                                gcode=orderqty[item]['gcode'])
                            # if perioddata.orderqty == None:
                            #     perioddata.orderqty =0

                            if orderqty[item]['qty'] == None:
                                orderqty[item]['qty'] =0

                            perioddata.orderqty = orderqty[item]['qty']
                            print('Set Order Qty:',orderqty[item]['gcode'],'orderqty=',perioddata.orderqty)

                            # perioddata.stockqty = perioddataitem.iqty + perioddataitem.tiqty - perioddataitem.toqty - perioddataitem.totalsalesqty
                            if perioddata.iqty == 0:
                                perioddata.salespercent = 0.0
                            elif perioddata.iqty == None:
                                perioddata.salespercent = 0.0
                            else:
                                perioddata.salespercent = float(perioddata.totalsalesqty / (
                                    perioddata.iqty + perioddata.tiqty - perioddata.toqty + perioddata.orderqty))
                                print('Set Order salespercent:',perioddata.salespercent)

                            perioddata.save()

    print('Set Order qty finished')
    return HttpResponse(0, content_type="application/json")

def SetYearPeriodData(request):
    company = request.GET['company']
    reportyear= request.GET['reportyear']
    rptcode1= request.GET['rptcode1']

    reportyear = REPORTYEAR
    rptcode1=RPTCODE1
    # reportname ='阶段性销售报表'
    reportname ='关键阶段销售报表'
    yearfromdate =  YEARFROMDATE

    # datetime.datetime.strptime(detester,'%Y-%m-%d')
    # InitPeriodData('JMJ','2019','19')
    InitPeriodData(company,reportyear,rptcode1)

    goods = Goods.objects.filter(rptcode1=rptcode1)
    stores = Storeinfo.objects.filter(company=company)
    for good in goods:
        for store in stores:
            # if store.storecode == '6':
            #     store.storecode = '1'

            # reportperiod = GetReportPeriod(reportyear,'阶段性销售报表',datetime.strptime(fromdate,'%Y%m%d') )
            reportperiods = ReportPeriod.objects.filter(reportyear=reportyear).filter(reportname=reportname).filter(period__in=('03','04'))
            totaliqty =0
            thisperiodsaleqty = 0
            thisperiodsaleamount = 0
            totalsalesqty =0
            totalsalesamount =0
            for reportperiod in reportperiods:
                fromdate = datetime.strftime(reportperiod.fromdate,'%Y%m%d')
                todate = datetime.strftime(reportperiod.todate,'%Y%m%d')
                print(reportperiod.reportyear, reportperiod.id, store.storename,good.gcode,fromdate,todate)
                perioddataitem = PeriodData.objects.get(reportperiod=reportperiod,company=company,storecode=store.storecode,gcode=good.gcode)
                print( store.storecode,good.gcode,fromdate, todate)
                # items = OldData.objects.filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__gte=fromdate).filter(vsdate__lte=todate)
                thisqty = OldData.objects.values('storecode','gcode','saleatr').annotate(thisqty=Sum('salesqty')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__gte=fromdate).filter(vsdate__lte=todate).filter(saleatr='G')
                thisamount = OldData.objects.values('storecode','gcode','saleatr').annotate(thisamount=Sum('salesamount')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__gte=fromdate).filter(vsdate__lte=todate).filter(saleatr='G')

                print( store.storecode,good.gcode,yearfromdate, todate)
                totalqty = OldData.objects.values('storecode','gcode','saleatr').annotate(sumqty=Sum('salesqty')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__gte=yearfromdate).filter(vsdate__lte=todate).filter(saleatr='G')
                totalamount = OldData.objects.values('storecode','gcode','saleatr').annotate(sumamount=Sum('salesamount')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__gte=yearfromdate).filter(vsdate__lte=todate).filter(saleatr='G')

                iqty = OldData.objects.values('storecode','gcode','saleatr').annotate(sumiqty=Sum('salesqty')).filter(storecode=store.storecode).filter(gcode=good.gcode).filter(vsdate__lte=todate).filter(saleatr='I')


                if len(thisqty) != 0 :
                    thisperiodsaleqty = thisqty[0]['thisqty']
                    thisperiodsaleamount = thisamount[0]['thisamount']
                    print('this period',thisqty[0]['thisqty'], thisamount[0]['thisamount'])
                else:
                    thisperiodsaleqty = 0
                    thisperiodsaleamount = 0
                    # print(0)

                if len(totalqty) != 0:
                    print(totalqty)
                    totalsalesqty = totalqty[0]['sumqty']
                    totalsalesamount = totalamount[0]['sumamount']
                    print('total:',totalqty[0]['sumqty'],totalamount[0]['sumamount'] )
                else:
                    totalsalesqty = 0
                    totalsalesamount = 0
                    # print(0)

                if len(iqty) !=0:
                    totaliqty = iqty[0]['sumiqty']
                else:
                    totaliqty =0

                # print(items)filter(vsdate__gte=fromdate).filter(vsdate__lte=todate).filter(storecode=store.storecode)
                # for item in items:
                #     print(item.salesqty)
                #     thisperiodsaleqty = thisperiodsaleqty + item.salesqty
                #     thisperiodsaleamount = thisperiodsaleamount + item.salesamount
                #
                perioddataitem.iqty = totaliqty
                perioddataitem.thisperiodsalesqty = thisperiodsaleqty
                perioddataitem.thisperiodsalesamount =thisperiodsaleamount
                perioddataitem.totalsalesqty = totalsalesqty
                perioddataitem.totalsalesamount = totalsalesamount
                perioddataitem.save()

                if perioddataitem.iqty ==None:
                    perioddataitem.iqty =0

                if perioddataitem.tiqty == None:
                    perioddataitem.tiqty =0

                if perioddataitem.toqty == None:
                    perioddataitem.toqty =0

                if perioddataitem.totalsalesqty==None:
                    perioddataitem.totalsalesqty =0

                perioddataitem.stockqty = perioddataitem.iqty + perioddataitem.tiqty -perioddataitem.toqty - perioddataitem.totalsalesqty
                if perioddataitem.iqty == 0 or perioddataitem.iqty ==None:
                    perioddataitem.salespercent =0.0
                else:
                    perioddataitem.salespercent = perioddataitem.totalsalesqty / (perioddataitem.iqty)

                print(perioddataitem.storecode, perioddataitem.gcode, fromdate,todate,yearfromdate,perioddataitem.thisperiodsalesqty,perioddataitem.totalsalesqty)
                perioddataitem.save()


    return HttpResponse(0, content_type="application/json")

def SumStoreData():
    reportyear = '2020'
    reportyear = REPORTYEAR
    company = 'JMJ'
    reportname = '阶段性销售报表'
    reportperiods = ReportPeriod.objects.filter(reportyear=reportyear).filter(reportname=reportname)
    # for reportperiod in reportperiods:
