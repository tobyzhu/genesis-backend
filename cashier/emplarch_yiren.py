from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from decimal import *
import requests
import datetime
import numpy as np
import pandas as pd
from django.db.models import Count,Sum,Q,F

from .models import Expvstoll,Expense,Toll,EmplArchivementDetail
from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode
from adviser.models import Cardinfo
from goods.views import FillTransdtl
from adviser.views import *

import common.constants

# expense表中，exp_xbasenum记录为相应交易流水金额   xpoint 记录为固定提成  xamount 资金流水   xperc流水分配比例
#  xperc
def cal_emplarchivement_yiren(company,storecode, fromdate,todate):
    if fromdate < '20191201':
        fromdate='20191201'

    transuuids = Expvstoll.objects.filter(company=company,valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate,vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    ttypes = ['S','G']
    for transuuid in transuuids:
        cardinfo_stype='N'
        print('transuuid.ccode',transuuid.ccode)
        if len(transuuid.ccode)>0 :
            cardinfo_stype = Cardinfo.objects.filter(company=company,flag='Y',ccode=transuuid.ccode)[0].stype

        transitems = Expense.objects.filter(company=company,flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)

        # 计算该笔交易中，现金付款比例，卡付类付款比例
        cashamount = 0
        totalamount = 0
        cardamount=0
        sendamount=0
        otheramount=0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            if p.iscash==None:
                p.iscash='9'

            if p.iscash=='3':
                otheramount =  pcode.totmount + Decimal(otheramount)

            if p.iscash=='2':
                sendamount =  pcode.totmount + Decimal(sendamount)
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
            if p.iscash=='0':
                cardamount = pcode.totmount + Decimal(cardamount)
                if cardinfo_stype=='P':
                    sendamount=sendamount + pcode.totmount
                    cardamount=0

        if totalamount ==0 :
            cashratio=1
            cardratio=1
            sendratio=1
            otherratio=1
        else:
            cashratio = round(Decimal(cashamount / totalamount),4)
            cardratio = round(Decimal(cardamount / totalamount),4)
            sendratio = round(Decimal(sendamount / totalamount),4)
            otherratio = round(Decimal(otheramount / totalamount),4)
        print('cardratio',cardratio,'sendration=',sendratio,'cashratio=',cashratio)

        for transitem in transitems:
            transitem.cashratio = cashratio
            transitem.cardratio = cardratio
            transitem.sendratio = sendratio
            transitem.otherratio = otherratio
            # 处理一些为NULL的情况
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
                pmratio=1
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''
            if transitem.s_qty==None:
                transitem.s_qty=0

            if transitem.ttype =='S':
                try:
                    item = Serviece.objects.filter(company=company, flag='Y').filter(svrcdoe=transitem.srvcode).last()
                    if item.pmpoint == None:
                        item.pmpoint = 0
                    if item.secpoint == None:
                        item.secpoint = 0
                    if item.thrpoint == None:
                        item.thrpoint = 0
                    if transitem.s_qty == None:
                        transitem.s_qty = 0

                    #     伊人计算项次   在设定中设定在qty， 在expense中记录在stdmins
                    transitem.stdmins = item.qty * transitem.s_qty

                    if item.pmperc==None:
                        item.pmperc=0
                    if item.secperc ==None:
                        item.secperc=0
                    if item.thrperc==None:
                        item.thrperc=0

                    if transitem.stype == 'P':
                        #     计算完全赠送类  赠送类固定提成 按点数计算
                        #       资金流水为0 ,操作流水也为0
                        transitem.pmperc=0
                        transitem.secperc=0.5
                        transitem.thprec=0
                        transitem.pmguideperc=0
                        transitem.secguideperc=0.5
                        transitem.thrguideperc=0
                        transitem.pmamount=0
                        transitem.secamount=0
                        transitem.thramount=0
                        transitem.exp_basenum = 0
                        transitem.exp_secbasenum = 0
                        transitem.exp_thrbasenum = 0
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = item.secpoint * transitem.s_qty
                        transitem.thrpoint = item.thrpoint * transitem.s_qty
                        pmratio=1
                        secratio=0
                        thrratio=0

                        if len(transitem.asscode1.strip()) > 0:
                            transitem.pmguideperc = 0
                            transitem.secguideperc = 1.0
                            transitem.thrguideperc = 0
                            transitem.pmperc=0
                            transitem.secperc=1.0
                            transitem.thprec=0
                            pmratio=0.5
                            secratio=0.5
                            thrratio=0

                            if transitem.create_time.strftime('%Y%m%d') <= '20191104':
                                transitem.secpoint = item.pmpoint * transitem.s_qty
                                transitem.thrpoint = 0

                            if transitem.create_time.strftime('%Y%m%d') > '20191104':
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = item.thrpoint * transitem.s_qty

                        if len(transitem.asscode2.strip()) > 0:
                            transitem.pmguideperc = 0
                            transitem.secguideperc = 0.5
                            transitem.thrguideperc = 0.5
                            transitem.pmperc=0
                            transitem.secperc=0.5
                            transitem.thprec=0.5
                            pmratio=0.33333
                            secratio=0.33333
                            thrratio=0.33333

                            # print(datetime.datetime.strftime(transitem.create_time,'%Y%m%d'))
                            if transitem.create_time.strftime('%Y%m%d') > '20191104':
                                transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                            if transitem.create_time.strftime( '%Y%m%d') <= '20191104':
                                transitem.secpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)


                        #     资金流水
                        transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                        transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                        transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                        #   服务操作流水   开单人员不计操作流水
                        transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal( cardratio + cashratio) + \
                                                transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal( sendratio) * Decimal(0.5)

                        transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(cardratio + cashratio) + \
                                                   transitem.s_mount * Decimal(transitem.secguideperc) * Decimal( sendratio) * Decimal(0.5)

                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal( cardratio + cashratio) + \
                                                   transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal( sendratio) * Decimal(0.5)

                        transitem.save()

                    # 设置实操拆分比例
                    if transitem.stype == 'N':
                        print('N',transitem.stype,transitem.exptxserno,transitem.srvcode,transitem.s_qty,item.secpoint)
                        # 正常消费服务
                        transitem.pmperc = 0
                        transitem.secperc = 0
                        transitem.thprec = 0
                        transitem.pmguideperc = 1
                        transitem.secguideperc = 1
                        transitem.thrguideperc = 0
                        transitem.pmamount = 0
                        transitem.secamount = 0
                        transitem.thramount = 0
                        transitem.exp_basenum = 0
                        transitem.exp_secbasenum = 0
                        transitem.exp_thrbasenum = 0
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = item.secpoint * transitem.s_qty
                        transitem.thrpoint = item.thrpoint * transitem.s_qty

                        pmratio=1
                        secratio=0
                        thrratio=0
                        if len(transitem.asscode1.strip()) > 0:
                            transitem.pmguideperc = 0
                            transitem.secguideperc = 1.0
                            transitem.thrguideperc = 0
                            transitem.pmperc=0.0
                            transitem.secperc=1.0
                            transitem.thprec=0.0
                            pmratio=0.5
                            secratio=0.5
                            thrratio=0

                            if transitem.create_time.strftime('%Y%m%d') <= '20191104':
                                # transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = item.pmpoint * transitem.s_qty
                                transitem.thrpoint = 0

                            if  transitem.create_time.strftime('%Y%m%d')>'20191104':
                                # transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = 0
                            secperc= item.secperc + item.thrperc
                            thrperc=0

                        if len(transitem.asscode2.strip()) > 0:
                            transitem.pmguideperc = 0
                            transitem.secguideperc = 0.5
                            transitem.thrguideperc = 0.5
                            transitem.pmperc=0
                            transitem.secperc=0.5
                            transitem.thprec=0.5
                            pmratio=0.33333
                            secratio=0.33333
                            thrratio=0.33333

                            if  transitem.create_time.strftime('%Y%m%d')<='20191104':
                                # transitem.pmpoint = item.pmpoint * transitem.s_qty
                                if item.thrpoint ==0 :
                                    transitem.secpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                    transitem.thrpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                else:
                                    transitem.secpoint = item.pmpoint * transitem.s_qty
                                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                            if  transitem.create_time.strftime('%Y%m%d')>'20191104':
                                # transitem.pmpoint = item.pmpoint * transitem.s_qty
                                if item.thrpoint ==0 :
                                    transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                    transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                else:
                                    transitem.secpoint = item.secpoint * transitem.s_qty
                                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                            secperc = (item.secperc + item.thrperc) /2
                            thrperc = (item.secperc + item.thrperc) /2

                        #     资金流水
                        transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                        transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                        transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                        if secperc>0:
                            transitem.secpoint = transitem.s_mount * Decimal(secperc) * Decimal( cashratio + cardratio)

                        if thrperc >0:
                            transitem.thrpoint = transitem.s_mount * Decimal(thrperc) * Decimal( cashratio + cardratio)

                        #   服务操作流水   开单人员不计操作流水
                        transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal(cardratio + cashratio) +\
                                                    transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal(sendratio) *Decimal(0.5)

                        transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(cardratio + cashratio) + \
                                                   transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(sendratio) * Decimal(0.5)

                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal(cardratio + cashratio)+ \
                                                   transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal(sendratio) * Decimal(0.5)

                        transitem.save()


                except:
                    print('skipped',transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)

            print(transuuid.ttype, transitem.stype, transuuid.ccode, transuuid.cardtype)
            # 划储值卡购买产品、保健品算积点
            if transitem.ttype =='G':
                print(transitem.exptxserno,transitem.srvcode,len(transitem.srvcode))
                try:
                    item = Goods.objects.filter(company=company).filter(gcode=transitem.srvcode).last()
                    print(item.gcode,item.gname)
                    if item.pmpoint == None:
                        pmpoint = 0
                    if item.secpoint == None:
                        secpoint = 0
                    if item.thrpoint == None:
                        thrpoint = 0
                    if transitem.s_qty == None:
                        transitem.s_qty = 0

                    # 赠送产品  员工什么都不算
                    if transitem.stype=='P':
                        transitem.pmperc=0
                        transitem.secperc=0
                        transitem.thprec=0
                        transitem.pmguideperc=0
                        transitem.secguideperc=0
                        transitem.thrguideperc=0
                        transitem.exp_basenum=0
                        transitem.exp_secbasenum=0
                        transitem.exp_thrbasenum=0
                        transitem.pmamount=0
                        transitem.secamount=0
                        transitem.thramount=0
                        transitem.pmpoint= 0
                        transitem.secpoint= 0
                        transitem.thrpoint = 0
                        pmratio = 0
                        secratio =0
                        thrratio =0

                        if len(transitem.pmcode.strip()) > 0:
                            pmratio=1
                            secratio=0
                            thrratio=0

                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.333
                            secratio = 0.333
                            thrratio = 0.333
                        transitem.pmperc = pmratio
                        transitem.secperc = secratio
                        transitem.thprec = thrratio

                        transitem.save()

                    if transitem.stype=='N':
                        pmratio = 0
                        secratio =0
                        thrratio =0

                        if len(transitem.pmcode.strip()) > 0:
                            pmratio=1
                            secratio=0
                            thrratio=0

                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.333
                            secratio = 0.333
                            thrratio = 0.333

                        transitem.pmperc = pmratio
                        transitem.secperc = secratio
                        transitem.thprec = thrratio

                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)*Decimal(cardratio + cashratio)
                        transitem.exp_secbasenum= transitem.s_mount * Decimal(secratio)*Decimal(cardratio + cashratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)*Decimal(cardratio + cashratio)

                        transitem.pmamount =transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                        transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                        transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                        transitem.pmpoint = transitem.s_qty * Decimal(pmpoint)
                        transitem.secpoint = transitem.s_qty * Decimal(secpoint)
                        transitem.thrpoint = transitem.s_qty * Decimal(thrpoint)

                        transitem.save()
                except:
                    print('skipped',transitem.exptxserno,transitem.srvcode,len(transitem.srvcode))

            if transitem.ttype in ('C','I'):
                print(transitem.ttype,transitem.exptxserno,transitem.srvcode,transitem.stype)
                transitem.pmperc = 0
                transitem.secperc = 0
                transitem.thprec = 0
                transitem.pmguideperc = 0
                transitem.secguideperc = 0
                transitem.thrguideperc = 0
                transitem.exp_basenum = 0
                transitem.exp_secbasenum = 0
                transitem.exp_thrbasenum = 0
                transitem.pmamount = 0
                transitem.secamount = 0
                transitem.thramount = 0
                transitem.pmpoint = 0
                transitem.secpoint = 0
                transitem.thrpoint = 0

                try:
                    cardinfo = Cardinfo.objects.filter(company=company).filter(ccode=transitem.srvcode).last()
                    print(cardinfo.ccode)
                    if cardinfo.cardtype==None:
                        cardtype=''
                    else:
                        cardtype=cardinfo.cardtype
                except:
                    print('skipped',transitem.exptxserno,transitem.ttype,transitem.srvcode)
                    cardtype=''

                try:
                    item = Cardtype.objects.filter(company=company, flag='Y', cardtype=cardtype).last()
                    if item.pmpoint == None:
                        pmpoint = 0
                    if item.secpoint == None:
                        secpoint = 0
                    if item.thrpoint == None:
                        thrpoint = 0
                    if transitem.s_qty == None:
                        s_qty = 0
                except:
                    print('skipped',cardinfo,transitem.srvcode,transuuid.exptxserno)
                    pmpoint=0
                    secpoint=0
                    thrpoint=0


                # 赠送的卡项，什么都不算
                if transitem.stype == 'P':
                    transitem.pmperc = 0
                    transitem.secperc = 0
                    transitem.thprec = 0
                    transitem.pmguideperc = 0
                    transitem.secguideperc = 0
                    transitem.thrguideperc = 0
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0
                    transitem.pmpoint = 0
                    transitem.secpoint = 0
                    transitem.thrpoint = 0

                    pmratio = 0
                    secratio = 0
                    thrratio = 0

                    if len(transitem.pmcode.strip()) > 0:
                        pmratio = 1
                        secratio = 0
                        thrratio = 0

                    if len(transitem.asscode1.strip()) > 0:
                        pmratio = 0.5
                        secratio = 0.5
                        thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        pmratio = 0.33333
                        secratio = 0.33333
                        thrratio = 0.33333

                    transitem.pmperc = pmratio
                    transitem.secperc = secratio
                    transitem.thprec = thrratio
                    transitem.save()

                if transitem.stype=='N':
                    pmratio = 0
                    secratio = 0
                    thrratio = 0

                    if len(transitem.pmcode.strip()) > 0:
                        pmratio = 1
                        secratio = 0
                        thrratio = 0

                    if len(transitem.asscode1.strip()) > 0:
                        pmratio = 0.5
                        secratio = 0.5
                        thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        pmratio = 0.33333
                        secratio = 0.33333
                        thrratio = 0.33333

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                    # 计算疗程卡销售流水
                    if (item.suptype=='20') and (item.comptype=='times'):
                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio) * Decimal(cashratio + cardratio)
                        transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio) * Decimal(cashratio + cardratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio) * Decimal(cashratio + cardratio)

                        transitem.pmperc = pmratio
                        transitem.secperc = secratio
                        transitem.thprec = thrratio

                    if (item.suptype=='25') or (item.comptype=='period'):
                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio) * Decimal(cashratio + cardratio)
                        transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio) * Decimal(cashratio + cardratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio) * Decimal(cashratio + cardratio)

                        transitem.pmperc = pmratio
                        transitem.secperc = secratio
                        transitem.thprec = thrratio

                    transitem.save()

    return  0
    # return HttpResponse("完成！", content_type="application/json")

def process_pertrans_yiren(company,storecode,txserno,transuuid):
    # company='yiren'
    if len(transuuid) >0:
        transuuid = Expvstoll.objects.get(company=company,storecode=storecode,uuid=transuuid)

    if len(txserno) >0 :
        transuuid = Expvstoll.objects.get(company=company,storecode=storecode,exptxserno=txserno)

    t =  datetime.now().strftime('%Y-%m-$d %H:%M:%S')
    print('before set_oldcustflag',transuuid.exptxserno, datetime.now().strftime('%Y-%m-$d %H:%M:%S'))
    transuuid.set_oldcustflag()
    print('before set_cardhistory',transuuid.exptxserno, datetime.now().strftime('%Y-%m-$d %H:%M:%S'))
    # transuuid.set_cardhistory()
    print('before set_transgoodstranslog',transuuid.exptxserno,datetime.now().strftime('%Y-%m-$d %H:%M:%S'))
    transuuid.set_transgoodstranslog()
    print('after set_transgoodstranslog',transuuid.exptxserno,datetime.now().strftime('%Y-%m-$d %H:%M:%S'))

    ttypes = ['S','G']
    # for transuuid in transuuids:
    cardinfo_stype='N'
    if len(transuuid.ccode)>0 :
        cardinfo_stype = Cardinfo.objects.filter(company=company,flag='Y',status='O',ccode=transuuid.ccode)[0].stype

    transitems = Expense.objects.filter(company=company,flag='Y').filter(transuuid=transuuid)
    pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)

    # 计算该笔交易中，现金付款比例，卡付类付款比例
    cashamount = 0
    totalamount = 0
    cardamount=0
    sendamount=0
    otheramount=0
    for pcode in pcodes:
        print('pcode=',pcode.pcode)
        if pcode.totmount==None:
            pcode.totmount=0

        totalamount = totalamount + Decimal(pcode.totmount)
        p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
        print(p,p.iscash)
        if p.iscash==None:
            p.iscash='9'

        if p.iscash=='3':
            otheramount =  pcode.totmount + Decimal(otheramount)

        if p.iscash=='2':
            sendamount =  pcode.totmount + Decimal(sendamount)
        if p.iscash == '1':
            cashamount = pcode.totmount + Decimal(cashamount)
        if p.iscash=='0':
            cardamount = pcode.totmount + Decimal(cardamount)
            if cardinfo_stype=='P':
                sendamount=sendamount + pcode.totmount
                cardamount=0

    if totalamount ==0 :
        cashratio=1
        cardratio=1
        sendratio=1
        otherratio=1
    else:
        cashratio = Decimal(cashamount / totalamount)
        cardratio = Decimal(cardamount / totalamount)
        sendratio = Decimal(sendamount / totalamount)
        otherratio = Decimal(otheramount / totalamount)
    print('cardratio',cardratio,'sendration=',sendratio,'cashratio=',cashratio)

    for transitem in transitems:
        print(transitem.create_time, transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)

        transitem.cashratio = cashratio
        transitem.cardratio = cardratio
        transitem.sendratio = sendratio
        transitem.otherratio = otherratio
        # 处理一些为NULL的情况
        if transitem.s_mount==None:
            transitem.s_mount=0
        if transitem.pmcode == None:
            transitem.pmcode = ''
            pmratio=1
        if transitem.asscode1 == None:
            transitem.asscode1 = ''
        if transitem.asscode2 == None:
            transitem.asscode2 = ''
        if transitem.s_qty==None:
            transitem.s_qty=0

        if transitem.ttype =='S':
            try:
                item = Serviece.objects.filter(company=company, flag='Y').filter(svrcdoe=transitem.srvcode).last()

                if item.pmpoint == None:
                    item.pmpoint = 0
                if item.secpoint == None:
                    item.secpoint = 0
                if item.thrpoint == None:
                    item.thrpoint = 0
                if transitem.s_qty == None:
                    transitem.s_qty = 0

                #     伊人计算项次   在设定中设定在qty， 在expense中记录在stdmins
                transitem.stdmins = item.qty * transitem.s_qty

                print(transitem.stype, item.secpoint, transitem.s_qty)

                if item.pmperc==None:
                    item.pmperc=0
                if item.secperc ==None:
                    item.secperc=0
                if item.thrperc==None:
                    item.thrperc=0

                print('transitem.stype',transitem.stype)
                if transitem.stype == 'P':

                    #     计算完全赠送类  赠送类固定提成 按点数计算
                    #       资金流水为0 ,操作流水也为0
                    transitem.pmperc=0
                    transitem.secperc=0.5
                    transitem.thprec=0
                    transitem.pmguideperc=0
                    transitem.secguideperc=0.5
                    transitem.thrguideperc=0
                    transitem.pmamount=0
                    transitem.secamount=0
                    transitem.thramount=0
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint = item.pmpoint * transitem.s_qty
                    transitem.secpoint = item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty
                    pmratio=1
                    secratio=0
                    thrratio=0

                    if len(transitem.asscode1.strip()) > 0:
                        print('len(transitem.asscode1.strip())',len(transitem.asscode1.strip()))
                        transitem.pmguideperc = 0
                        transitem.secguideperc = 1.0
                        transitem.thrguideperc = 0
                        transitem.pmperc=0
                        transitem.secperc=1.0
                        transitem.thprec=0
                        pmratio=0.5
                        secratio=0.5
                        thrratio=0

                        # print(datetime.datetime.strftime(transitem.create_time,'%Y%m%d'))
                        if transitem.create_time.strftime( '%Y%m%d') <= '20191104':
                            print('ass1 before 20191104',datetime.datetime.strftime(transitem.create_time,'%Y%m%d'))
                        # if datetime.datetime.strftime(transitem.create_time,'%Y%m%d')<='20191104':
                            # transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.pmpoint * transitem.s_qty
                            transitem.thrpoint = 0

                        if transitem.create_time.strftime('%Y%m%d') > '20191104':
                        # if datetime.datetime.strftime(transitem.create_time,'%Y%m%d')>'20191104':
                            print('ass1 after 20191104',datetime.datetime.strftime(transitem.create_time,'%Y%m%d'))
                            print('qty', transitem.s_qty)
                            # transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.secpoint * transitem.s_qty
                            print('2')
                            transitem.thrpoint = item.thrpoint * transitem.s_qty
                            print('3')

                    print('len(transitem.asscode2.strip())',len(transitem.asscode2.strip()))
                    if len(transitem.asscode2.strip()) > 0:
                        print('ass2','len(transitem.asscode2.strip())',len(transitem.asscode2.strip()))
                        transitem.pmguideperc = 0
                        transitem.secguideperc = 0.5
                        transitem.thrguideperc = 0.5
                        transitem.pmperc=0
                        transitem.secperc=0.5
                        transitem.thprec=0.5
                        pmratio=0.33333
                        secratio=0.33333
                        thrratio=0.33333


                        if transitem.create_time.strftime('%Y%m%d') > '20191104':
                            transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                            transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                        if transitem.create_time.strftime( '%Y%m%d') <= '20191104':
                            transitem.secpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                            transitem.thrpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                    # transitem.pmperc = pmratio
                    # transitem.secperc = secratio
                    # transitem.thprec = thrratio
                    #     资金流水
                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                    # transitem.exp_basenum = transitem.s_mount * transitem.pmperc * Decimal(cardratio + cashratio)*0
                    # transitem.exp_secbasenum = transitem.s_mount * transitem.secperc * Decimal(1 - cardratio + cashratio) * Decimal(0.5)
                    # transitem.exp_thrbasenum = transitem.s_mount * transitem.thprec * Decimal(1 - cardratio + cashratio) * Decimal(0.5)

                    #   服务操作流水   开单人员不计操作流水
                    # transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmperc) * Decimal( cardratio + cashratio) + \
                    #                         transitem.s_mount * Decimal(transitem.pmperc) * Decimal( sendratio) * Decimal(0.5)
                    #
                    # transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secperc) * Decimal(cardratio + cashratio) + \
                    #                            transitem.s_mount * Decimal(transitem.secperc) * Decimal( sendratio) * Decimal(0.5)
                    #
                    # transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thprec) * Decimal( cardratio + cashratio) + \
                    #                            transitem.s_mount * Decimal(transitem.thprec) * Decimal( sendratio) * Decimal(0.5)

                    transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal( cardratio + cashratio) + \
                                            transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal( sendratio) * Decimal(0.5)

                    transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(cardratio + cashratio) + \
                                               transitem.s_mount * Decimal(transitem.secguideperc) * Decimal( sendratio) * Decimal(0.5)

                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal( cardratio + cashratio) + \
                                               transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal( sendratio) * Decimal(0.5)

                    transitem.save()

                # 设置实操拆分比例
                if transitem.stype == 'N':
                    print('N',transitem.stype,transitem.exptxserno,transitem.srvcode,transitem.s_qty,item.secpoint)
                    # 正常消费服务
                    transitem.pmperc = 0
                    transitem.secperc = 0
                    transitem.thprec = 0
                    transitem.pmguideperc = 1
                    transitem.secguideperc = 1
                    transitem.thrguideperc = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint = item.pmpoint * transitem.s_qty
                    transitem.secpoint = item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                    pmratio=1
                    secratio=0
                    thrratio=0
                    print('len(transitem.asscode1.strip())',len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        transitem.pmguideperc = 0
                        transitem.secguideperc = 1.0
                        transitem.thrguideperc = 0
                        transitem.pmperc=0.0
                        transitem.secperc=1.0
                        transitem.thprec=0.0
                        pmratio=0.5
                        secratio=0.5
                        thrratio=0

                        if transitem.create_time.strftime('%Y%m%d') <= '20191104':
                            print(1,item.pmpoint)
                            # transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.pmpoint * transitem.s_qty
                            transitem.thrpoint = 0

                        if transitem.create_time.strftime('%Y%m%d')>'20191104':
                            transitem.secpoint = item.secpoint * transitem.s_qty
                            transitem.thrpoint = 0

                        secperc= item.secperc + item.thrperc
                        thrperc=0

                    print('len(transitem.asscode2.strip())',len(transitem.asscode2.strip()))
                    if len(transitem.asscode2.strip()) > 0:
                        transitem.pmguideperc = 0
                        transitem.secguideperc = 0.5
                        transitem.thrguideperc = 0.5
                        transitem.pmperc=0
                        transitem.secperc=0.5
                        transitem.thprec=0.5
                        pmratio=0.33333
                        secratio=0.33333
                        thrratio=0.33333

                        if transitem.create_time.strftime('%Y%m%d')<='20191104':
                            # transitem.pmpoint = item.pmpoint * transitem.s_qty
                            if item.thrpoint ==0 :
                                transitem.secpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.pmpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                            else:
                                transitem.secpoint = item.pmpoint * transitem.s_qty
                                transitem.thrpoint = item.thrpoint * transitem.s_qty

                        if transitem.create_time.strftime('%Y%m%d')>'20191104':
                            # transitem.pmpoint = item.pmpoint * transitem.s_qty
                            if item.thrpoint ==0 :
                                transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                            else:
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = item.thrpoint * transitem.s_qty

                        secperc = (item.secperc + item.thrperc) /2
                        thrperc = (item.secperc + item.thrperc) /2

                    # transitem.pmperc = pmratio
                    # transitem.secperc = secratio
                    # transitem.thprec = thrratio

                    #     资金流水
                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                    print('secperc',secperc,'thrperc',thrperc)
                    if secperc>0:
                        transitem.secpoint = transitem.s_mount * Decimal(secperc) * Decimal( cashratio + cardratio)

                    if thrperc >0:
                        transitem.thrpoint = transitem.s_mount * Decimal(thrperc) * Decimal( cashratio + cardratio)
                    print('secpoint',transitem.secpoint,'thrperc',transitem.thrpoint)

                    #   服务操作流水   开单人员不计操作流水
                    # transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmperc) * Decimal(cardratio + cashratio) +\
                    #                             transitem.s_mount * Decimal(transitem.pmperc) * Decimal(sendratio) *Decimal(0.5)
                    #
                    # transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secperc) * Decimal(cardratio + cashratio) + \
                    #                            transitem.s_mount * Decimal(transitem.secperc) * Decimal(sendratio) * Decimal(0.5)
                    #
                    # transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thprec) * Decimal(cardratio + cashratio)+ \
                    #                            transitem.s_mount * Decimal(transitem.thprec) * Decimal(sendratio) * Decimal(0.5)


                    transitem.exp_basenum = transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal(cardratio + cashratio) +\
                                                transitem.s_mount * Decimal(transitem.pmguideperc) * Decimal(sendratio) *Decimal(0.5)

                    transitem.exp_secbasenum = transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(cardratio + cashratio) + \
                                               transitem.s_mount * Decimal(transitem.secguideperc) * Decimal(sendratio) * Decimal(0.5)

                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal(cardratio + cashratio)+ \
                                               transitem.s_mount * Decimal(transitem.thrguideperc) * Decimal(sendratio) * Decimal(0.5)

                    transitem.save()


            except:
                print('skipped',transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)

        print(transuuid.ttype, transitem.stype, transuuid.ccode, transuuid.cardtype)
        # 划储值卡购买产品、保健品算积点
        if transitem.ttype =='G':
            print(transitem.exptxserno,transitem.srvcode,len(transitem.srvcode))
            transitem.set_owegoods()
            transitem.set_goodstranslog()

            try:
                item = Goods.objects.filter(company=company).filter(gcode=transitem.srvcode).last()
                print(item.gcode,item.gname)
                if item.pmpoint == None:
                    pmpoint = 0
                if item.secpoint == None:
                    secpoint = 0
                if item.thrpoint == None:
                    thrpoint = 0
                if transitem.s_qty == None:
                    transitem.s_qty = 0

                # 赠送产品  员工什么都不算
                if transitem.stype=='P':
                    transitem.pmperc=0
                    transitem.secperc=0
                    transitem.thprec=0
                    transitem.pmguideperc=0
                    transitem.secguideperc=0
                    transitem.thrguideperc=0
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0
                    transitem.pmamount=0
                    transitem.secamount=0
                    transitem.thramount=0
                    transitem.pmpoint= 0
                    transitem.secpoint= 0
                    transitem.thrpoint = 0
                    pmratio = 0
                    secratio =0
                    thrratio =0

                    if len(transitem.pmcode.strip()) > 0:
                        pmratio=1
                        secratio=0
                        thrratio=0

                    if len(transitem.asscode1.strip()) > 0:
                        pmratio = 0.5
                        secratio = 0.5
                        thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        pmratio = 0.333
                        secratio = 0.333
                        thrratio = 0.333
                    transitem.pmperc = pmratio
                    transitem.secperc = secratio
                    transitem.thprec = thrratio

                    transitem.save()

                if transitem.stype=='N':
                    pmratio = 0
                    secratio =0
                    thrratio =0

                    if len(transitem.pmcode.strip()) > 0:
                        pmratio=1
                        secratio=0
                        thrratio=0

                    if len(transitem.asscode1.strip()) > 0:
                        pmratio = 0.5
                        secratio = 0.5
                        thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        pmratio = 0.333
                        secratio = 0.333
                        thrratio = 0.333

                    transitem.pmperc = pmratio
                    transitem.secperc = secratio
                    transitem.thprec = thrratio

                    transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)*Decimal(cardratio + cashratio)
                    transitem.exp_secbasenum= transitem.s_mount * Decimal(secratio)*Decimal(cardratio + cashratio)
                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)*Decimal(cardratio + cashratio)

                    transitem.pmamount =transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                    transitem.pmpoint = transitem.s_qty * Decimal(pmpoint)
                    transitem.secpoint = transitem.s_qty * Decimal(secpoint)
                    transitem.thrpoint = transitem.s_qty * Decimal(thrpoint)

                    transitem.save()
            except:
                print('skipped',transitem.exptxserno,transitem.srvcode,len(transitem.srvcode))

        if transitem.ttype in ('C','I'):
            print(transitem.ttype,transitem.exptxserno,transitem.srvcode,transitem.stype)
            transitem.pmperc = 0
            transitem.secperc = 0
            transitem.thprec = 0
            transitem.pmguideperc = 0
            transitem.secguideperc = 0
            transitem.thrguideperc = 0
            transitem.exp_basenum = 0
            transitem.exp_secbasenum = 0
            transitem.exp_thrbasenum = 0
            transitem.pmamount = 0
            transitem.secamount = 0
            transitem.thramount = 0
            transitem.pmpoint = 0
            transitem.secpoint = 0
            transitem.thrpoint = 0

            try:
                cardinfo = Cardinfo.objects.filter(company=company).filter(ccode=transitem.srvcode).last()
                print(cardinfo.ccode)
                if cardinfo.cardtype==None:
                    cardtype=''
                else:
                    cardtype=cardinfo.cardtype
            except:
                print(transitem.exptxserno,transitem.ttype,transitem.srvcode)
                cardtype=''

            try:
                item = Cardtype.objects.filter(company=company, flag='Y', cardtype=cardtype).last()
                if item.pmpoint == None:
                    pmpoint = 0
                if item.secpoint == None:
                    secpoint = 0
                if item.thrpoint == None:
                    thrpoint = 0
                if transitem.s_qty == None:
                    s_qty = 0
            except:
                print(cardinfo,transitem.srvcode,transuuid.exptxserno)
                pmpoint=0
                secpoint=0
                thrpoint=0


            # 赠送的卡项，什么都不算
            if transitem.stype == 'P':
                transitem.pmperc = 0
                transitem.secperc = 0
                transitem.thprec = 0
                transitem.pmguideperc = 0
                transitem.secguideperc = 0
                transitem.thrguideperc = 0
                transitem.exp_basenum = 0
                transitem.exp_secbasenum = 0
                transitem.exp_thrbasenum = 0
                transitem.pmamount = 0
                transitem.secamount = 0
                transitem.thramount = 0
                transitem.pmpoint = 0
                transitem.secpoint = 0
                transitem.thrpoint = 0

                pmratio = 0
                secratio = 0
                thrratio = 0

                if len(transitem.pmcode.strip()) > 0:
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                if len(transitem.asscode1.strip()) > 0:
                    pmratio = 0.5
                    secratio = 0.5
                    thrratio = 0

                if len(transitem.asscode2.strip()) > 0:
                    pmratio = 0.33333
                    secratio = 0.33333
                    thrratio = 0.33333

                transitem.pmperc = pmratio
                transitem.secperc = secratio
                transitem.thprec = thrratio
                transitem.save()

            if transitem.stype=='N':
                pmratio = 0
                secratio = 0
                thrratio = 0

                if len(transitem.pmcode.strip()) > 0:
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                if len(transitem.asscode1.strip()) > 0:
                    pmratio = 0.5
                    secratio = 0.5
                    thrratio = 0

                if len(transitem.asscode2.strip()) > 0:
                    pmratio = 0.33333
                    secratio = 0.33333
                    thrratio = 0.33333

                print('transitem item',transitem.s_mount,cashratio,pmratio)
                transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                # 计算疗程卡销售流水
                if (item.suptype=='20') and (item.comptype=='times'):
                    transitem.exp_basenum = transitem.s_mount * Decimal(pmratio) * Decimal(cashratio + cardratio)
                    transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio) * Decimal(cashratio + cardratio)
                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio) * Decimal(cashratio + cardratio)

                    transitem.pmperc = pmratio
                    transitem.secperc = secratio
                    transitem.thprec = thrratio

                if (item.suptype=='25') or (item.comptype=='period'):
                    transitem.exp_basenum = transitem.s_mount * Decimal(pmratio) * Decimal(cashratio + cardratio)
                    transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio) * Decimal(cashratio + cardratio)
                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio) * Decimal(cashratio + cardratio)

                    transitem.pmperc = pmratio
                    transitem.secperc = secratio
                    transitem.thprec = thrratio

                transitem.save()

    return  0


EMPL_ARCHEMENT_BYMONTH_YIREN = " select   e.ecode ecode , e.ename ename, e.team team, substring(a.vsdate,1,6) month ,(case b.ttype when 'S' then '服务' when 'G' then '商品' else '售卡' end ) level2, "\
                " GetAppoptionValue(b.company,'financeclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'financeclass1',b.company) )  level3, "\
                " GetAppoptionValue(b.company,'brand',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'brand',b.company) )  brand, "\
                " count( distinct if(a.ttype ='C',NULL, vipuuid) ) vipcnt, count(distinct vsdate, if(a.ttype ='C',NULL, vipuuid)) viptimes, "\
                " sum(b.s_qty) s_qty, sum(b.s_mount) s_mount , sum(b.pmamount) yejiamount , "\
                "		sum(case b.stype when 'N' then (case b.ttype when 'S' then b.s_mount when 'G' then b.s_mount else 0 end ) else 0 end ) * ifnull(pmguideperc,0)  shihao,  0 shichao"\
                " from expvstoll a, expense b , empl e"\
                " where 1=1 and a.valiflag='Y' and a.flag='Y' and b.flag='Y' "\
                " and a.company=b.company  and a.company = e.company AND a.uuid = b.transuuid "\
                " and a.company=%s "\
                " and a.storecode in (%s) "\
                " and substring(a.vsdate,1,6) = %s "\
                " and b.pmcode = e.ecode and e.ecode=%s "\
                " group by  ecode, ename, team, month,  level2, level3,brand "\
                " union all "\
                " select   e.ecode ecode , e.ename ename, e.team team, substring(a.vsdate,1,6) month ,(case b.ttype when 'S' then '服务' when 'G' then '商品' else '售卡' end ) level2, "\
                " GetAppoptionValue(b.company,'financeclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'financeclass1',b.company) )  level3, "\
                " GetAppoptionValue(b.company,'brand',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'brand',b.company) )  brand, "\
                " count( distinct if(a.ttype ='C',NULL, vipuuid) ) vipcnt, count(distinct vsdate, if(a.ttype ='C',NULL, vipuuid)) viptimes, "\
                " sum(b.s_qty) s_qty, sum(b.s_mount) s_mount , sum(b.secamount) yejiamount , "\
                "	0 shihao,	sum(case b.stype when 'N' then (case b.ttype when 'S' then b.s_mount when 'G' then b.s_mount else 0 end ) else 0 end ) * ifnull(secguideperc,0) shichao"\
                " from expvstoll a, expense b , empl e"\
                " where 1=1 and a.valiflag='Y' and a.flag='Y' and b.flag='Y' "\
                " and a.company=b.company  and a.company = e.company AND a.uuid = b.transuuid "\
                " and a.company=%s "\
                " and a.storecode in (%s) "\
                " and substring(a.vsdate,1,6) = %s "\
                " and b.asscode1 = e.ecode and e.ecode=%s "\
                " group by  ecode, ename, team, month,  level2, level3,brand " \
                " union all" \
                " select   e.ecode ecode , e.ename ename, e.team team, substring(a.vsdate,1,6) month ,(case b.ttype when 'S' then '服务' when 'G' then '商品' else '售卡' end ) level2, "\
                " GetAppoptionValue(b.company,'financeclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'financeclass1',b.company) )  level3, "\
                " GetAppoptionValue(b.company,'brand',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'brand',b.company) )  brand, "\
                " count( distinct if(a.ttype ='C',NULL, vipuuid) ) vipcnt, count(distinct vsdate, if(a.ttype ='C',NULL, vipuuid)) viptimes, "\
                " sum(b.s_qty) s_qty, sum(b.s_mount) s_mount , sum(b.thramount) yejiamount , "\
                "	0 shihao,	sum(case b.stype when 'N' then (case b.ttype when 'S' then b.s_mount when 'G' then b.s_mount else 0 end ) else 0 end ) * ifnull(thrguideperc,0) shichao"\
                " from expvstoll a, expense b , empl e"\
                " where 1=1 and a.valiflag='Y' and a.flag='Y' and b.flag='Y' "\
                " and a.company=b.company  and a.company = e.company AND a.uuid = b.transuuid "\
                " and a.company=%s "\
                " and a.storecode in (%s) "\
                " and substring(a.vsdate,1,6) = %s "\
                " and b.asscode2 = e.ecode and e.ecode=%s "\
                " group by  ecode, ename, team, month,  level2, level3,brand "


EMPL_ARCHEMENT_BYDAILY_YIREN="  select  Getemplinfo(b.company,b.pmcode,'position') position,  b.pmcode, f_getinfobycode(b.pmcode,'E','ename',b.company) ename , a.vsdate, a.cdate, b.ttype,"\
                             "       GetAppoptionValue(b.company,'financeclass1',F_Getinfobycode(b.srvcode,b.ttype,'financeclass1',b.company) ) srvrptype, "\
                             "    b.srvcode, F_Getnamebysrvcode(b.srvcode, b.ttype,b.company) srvname, b.stype, b.s_qty,b.s_price, b.s_mount,  "\
                             "   b.pmamount xamount,b.pmpoint point, "\
                             "   (case b.ttype when 'S' then b.exp_basenum else 0 end) s_basenum, "\
                             "   (case b.ttype when 'G' then b.exp_basenum else 0 end)  g_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_basenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_basenum , 0 )"\
                             "           else 0 end )  c20_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_basenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_basenum , 0 )"\
                             "           else 0 end )  c25_basenum,         0 cnt, "\
                             "   getserno(b.exptxserno, 'EXPVSTOLL_') serno, b.ditem  , b.exptxserno txserno, v.vname,v.vcode, a.storecode,v.viptype "\
                             "   from expvstoll a, expense b , vip v"\
                             "   where 1=1"\
                             "   and a.valiflag ='Y'"\
                             "   and a.company = b.company"\
                             "   and a.company=%s"\
                             "   and a.storecode  in (%s)"\
                             "   AND a.uuid = b.transuuid"\
                             "   and a.vipuuid=v.uuid"\
                             "   and substring(a.cdate,1,6) = %s "\
                             "   and b.pmcode =%s "\
                             "   and length(trim(b.pmcode)) >0"\
                             "   union all"\
                             "   select  Getemplinfo(b.company,b.asscode1,'position')  position, b.asscode1, f_getinfobycode(b.asscode1,'E','ename',b.company) ename ,a.vsdate, a.cdate, b.ttype,"\
                             "       GetAppoptionValue(b.company,'financeclass1',F_Getinfobycode(b.srvcode,b.ttype,'financeclass1',b.company) ) srvrptype, "\
                             "    b.srvcode, F_Getnamebysrvcode(b.srvcode, b.ttype,b.company) srvname, b.stype,  b.s_qty,b.s_price, b.s_mount,  "\
                             "   b.secamount xamount,b.secpoint point, "\
                             "   (case b.ttype when 'S' then b.exp_secbasenum else 0 end) s_basenum, "\
                             "   (case b.ttype when 'G' then b.exp_secbasenum else 0 end)  g_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_secbasenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_secbasenum , 0 )"\
                             "           else 0 end )  c20_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_secbasenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_secbasenum , 0 )"\
                             "           else 0 end )  c25_basenum,        (case b.ttype when 'S' then b.stdmins*b.secperc else 0 end) cnt, "\
                             "   getserno(b.exptxserno, 'EXPVSTOLL_') serno, b.ditem  , b.exptxserno txserno, v.vname,v.vcode, a.storecode,v.viptype "\
                             "   from expvstoll a, expense b , vip v"\
                             "   where 1=1"\
                             "   and a.valiflag ='Y'"\
                             "   and a.company = b.company"\
                             "   and a.company=%s"\
                             "   and a.storecode  in (%s)"\
                             "   AND a.uuid = b.transuuid"\
                             "   and a.vipuuid = v.uuid"\
                             "   and substring(a.cdate,1,6) = %s "\
                             "   and b.asscode1 =%s "\
                             "   and length(trim(b.asscode1)) >0"\
                             "   union all"\
                             "   select  Getemplinfo(b.company,b.asscode2,'position') position, b.asscode2, f_getinfobycode(b.asscode2,'E','ename',b.company) ename ,a.vsdate, a.cdate, b.ttype, "\
                             "       GetAppoptionValue(b.company,'financeclass1',F_Getinfobycode(b.srvcode,b.ttype,'financeclass1',b.company) ) srvrptype, "\
                             "  b.srvcode, F_Getnamebysrvcode(b.srvcode, b.ttype,b.company) srvname, b.stype, b.s_qty,b.s_price, b.s_mount,  "\
                             "   b.thramount xamount,b.thrpoint point, "\
                             "   (case b.ttype when 'S' then b.exp_thrbasenum else 0 end) s_basenum, "\
                             "   (case b.ttype when 'G' then b.exp_thrbasenum else 0 end)  g_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_thrbasenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '20', b.exp_thrbasenum , 0 )"\
                             "           else 0 end )  c20_basenum,"\
                             "   (case b.ttype when 'C' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_thrbasenum , 0 )"\
                             "                 when 'I' then if(getcardsuptype(getcardtype(b.srvcode,b.company),b.company)= '25', b.exp_thrbasenum , 0 )"\
                             "           else 0 end )  c25_basenum,         (case b.ttype when 'S' then b.stdmins*b.thprec else 0 end)  cnt, "\
                             "   getserno(b.exptxserno, 'EXPVSTOLL_') serno, b.ditem  , b.exptxserno txserno,v.vname,v.vcode, a.storecode,v.viptype "\
                             "   from expvstoll a, expense b , vip v"\
                             "   where 1=1"\
                             "   and a.valiflag ='Y'"\
                             "   and a.company = b.company"\
                             "   and a.company=%s"\
                             "   and a.storecode  in (%s)"\
                             "   AND a.uuid = b.transuuid"\
                             "   and a.vipuuid = v.uuid"\
                             "    and substring(a.cdate,1,6) = %s "\
                             "     and b.asscode2 =%s "\
                             "   and length(trim(b.asscode2)) >0"

def get_ttypename(ttype):
    if ttype=='S':
        return '服务'

    if ttype=='G':
        return '商品'

    if ttype=='C':
        return '售卡'

    if ttype=='I':
        return '充值'

def get_stypename(stype):
    if stype=='N':
        return '正常'

    if stype=='P':
        return '赠送'

def get_viptypename(viptype):
    if viptype=='10':
        return '会员'

    if viptype=='20':
        return '散客'

    if viptype=='30':
        return '潜在客户'

    if viptype=='60':
        return '内部员工'

# def get_emplarchdetail_byecode_yiren(request):
def get_emplarchdetail_byecode_yiren(company,storecode,ecode,month,filename):

    # company=request.GET['yiren']
    # storecode = request.GET['storecode']
    # ecode = request.GET['ecode']
    # month = request.GET['month']

    # ecode='1011'
    # month ='202001'
    # expense = Expense.objects.filter(company=company,transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).\
    #     values('pmcode','ttype','srvcode').annotate()

    sql = EMPL_ARCHEMENT_BYDAILY_YIREN

    params=(company+' '+ storecode + ' '+ month +  ' ' +ecode  +' '+company+' '+ storecode + ' '+ month+ ' ' +ecode + ' ' +company + ' '+ storecode + ' '+ month + ' ' +ecode   ).split()
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)

    df = pd.read_json(json_data,encoding="utf-8", orient='records')
    print('df',df)
    if df.empty:
        return ''

    df['ttypename'] = df.apply(lambda x : get_ttypename(x.ttype),axis = 1)
    df['stypename'] = df.apply(lambda x : get_stypename(x.stype),axis = 1)
    df['viptypename'] = df.apply(lambda x : get_viptypename(x.viptype),axis = 1)
    print('df1',df)

    columnorder=['storecode','position','pmcode','ename','stypename','ttypename','srvrptype','vsdate','cdate','viptype','vcode','vname','srvcode','srvname','s_qty','s_price','s_mount',
                 'point','xamount','s_basenum','g_basenum','c20_basenum','c25_basenum','cnt','serno']
    df= df[columnorder]
    print('df2',df)

    df.rename(columns={"txserno": "流水号","position":"角色","c20_basenum":"疗程卡流水","s_basenum":"服务流水","xamount":"资金流水","g_basenum":"商品流水","s_mount":"项目金额","srvname":"项目名称",
                       "viptype":"客户类型","vname":"客户姓名","s_qty":"数量","stypename":"是否赠送","c25_basenum":"附卡流水","srvcode":"项目编号","srvrptype":"项目分类","vcode":"会员号",
                       "cnt":"项次","ditem":"项次序号","ename":"员工姓名","pmcode":"工号","ttypename":"交易类型","point":"固定提成","storecode":"门店","vsdate":"交易日期","cdate":"记账日期",
                       "s_price":"单价","serno":"流水号" }, inplace=True)
    print('df3',df)
    # df.to_excel("c:\tmp\empl.xls")
    # filename = 'c:/tmp/yirendata/'+storecode+'-'+ecode+'-202001.xlsx'
    df.to_excel(filename,'sheet1')

    # return '0'
    return HttpResponse('0', content_type="application/json")


def get_saveemplarch(request):
    company=request.GET['company']
    empls = Empl.objects.filter(company=company,status='Y',storecode='04').order_by('storecode','ecode')
    for empl in empls:
        storecode=empl.storecode
        ecode=empl.ecode
        month='202001'
        filename="c:/tmp/yirendata/" +storecode + '-' + empl.ename+'-202001.xlsx'
        if (len(storecode)>0 and  len(ecode)>0 and len(empl.ename)>0):
            print('params',storecode,ecode,empl.ename)
            # url = 'http://localhost:8080/cashier/get_saveemplarch/?company='+company+'&storecode='+storecode+"&ecode="+ecode+"&month="+month
            #
            # print(url)
            # data= requests.get(url=url)
            get_emplarchdetail_byecode_yiren(company,storecode, ecode, month,filename)

    return  HttpResponse('完成', content_type="application/json")


class EmplArchivement(object):
    def __init__(self,**kwargs):
        self.company = kwargs.get('company','yiren')
        self.fromdate = kwargs.get('fromdate','20201101').replace('-','')
        self.todate = kwargs.get('todate','20201110').replace('-','')
        self.ecode = kwargs.get('ecode','1101')
        self.reportdata=[]


        self.trans = Expvstoll.objects.filter(company=self.company,flag='Y',valiflag='Y',vsdate__gte=self.fromdate,vsdate__lte=self.todate)

    def get_vipcnt(self):
        self.vipcnt = Expense.objects.filter(transuuid_id__in=self.trans,ttype__in=('S','G')).filter( Q(pmcode = self.ecode) | Q(asscode1 = self.ecode) | Q(asscode2= self.ecode))\
            .values('transuuid_id__vipuuid').distinct().count()
        item={'itemname':'客数','value': self.vipcnt}
        self.reportdata.append(item)

    def get_viptimes(self):
        self.viptimes = Expense.objects.filter(transuuid_id__in=self.trans,ttype__in=('S','G')).filter(Q(pmcode=self.ecode) | Q(asscode1=self.ecode) | Q( asscode2 =self.ecode)).values('transuuid_id__vsdate','transuuid_id__vipuuid').distinct().count()
        item={'itemname':'客次','value':self.viptimes}
        self.reportdata.append(item)

    def get_itemcnt(self):
        sec_itemcnt_data = Expense.objects.filter(transuuid_id__in=self.trans,ttype__in=('S'),asscode1=self.ecode).values('asscode1').annotate(itemcnt= Sum(F('stdmins')*F('secperc'))).values('itemcnt')
        thr_itemcnt_data = Expense.objects.filter(transuuid_id__in=self.trans,ttype__in=('S'),asscode2=self.ecode).values('asscode2').annotate(itemcnt= Sum(F('stdmins')*F('thprec'))).values('itemcnt')
        if len(sec_itemcnt_data) > 0:
            sec_itemcnt = list(sec_itemcnt_data)[0]['itemcnt']
        else:
            sec_itemcnt =0
        if len(thr_itemcnt_data) > 0:
            thr_itemcnt = list(thr_itemcnt_data)[0]['itemcnt']
        else:
            thr_itemcnt =0

        self.itemcnt = round(sec_itemcnt + thr_itemcnt,2)

        item={'itemname':'项次','value':self.itemcnt}
        self.reportdata.append(item)

    def get_amounts(self):
        # 资金流水
        result_data = Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode).values('pmcode').annotate(cashamount= Sum('pmamount')).values('cashamount')
        if len(result_data) == 0:
            pm_cashamount = 0
        else:
            pm_cashamount = result_data[0]['cashamount']

        result_data = Expense.objects.filter(transuuid_id__in=self.trans,asscode1=self.ecode).values('asscode1').annotate(cashamount= Sum('secamount')).values('cashamount')
        if len(result_data) == 0:
            sec_cashamount = 0
        else:
            sec_cashamount = result_data[0]['cashamount']

        result_data = Expense.objects.filter(transuuid_id__in=self.trans,asscode2=self.ecode).values('asscode2').annotate(cashamount= Sum('thramount')).values('cashamount')
        if len(result_data) == 0:
            thr_cashamount = 0
        else:
            thr_cashamount = result_data[0]['cashamount']
        self.cashamount = pm_cashamount + sec_cashamount + thr_cashamount
        item={'itemname':'资金流水','value':self.cashamount}
        self.reportdata.append(item)

        # 固定提成
        result_data = Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode).values('pmcode').annotate(point= Sum('pmpoint')).values('point')
        if len(result_data) == 0:
            pm_point = 0
        else:
            pm_point = result_data[0]['point']
        result_data = Expense.objects.filter(transuuid_id__in=self.trans,asscode1=self.ecode).values('asscode1').annotate(point= Sum('secpoint')).values('point')
        if len(result_data) == 0:
            sec_point = 0
        else:
            sec_point = result_data[0]['point']
        result_data = Expense.objects.filter(transuuid_id__in=self.trans,asscode2=self.ecode).values('asscode2').annotate(point= Sum('thrpoint')).values('point')
        if len(result_data) == 0:
            thr_point = 0
        else:
            thr_point = result_data[0]['point']
        self.point = pm_point + sec_point + thr_point
        item={'itemname':'固定提成','value':self.point}
        self.reportdata.append(item)

        # 服务流水
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='S').values('pmcode').annotate(s_amount= Sum('exp_basenum')).values('s_amount')
        if len(result_data) == 0:
            pm_s_amount = 0
        else:
            pm_s_amount = result_data[0]['s_amount']
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='S').values('asscode1').annotate(s_amount= Sum('exp_secbasenum')).values('s_amount')
        if len(result_data) == 0:
            sec_s_amount = 0
        else:
            sec_s_amount = result_data[0]['s_amount']
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='S').values('asscode2').annotate(s_amount= Sum('exp_thrbasenum')).values('s_amount')
        if len(result_data) == 0:
            thr_s_amount = 0
        else:
            thr_s_amount = result_data[0]['s_amount']
        self.s_amount = pm_s_amount + sec_s_amount + thr_s_amount
        item={'itemname':'服务流水','value':self.s_amount}
        self.reportdata.append(item)

        # 商品流水
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='G').values('pmcode').annotate(g_amount= Sum('exp_basenum')).values('g_amount')
        if len(result_data) == 0:
            pm_g_amount = 0
        else:
            pm_g_amount = result_data[0]['g_amount']
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='G').values('asscode1').annotate(g_amount= Sum('exp_secbasenum')).values('g_amount')
        if len(result_data) == 0:
            sec_g_amount = 0
        else:
            sec_g_amount = result_data[0]['g_amount']
        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype='G').values('asscode2').annotate(g_amount= Sum('exp_thrbasenum')).values('g_amount')
        if len(result_data) == 0:
            thr_g_amount = 0
        else:
            thr_g_amount = result_data[0]['g_amount']
        self.g_amount = pm_g_amount + sec_g_amount + thr_g_amount
        item={'itemname':'商品流水','value':self.g_amount}
        self.reportdata.append(item)

        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype__in = ('C','I')).values('pmcode').annotate(c_amount= Sum('exp_basenum')).values('c_amount')
        if len(result_data) == 0:
            pm_c_amount = 0
        else:
            pm_c_amount = result_data[0]['c_amount']

        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype__in=('C','I')).values('asscode1').annotate(c_amount= Sum('exp_secbasenum')).values('c_amount')
        if len(result_data) == 0:
            sec_c_amount = 0
        else:
            sec_c_amount = result_data[0]['c_amount']

        result_data =  Expense.objects.filter(transuuid_id__in=self.trans,pmcode=self.ecode,ttype__in=('C','I')).values('asscode2').annotate(c_amount= Sum('exp_thrbasenum')).values('c_amount')
        if len(result_data) == 0:
            thr_c_amount = 0
        else:
            thr_c_amount = result_data[0]['c_amount']

        self.c_amount = pm_c_amount + sec_c_amount + thr_c_amount
        item = {'itemname': '售卡流水', 'value': self.c_amount}
        self.reportdata.append(item)


