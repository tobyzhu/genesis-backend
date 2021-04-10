from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from decimal import *

from .models import Expvstoll,Expense,Toll,EmplArchivementDetail
from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode
from adviser.models import Cardinfo

import common.constants

# Create your views here.
SUPTYPE10LIST=['101','102','103','104','110','111','112','113','114','115','116','120','121']
# 产品卡
GOODS_CARDTYPELIST = ['201', '203', '301','302']
# 肝胆卡

GOODS_CARDTYPELIST_1 = ['201', '203', '301']
GOODS_CARDTYPELIST_2 = ['302']

SPEC_CARDLIST1 =['306']

def cal_empalarch_yfy_daily(request):
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']

    set_exp_basenum_yfy('01', fromdate, todate)
    set_exp_xamount_yfy_01(fromdate, todate)
    set_exp_basenum_yfy('02', fromdate, todate)
    set_exp_xamount_yfy_02(fromdate, todate)
    set_exp_basenum_yfy('03', fromdate, todate)
    set_exp_xamount_yfy_03(fromdate, todate)
    set_exp_basenum_yfy('04', fromdate, todate)
    set_exp_xamount_yfy_04(fromdate, todate)
    set_exp_basenum_yfy('05', fromdate, todate)
    set_exp_xamount_yfy_05(fromdate, todate)

    return HttpResponse(1, content_type="application/json")


def cal_emplarch_yfy(request):
    company='yfy'
    storecode=request.GET['storecode']
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']

    if storecode =='01':
        set_exp_basenum_yfy(storecode, fromdate,todate)
        set_exp_xamount_yfy_01(fromdate,todate)

    if storecode == '02':
        set_exp_basenum_yfy_02(storecode, fromdate, todate)
        set_exp_xamount_yfy_02(fromdate, todate)

    if storecode == '03':
        set_exp_basenum_yfy(storecode,fromdate, todate)
        set_exp_xamount_yfy_03(fromdate, todate)

    if storecode == '04':
        set_exp_basenum_yfy(storecode,fromdate, todate)
        set_exp_xamount_yfy_04(fromdate, todate)

    if storecode == '05':
        set_exp_basenum_yfy(storecode, fromdate, todate)
        set_exp_xamount_yfy_05(fromdate, todate)

    return HttpResponse(1, content_type="application/json")


def cal_emplarch_exp_basenum(request):
    company=common.constants.COMPANYID
    fromdate=request.GET['fromdate']
    todate=request.GET['todate']
    transuuids = Expvstoll.objects.filter(company=company,valiflag='Y').filter(vsdate__gte=fromdate).filter(vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    ttypes = ['S','G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company,flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)

        for transitem in transitems:
            print(transitem.create_time, transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''
            if transitem.s_qty==None:
                transitem.s_qty=0

            if transitem.ttype=='S':
                item=Serviece.objects.filter(company=company,flag='Y').filter(svrcdoe=transitem.srvcode).last()

            if transitem.ttype=='G':
                item=Goods.objects.filter(company=company,flag='Y').filter(gcode=transitem.srvcode).last()

            if transitem.ttype in ('C','I'):
                print('transitem',transitem)
                cardinfo=Cardinfo.objects.filter(company=company,flag='Y',status='O').filter(ccode=transitem.srvcode).last()
                print('cardinfo:',cardinfo)
                if cardinfo==None:
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0
                else:
                    item = Cardtype.objects.filter(company=company,flag='Y').filter(cardtype=cardinfo.cardtype).last()
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0

                transitem.save()

            if item.pmpoint ==None:
                item.pmpoint=0
            if item.secpoint==None:
                item.secpoint=0
            if item.thrpoint==None:
                item.thrpoint =0

            if transitem.ttype =='S':
                if transitem.s_qty == None:
                    transitem.s_qty = 0

                if transitem.stype=='P':
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.pmpoint=item.pmpoint  * transitem.s_qty
                    transitem.secpoint= item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                    if len(transitem.asscode1.strip())>0:
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = item.secpoint * transitem.s_qty
                        transitem.thrpoint = 0
                    if len(transitem.asscode2.strip())>0 :
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = ( item.secpoint + item.thrpoint ) * transitem.s_qty * Decimal(0.5)
                        transitem.thrpoint = ( item.secpoint + item.thrpoint ) * transitem.s_qty * Decimal(0.5)

                if transitem.stype=='N':
                    transitem.exp_basenum=transitem.s_mount
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0

                    if len(transitem.asscode1.strip())>0:
                        transitem.exp_secbasenum=transitem.s_mount
                    if len(transitem.asscode2.strip())>0 :
                        transitem.exp_secbasenum=transitem.s_mount * Decimal(0.5)
                        transitem.exp_thrbasenum=transitem.s_mount * Decimal(0.5)

                    # transitem.pmperc=item.pmperc
                    # transitem.secperc=item.secperc
                    # transitem.thprec=item.thrperc
                    # transitem.pmguideperc=item.pmguideperc
                    # transitem.secguideperc=item.secguideperc

                transitem.save()

            if transitem.ttype =='G':
                if transitem.stype=='P':
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.pmpoint=item.pmpoint * transitem.s_qty
                    transitem.secpoint= item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                if transitem.stype=='N':
                    transitem.exp_basenum=transitem.s_mount
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0

                    if len(transitem.asscode1.strip())>0:
                        transitem.exp_basenum = transitem.s_mount * Decimal(0.5)
                        transitem.exp_secbasenum=transitem.s_mount * Decimal(0.5)
                        transitem.exp_thrbasenum=0
                    if len(transitem.asscode2.strip())>0 :
                        transitem.exp_basenum = transitem.s_mount * Decimal(0.5)
                        transitem.exp_secbasenum=transitem.s_mount * Decimal(0.25)
                        transitem.exp_thrbasenum=transitem.s_mount * Decimal(0.25)

                    # transitem.pmperc=item.pmperc
                    # transitem.secperc=item.secperc
                    # transitem.thprec=item.thrperc
                    # transitem.pmguideperc=item.pmguideperc
                    # transitem.secguideperc=item.secguideperc

                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")


# 积点计算规则：
#   1、计算固定提成及积点
#   2、从储值卡做 纹绣类-400。手术类-500 服务算积点
#   3、从储值卡购买产品、保健品算积点，
#   4、从产品卡，保健品卡、肝胆卡 够产品不算积点
#   5、从储值卡购买产品卡、保健品卡，肝胆卡 算积点
#   6，pmguideperc 顾问实耗计算比例    secguideperc thrguideperc 美疗师实耗计算比例
def set_exp_basenum_yfy(storecode, fromdate,todate):
    company=common.constants.COMPANYID
    transuuids = Expvstoll.objects.filter(company=company,valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate,vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    ttypes = ['S','G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company,flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)

        for transitem in transitems:
            print(transitem.create_time, transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''
            if transitem.s_qty==None:
                transitem.s_qty=0

            # 纹绣，手术算积点
            if transitem.ttype =='S':
                item = Serviece.objects.filter(company=company, flag='Y').filter(svrcdoe=transitem.srvcode).last()

                if item.pmpoint == None:
                    item.pmpoint = 0
                if item.secpoint == None:
                    item.secpoint = 0
                if item.thrpoint == None:
                    item.thrpoint = 0
                if transitem.s_qty == None:
                    transitem.s_qty = 0

                #     计算赠送类固定提成 按点数计算
                if transitem.stype == 'P':
                    transitem.pmperc=0
                    transitem.secperc=0
                    transitem.thprec=0
                    transitem.pmguideperc=0
                    transitem.secguideperc=0
                    transitem.thrguideperc=0
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint = item.pmpoint * transitem.s_qty
                    transitem.secpoint = item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                    if len(transitem.asscode1.strip()) > 0:
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = item.secpoint * transitem.s_qty
                        transitem.thrpoint = 0
                        transitem.secperc=1
                        transitem.thprec=0
                    if len(transitem.asscode2.strip()) > 0:
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                        transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                        transitem.secperc=0.5
                        transitem.thrprec=0.5
                    transitem.save()

                # 设置实操拆分比例
                if transitem.stype == 'N':
                    transitem.pmguideperc = 1
                    transitem.secguideperc = 0
                    transitem.thrguideperc = 0

                    if len(transitem.asscode1.strip()) > 0:
                        transitem.pmguideperc = 1
                        transitem.secguideperc = 1
                        transitem.thrguideperc = 0
                    if len(transitem.asscode2.strip()) > 0:
                        transitem.pmguideperc = 1
                        transitem.secguideperc = 0.5
                        transitem.thrguideperc = 0.5

                    # 手术类不计美疗师实操，只记顾问实耗
                    if item.topcode =='500':
                        transitem.pmguideperc=1
                        transitem.secguideperc=0
                        transitem.thrguideperc=0

                    transitem.save()

                print(transuuid.ttype, transitem.stype, transuuid.ccode,transuuid.cardtype,item.topcode)
                # try:
                if transuuid.cardtype in SUPTYPE10LIST:
                    # paycardinfo = Cardinfo.objects.filter(company=company, storecode=storecode, flag='Y',
                    #                                       status='O',ccode=transuuid.ccode).last()
                    print(transuuid.cardtype, item.topcode)

                    # 只有主卡卡付 手术计算积点
                    if item.topcode in ('400','500'):
                        if transitem.stype=='N':
                            pmratio = 1
                            secratio = 0
                            thrratio = 0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.8
                                secratio = 0.2
                                thrratio = 0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.8
                                secratio = 0.1
                                thrratio = 0.1
                        else:
                            transitem.exp_basenum = 0
                            transitem.exp_secbasenum = 0
                            transitem.exp_thrbasenum = 0
                            transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.secpoint * transitem.s_qty
                            transitem.thrpoint = item.thrpoint * transitem.s_qty

                            if len(transitem.asscode1.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = 0
                            if len(transitem.asscode2.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                        transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)
                        transitem.save()

                    # 只有主卡卡付 纹绣计算积点   只计顾问纹绣积点，美容师不计积点
                    if transuuid.storecode=='01' and item.topcode in ('400'):
                        if transitem.stype=='N':
                            pmratio = 1
                            secratio = 0
                            thrratio = 0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 1
                                secratio = 0
                                thrratio = 0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 1
                                secratio = 0
                                thrratio = 0
                        else:
                            transitem.exp_basenum = 0
                            transitem.exp_secbasenum = 0
                            transitem.exp_thrbasenum = 0
                            transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.secpoint * transitem.s_qty
                            transitem.thrpoint = item.thrpoint * transitem.s_qty

                            if len(transitem.asscode1.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = 0
                            if len(transitem.asscode2.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                        transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)
                        transitem.save()
                # except:
                else:
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0
                    transitem.save()
                #         topcode not in 400 500 ,不算积点，只算提成
                # else:
                #     pmratio  = 0
                #     secratio = 0
                #     thrratio = 0
                #
                #     transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                #     transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                #     transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)
                #
                #     transitem.save()

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
                        transitem.pmpoint= pmpoint  * transitem.s_qty
                        transitem.secpoint= secpoint * transitem.s_qty
                        transitem.thrpoint = thrpoint * transitem.s_qty

                        if len(transitem.asscode1.strip())>0:
                            transitem.pmpoint = pmpoint * transitem.s_qty
                            transitem.secpoint = secpoint * transitem.s_qty
                            transitem.thrpoint = 0
                        if len(transitem.asscode2.strip())>0 :
                            transitem.pmpoint = pmpoint * transitem.s_qty
                            transitem.secpoint = ( secpoint + thrpoint ) * transitem.s_qty * Decimal(0.5)
                            transitem.thrpoint = ( secpoint + thrpoint ) * transitem.s_qty * Decimal(0.5)

                    # 非赠送类的商品销售，算顾问实耗，不算美容师实耗

                    if transitem.stype=='N':
                        transitem.pmguideperc=1
                        transitem.secguideperc=0
                        transitem.thrguideperc=0

                except:
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint =0
                    transitem.secpoint=0
                    transitem.thrpoint=0

                if transitem.stype=='N':
                    pmratio = 0
                    secratio =0
                    thrratio =0
                    try:
                        paycardinfo = Cardinfo.objects.filter(company=company, flag='Y', status='O').filter(
                            ccode=transuuid.ccode).last()
                        # 产品卡扣产品，不计积点
                        if transuuid.cardtype in GOODS_CARDTYPELIST:
                            pmratio=0
                            secratio=0
                            thrratio=0

                        # 储值卡扣产品，计算积点
                        if transuuid.cardtype in SUPTYPE10LIST :
                            pmratio = 1
                            secratio = 0
                            thrratio = 0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.6
                                secratio = 0.4
                                thrratio = 0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.6
                                secratio = 0.2
                                thrratio = 0.2

                    except:
                        pmratio =0
                        secratio =0
                        thrratio =0

                        # if len(transitem.asscode1.strip())>0:
                        #     pmratio =0.6
                        #     secratio =0.4
                        #     thrratio =0
                        #
                        # if len(transitem.asscode2.strip())>0 :
                        #     pmratio =0.6
                        #     secratio =0.2
                        #     thrratio =0.2
                    transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                    transitem.exp_secbasenum= transitem.s_mount * Decimal(secratio)
                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)

                transitem.save()

            # print(transitem.ttype,transitem.stype)
            # 购买产品卡、保健品卡 肝胆卡 算积点
            if transitem.ttype in ('C','I'):
                print(transitem.ttype,transitem.exptxserno,transitem.srvcode,transitem.stype)
                # item=Goods.objects.get(company=company,flag='Y').filter(gcode=transuuid.srvcode)
                # try:
                #     cardinfo = Cardinfo.objects.filter(company=company).filter(ccode=transitem.srvcode).last()
                #     print(cardinfo.ccode)
                #     if cardinfo.cardtype==None:
                #         cardtype=''
                #     else:
                #         cardtype=cardinfo.cardtype
                # except:
                #     print(transitem.exptxserno,transitem.ttype,transitem.srvcode)
                #     cardtype=''
                #
                # try:
                #     item = Cardtype.objects.filter(company=company,flag='Y',cardtype=cardtype).last()
                #     if item.pmpoint == None:
                #         item.pmpoint = 0
                #     if item.secpoint == None:
                #         item.secpoint = 0
                #     if item.thrpoint == None:
                #         item.thrpoint = 0
                #     if transitem.s_qty == None:
                #         transitem.s_qty = 0
                # except:
                #     print(cardinfo,transitem.srvcode,transuuid.exptxserno)
                #     item.pmpoint=0
                #     item.secpoint=0
                #     item.thrpoint=0

                pmratio = 0
                secratio = 0
                thrratio = 0

                if transitem.stype=='P':
                    pmratio = 0
                    secratio = 0
                    thrratio = 0

                #     transitem.exp_basenum=0
                #     transitem.exp_secbasenum=0
                #     transitem.exp_thrbasenum=0
                #     transitem.pmpoint=item.pmpoint * transitem.s_qty
                #     transitem.secpoint= item.secpoint * transitem.s_qty
                #     transitem.thrpoint = item.thrpoint * transitem.s_qty

                if transitem.stype=='N':
                    try:
                        paycardinfo = Cardinfo.objects.filter(company=company, storecode=storecode,flag='Y', status='O').filter(
                            ccode=transuuid.ccode).last()

                        cardinfo =  Cardinfo.objects.filter(company=company, storecode=storecode,flag='Y', status='O').filter(
                            ccode=transitem.srvcode).last()

                        print(paycardinfo.cardtype,cardinfo.cardtype)

                        if paycardinfo.cardtype in SUPTYPE10LIST and cardinfo.cardtype in GOODS_CARDTYPELIST_1:
                            pmratio = 1
                            secratio = 0
                            thrratio =0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.6
                                secratio=0.4
                                thrratio=0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.6
                                secratio =0.2
                                thrratio =0.2
                        elif paycardinfo.cardtype in SUPTYPE10LIST and cardinfo.cardtype in GOODS_CARDTYPELIST_2:
                            pmratio = 1
                            secratio = 0
                            thrratio =0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.8
                                secratio=0.2
                                thrratio=0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.8
                                secratio =0.1
                                thrratio =0.1
                        else:
                            pmratio =0
                            secratio =0
                            thrratio = 0
                    except:
                        pmratio = 0
                        secratio = 0
                        thrratio = 0
                print('pmration',pmratio)
                transitem.exp_basenum=transitem.s_mount * Decimal(pmratio)
                transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                transitem.exp_thrbasenum =transitem.s_mount * Decimal(thrratio)

                # transitem.pmpoint = item.pmpoint * transitem.s_qty
                # transitem.secpoint = item.secpoint * transitem.s_qty
                # transitem.thrpoint = item.thrpoint * transitem.s_qty

                transitem.save()

    return  0
    # return HttpResponse("完成！", content_type="application/json")

# 02店产品5/5分
def set_exp_basenum_yfy_02(storecode, fromdate,todate):
    company=common.constants.COMPANYID
    storecode='02'
    transuuids = Expvstoll.objects.filter(company=company,valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate,vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    ttypes = ['S','G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company,flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)

        for transitem in transitems:
            print(transitem.create_time, transitem.exptxserno,transitem.ttype,transitem.srvcode,transitem.stype)
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''
            if transitem.s_qty==None:
                transitem.s_qty=0

            # 纹绣，手术算积点
            if transitem.ttype =='S':
                item = Serviece.objects.filter(company=company, flag='Y').filter(svrcdoe=transitem.srvcode).last()

                if item.pmpoint == None:
                    item.pmpoint = 0
                if item.secpoint == None:
                    item.secpoint = 0
                if item.thrpoint == None:
                    item.thrpoint = 0
                if transitem.s_qty == None:
                    transitem.s_qty = 0

                #     计算赠送类固定提成 按点数计算
                if transitem.stype == 'P':
                    transitem.pmperc=0
                    transitem.secperc=0
                    transitem.thprec=0
                    transitem.pmguideperc=0
                    transitem.secguideperc=0
                    transitem.thrguideperc=0
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint = item.pmpoint * transitem.s_qty
                    transitem.secpoint = item.secpoint * transitem.s_qty
                    transitem.thrpoint = item.thrpoint * transitem.s_qty

                    if len(transitem.asscode1.strip()) > 0:
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = item.secpoint * transitem.s_qty
                        transitem.thrpoint = 0
                        transitem.secperc=1
                        transitem.thprec=0
                    if len(transitem.asscode2.strip()) > 0:
                        transitem.pmpoint = item.pmpoint * transitem.s_qty
                        transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                        transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                        transitem.secperc=0.5
                        transitem.thrprec=0.5
                    transitem.save()

                # 设置实操拆分比例
                if transitem.stype == 'N':
                    transitem.pmguideperc = 1
                    transitem.secguideperc = 0
                    transitem.thrguideperc = 0

                    if len(transitem.asscode1.strip()) > 0:
                        transitem.pmguideperc = 1
                        transitem.secguideperc = 1
                        transitem.thrguideperc = 0
                    if len(transitem.asscode2.strip()) > 0:
                        transitem.pmguideperc = 1
                        transitem.secguideperc = 0.5
                        transitem.thrguideperc = 0.5

                    #
                    # 储值卡服务 纹绣类计 美疗师实操，只记顾问实耗
                    # if transuuid.cardtype in SUPTYPE10LIST:
                    #     if item.topcode =='400':
                    #         transitem.pmguideperc=1
                    #         transitem.secguideperc=1
                    #         transitem.thrguideperc=0

                    # 手术类不计美疗师实操，只记顾问实耗
                    if item.topcode =='500':
                        transitem.pmguideperc=1
                        transitem.secguideperc=0
                        transitem.thrguideperc=0

                    transitem.save()

                print(transuuid.ttype, transitem.stype, transuuid.ccode,transuuid.cardtype,item.topcode)
                # 储值卡服务
                if transuuid.cardtype in SUPTYPE10LIST:
                    # paycardinfo = Cardinfo.objects.filter(company=company, storecode=storecode, flag='Y',
                    #                                       status='O',ccode=transuuid.ccode).last()
                    print(transuuid.cardtype, item.topcode)


                    # 只有主卡卡付 纹绣、手术计算积点
                    if item.topcode in ('400','500'):
                        if transitem.stype=='N':
                            pmratio = 1
                            secratio = 0
                            thrratio = 0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.8
                                secratio = 0.2
                                thrratio = 0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.8
                                secratio = 0.1
                                thrratio = 0.1
                        else:
                            transitem.exp_basenum = 0
                            transitem.exp_secbasenum = 0
                            transitem.exp_thrbasenum = 0
                            transitem.pmpoint = item.pmpoint * transitem.s_qty
                            transitem.secpoint = item.secpoint * transitem.s_qty
                            transitem.thrpoint = item.thrpoint * transitem.s_qty

                            if len(transitem.asscode1.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = item.secpoint * transitem.s_qty
                                transitem.thrpoint = 0
                            if len(transitem.asscode2.strip()) > 0:
                                transitem.pmpoint = item.pmpoint * transitem.s_qty
                                transitem.secpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)
                                transitem.thrpoint = (item.secpoint + item.thrpoint) * transitem.s_qty * Decimal(0.5)

                        transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                        transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                        transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)
                        transitem.save()
                # except:
                else:
                    transitem.exp_basenum=0
                    transitem.exp_secbasenum=0
                    transitem.exp_thrbasenum=0
                    transitem.save()
                #         topcode not in 400 500 ,不算积点，只算提成
                # else:
                #     pmratio  = 0
                #     secratio = 0
                #     thrratio = 0
                #
                #     transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                #     transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                #     transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)
                #
                #     transitem.save()

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
                        transitem.pmpoint= pmpoint  * transitem.s_qty
                        transitem.secpoint= secpoint * transitem.s_qty
                        transitem.thrpoint = thrpoint * transitem.s_qty

                        if len(transitem.asscode1.strip())>0:
                            transitem.pmpoint = pmpoint * transitem.s_qty
                            transitem.secpoint = secpoint * transitem.s_qty
                            transitem.thrpoint = 0
                        if len(transitem.asscode2.strip())>0 :
                            transitem.pmpoint = pmpoint * transitem.s_qty
                            transitem.secpoint = ( secpoint + thrpoint ) * transitem.s_qty * Decimal(0.5)
                            transitem.thrpoint = ( secpoint + thrpoint ) * transitem.s_qty * Decimal(0.5)

                    # 非赠送类的商品销售，算顾问实耗，不算美容师实耗

                    if transitem.stype=='N':
                        transitem.pmguideperc=1
                        transitem.secguideperc=0
                        transitem.thrguideperc=0

                except:
                    transitem.exp_basenum = 0
                    transitem.exp_secbasenum = 0
                    transitem.exp_thrbasenum = 0
                    transitem.pmpoint =0
                    transitem.secpoint=0
                    transitem.thrpoint=0

                if transitem.stype=='N':
                    pmratio = 0
                    secratio =0
                    thrratio =0
                    try:
                        paycardinfo = Cardinfo.objects.filter(company=company, flag='Y', status='O').filter(
                            ccode=transuuid.ccode).last()
                        # 产品卡扣产品，不计积点
                        if transuuid.cardtype in GOODS_CARDTYPELIST:
                            pmratio=0
                            secratio=0
                            thrratio=0

                        # 储值卡扣产品，计算积点
                        if transuuid.cardtype in SUPTYPE10LIST :
                            pmratio = 1
                            secratio = 0
                            thrratio = 0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio = 0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio = 0.25

                    except:
                        pmratio =0
                        secratio =0
                        thrratio =0

                    transitem.exp_basenum = transitem.s_mount * Decimal(pmratio)
                    transitem.exp_secbasenum= transitem.s_mount * Decimal(secratio)
                    transitem.exp_thrbasenum = transitem.s_mount * Decimal(thrratio)

                transitem.save()

            # print(transitem.ttype,transitem.stype)
            # 购买产品卡、保健品卡 肝胆卡 算积点
            if transitem.ttype in ('C','I'):
                print(transitem.ttype,transitem.exptxserno,transitem.srvcode,transitem.stype)
                pmratio = 0
                secratio = 0
                thrratio = 0

                if transitem.stype=='P':
                    pmratio = 0
                    secratio = 0
                    thrratio = 0

                if transitem.stype=='N':
                    try:
                        paycardinfo = Cardinfo.objects.filter(company=company, storecode=storecode,flag='Y', status='O').filter(
                            ccode=transuuid.ccode).last()

                        cardinfo =  Cardinfo.objects.filter(company=company, storecode=storecode,flag='Y', status='O').filter(
                            ccode=transitem.srvcode).last()

                        print(paycardinfo.cardtype,cardinfo.cardtype)

                        if paycardinfo.cardtype in SUPTYPE10LIST and cardinfo.cardtype in GOODS_CARDTYPELIST_1:
                            pmratio = 1
                            secratio = 0
                            thrratio =0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.6
                                secratio=0.4
                                thrratio=0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.6
                                secratio =0.2
                                thrratio =0.2
                        elif paycardinfo.cardtype in SUPTYPE10LIST and cardinfo.cardtype in GOODS_CARDTYPELIST_2:
                            pmratio = 1
                            secratio = 0
                            thrratio =0

                            if len(transitem.asscode1.strip()) > 0:
                                pmratio = 0.8
                                secratio=0.2
                                thrratio=0

                            if len(transitem.asscode2.strip()) > 0:
                                pmratio = 0.8
                                secratio =0.1
                                thrratio =0.1
                        else:
                            pmratio =0
                            secratio =0
                            thrratio = 0
                    except:
                        pmratio = 0
                        secratio = 0
                        thrratio = 0
                print('pmration',pmratio)
                transitem.exp_basenum=transitem.s_mount * Decimal(pmratio)
                transitem.exp_secbasenum = transitem.s_mount * Decimal(secratio)
                transitem.exp_thrbasenum =transitem.s_mount * Decimal(thrratio)

                transitem.save()

    return  0
    # return HttpResponse("完成！", content_type="application/json")


def cal_emplarch_exp_amount(request):
    company = common.constants.COMPANYID
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y').filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount

                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    if transitem.ttype=='G':
                        if len(transitem.asscode1.strip()) > 0:
                            if transitem.storecode in ('01'):
                                pmratio = 0.6
                                secratio =0.4
                                thrratio =0
                            else:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            if transitem.storecode in ('01'):
                                pmratio = 0.6
                                secratio = 0.2
                                thrratio =0.2
                            else:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio = 0.25

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        if transitem.storecode in ('01','02'):
                            pmratio = 0.8
                            secratio = 0.2
                            thrratio =0
                        else:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio =0

                    if len(transitem.asscode2.strip()) > 0:
                        if transitem.storecode in ('01'):
                            pmratio = 0.8
                            secratio = 0.2
                            thrratio =0
                        else:
                            pmratio = 0.6
                            secratio = 0.2
                            thrratio =0.2

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)
                    # transitem.thprec=item.thrperc
                    # transitem.pmguideperc=item.pmguideperc
                    # transitem.secguideperc=item.secguideperc
                transitem.save()
    # return  0
    return HttpResponse("完成！", content_type="application/json")


def set_exp_xamount_yfy_01(fromdate,todate):
    company = common.constants.COMPANYID
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    storecode='01'
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y').filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate,storecode=storecode).order_by('storecode','vsdate','vstime')
    goods_cardtypelist=['201','202','203','204']
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y',storecode=storecode).filter(exptxserno=transuuid.exptxserno)
        pcodes = Toll.objects.filter(company=company,storecode=storecode).filter(exptxserno=transuuid.exptxserno)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            # print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            # print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode,transuuid.uuid,transuuid.exptxserno, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount
                    # 单次项目付现金 全部是顾问的业绩
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype=='':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 1.0
                            secratio =0.0
                            thrratio =0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 1.0
                            secratio = 0.0
                            thrratio =0.0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype == 'G':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.6
                            secratio = 0.4
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.6
                            secratio = 0.2
                            thrratio = 0.2

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                transitem.transitem_cardtype()
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    # print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.6
                                secratio = 0.4
                                thrratio =0
                            else:
                                pmratio = 0.8
                                secratio = 0.2
                                thrratio =0
                        except:
                            pmratio = 0.8
                            secratio = 0.2
                            thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.filter(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.6
                                secratio = 0.2
                                thrratio =0.2
                            else:
                                pmratio = 0.8
                                secratio = 0.1
                                thrratio =0.1
                        except:
                            pmratio = 0.8
                            secratio = 0.1
                            thrratio =0.1

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)

                    cardtype = Cardinfo.objects.filter(company=company,status='O',storecode='01',)


                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")


def set_exp_xamount_yfy_02(fromdate,todate):
    company = common.constants.COMPANYID
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    storecode='02'
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    goods_cardtypelist=['201','202','203','204']
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount
                    # 单次项目付现金 全部是顾问的业绩
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype=='S':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 1
                            secratio =0
                            thrratio =0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 1.0
                            secratio = 0.0
                            thrratio =0.0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype == 'G':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25
                    print(pmratio,secratio,thrratio)
                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                transitem.transitem_cardtype()
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                            else:
                                pmratio = 0.8
                                secratio = 0.2
                                thrratio =0
                        except:
                            pmratio = 0.8
                            secratio = 0.2
                            thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                            else:
                                pmratio = 0.8
                                secratio = 0.1
                                thrratio =0.1
                        except:
                            pmratio = 0.8
                            secratio = 0.1
                            thrratio = 0.1
                        # pmratio = 0.8
                        # secratio = 0.2
                        # thrratio =0

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)

                    cardtype = Cardinfo.objects.filter(company=company,status='O',storecode='01',)


                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")


def set_exp_xamount_yfy_03(fromdate,todate):
    company = common.constants.COMPANYID
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    storecode='03'
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    goods_cardtypelist=['201','202','203','204']
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount
                    # 单次项目付现金 全部是顾问的业绩
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype=='':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio =0.5
                            thrratio =0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 1.0
                            secratio = 0.0
                            thrratio =0.0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype == 'G':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                transitem.transitem_cardtype()
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                            else:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                        except:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                            else:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                        except:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25
                        # pmratio = 0.8
                        # secratio = 0.2
                        # thrratio =0

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)

                    cardtype = Cardinfo.objects.filter(company=company,status='O',storecode='01',)


                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")


def set_exp_xamount_yfy_04(fromdate,todate):
    company = common.constants.COMPANYID
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    storecode='04'
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    goods_cardtypelist=['201','202','203','204']
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount
                    # 单次项目付现金 全部是顾问的业绩
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype=='':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio =0.5
                            thrratio =0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 1.0
                            secratio = 0.0
                            thrratio =0.0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype == 'G':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                transitem.transitem_cardtype()
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                            else:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                        except:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                            else:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                        except:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25
                        # pmratio = 0.8
                        # secratio = 0.2
                        # thrratio =0

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)

                    cardtype = Cardinfo.objects.filter(company=company,status='O',storecode='01',)


                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")

def set_exp_xamount_yfy_05(fromdate,todate):
    company = common.constants.COMPANYID
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']
    storecode='05'
    transuuids = Expvstoll.objects.filter(company=company, valiflag='Y',storecode=storecode).filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate).order_by('storecode','vsdate','vstime')
    goods_cardtypelist=['201','202','203','204']
    # ttypes = ['S', 'G']
    for transuuid in transuuids:
        transitems = Expense.objects.filter(company=company, flag='Y').filter(transuuid=transuuid)
        pcodes = Toll.objects.filter(company=company).filter(transuuid=transuuid)
        cashamount = 0
        totalamount = 0
        for pcode in pcodes:
            print('pcode=',pcode.pcode)
            if pcode.totmount==None:
                pcode.totmount=0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=company, flag='Y', pcode=pcode.pcode)
            print(p,p.iscash)
            if p.iscash==None:
                p.iscash='3'
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
        if totalamount ==0 :
            cashratio=0
        else:
            cashratio = cashamount / totalamount

        print(transuuid.storecode, transuuid.vsdate,transuuid.exptxserno,totalamount,cashamount,cashratio)

        for transitem in transitems:
            if transitem.s_mount==None:
                transitem.s_mount=0
            if transitem.pmcode == None:
                transitem.pmcode = ''
            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''

            if transitem.ttype in ( 'S','G'):
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    # transitem.exp_basenum = transitem.s_mount
                    # 单次项目付现金 全部是顾问的业绩
                    pmratio = 1
                    secratio = 0
                    thrratio = 0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype=='':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio =0.5
                            thrratio =0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 1.0
                            secratio = 0.0
                            thrratio =0.0

                    # 单次产品付现金，根据输入人数而定 6/4 或6/22
                    if transitem.ttype == 'G':
                        if len(transitem.asscode1.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                        if len(transitem.asscode2.strip()) > 0:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)

                transitem.save()

            if transitem.ttype in ('C','I'):
                transitem.transitem_cardtype()
                if transitem.stype == 'P':
                    # transitem.exp_basenum = 0
                    # transitem.exp_secbasenum = 0
                    transitem.pmamount = 0
                    transitem.secamount = 0
                    transitem.thramount = 0

                if transitem.stype == 'N':
                    pmratio = 1
                    secratio =0
                    thrratio =0
                    print('transitem:',transitem.asscode1,transitem.asscode1.strip(),len(transitem.asscode1.strip()))
                    if len(transitem.asscode1.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                            else:
                                pmratio = 0.5
                                secratio = 0.5
                                thrratio =0
                        except:
                            pmratio = 0.5
                            secratio = 0.5
                            thrratio = 0

                    if len(transitem.asscode2.strip()) > 0:
                        try:
                            cardinfo = Cardinfo.objects.get(company=common.constants.COMPANYID,storecode=storecode,ccode=transitem.srvcode)
                            if cardinfo.cardtype in GOODS_CARDTYPELIST:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                            else:
                                pmratio = 0.5
                                secratio = 0.25
                                thrratio =0.25
                        except:
                            pmratio = 0.5
                            secratio = 0.25
                            thrratio = 0.25
                        # pmratio = 0.8
                        # secratio = 0.2
                        # thrratio =0

                    transitem.pmamount = transitem.s_mount * Decimal(cashratio) * Decimal(pmratio)
                    transitem.secamount = transitem.s_mount * Decimal(cashratio) * Decimal(secratio)
                    transitem.thramount = transitem.s_mount * Decimal(cashratio) * Decimal(thrratio)
                    print('transitem:',transitem.asscode1,'cashratio:',cashratio,' secratio=',secratio)

                    cardtype = Cardinfo.objects.filter(company=company,status='O',storecode='01',)


                transitem.save()
    return  0
    # return HttpResponse("完成！", content_type="application/json")

def cal_emplarch_02(fromdate, todate):

    return 0

