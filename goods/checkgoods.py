from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from decimal import *

from cashier.models import Expvstoll,Expense,Toll,EmplArchivementDetail
from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode
from adviser.models import Cardinfo
from goods.models import Salehead,Saledtl,Transhead,Transdtl,Goodstranslog

import common.constants

# 处理salehead 已经确认，但是goodstranslog未记录
def checksalehead_not_in_goodstranslog(request):
    saleheads=Salehead.objects.filter(company=common.constants.COMPANYID,flag='Y',status='20',storecode='00')
    for salehead in saleheads:
        print('check',salehead.doccode, salehead.vdate)
        goodstranslogs = Goodstranslog.objects.filter(doccode=saleheads.doccode)
        saledtls = Saledtl.objects.filter(company=common.constants.COMPANYID,saleheadid_id=salehead.uuid)

        if goodstranslogs.count()== saledtls.count():
            print('skip',salehead.doccode)

        if goodstranslogs.count() != saledtls.count():
            company=salehead.company
            sukid=salehead.sukid
            doccode=salehead.doccode
            saleatr=salehead.saleatr
            vdate=salehead.vdate
            storecode=salehead.storecode
            whcode=salehead.inwhcode
            supplierid=salehead.supplierid
            gnote=salehead.gnote
            tmount=salehead.tmount

            for saledtl in saledtls:
                seqbar = saledtl.seqbar
                gcode=saledtl.gcode
                goodsvaldate=saledtl.goodsvaldate
                qty =saledtl.qty
                price=saledtl.price
                disc=saledtl.disc
                amount=saledtl.mount

                try:
                    goodstranslog=Goodstranslog.objects.get(company=company,doccode=doccode,seqbar=seqbar)
                    print('skipped', doccode, seqbar, gcode)
                except:
                    print('create',doccode,seqbar,gcode)
                    goodstranslog=Goodstranslog.objects.create(
                        company=company,
                        storecode=storecode,
                        sukid=sukid,doccode=doccode,saleatr=saleatr,vdate=vdate,whcode=whcode,
                        gcode=gcode,goodsvaldate=goodsvaldate,qty1=qty,price1=price,amount1=amount
                    )
                    goodstranslog.save()
                    goodstranslog.set_qty2()
                    goodstranslog.set_qty3()


    return HttpResponse("完成！", content_type="application/json")



# 从goodstranslog中解析数据返回生成salehead，saledtl,transhead,transdtl
def reseverlog(request):
    SALEATRLIST= ['I','F','U','AD']
    fromdate=request.GET['fromdate']
    todate=request.GET['todate']
    company=common.constants.COMPANYID
    goodstranslog_sukids = list(Goodstranslog.objects.filter(company=company,saleatr__in=SALEATRLIST,vdate__gte=fromdate,vdate__lte=todate).values('storecode','whcode','saleatr','vdate','ecode','sukid','doccode').distinct())
    # print(goodstranslog_sukids)
    item=0
    for log_sukid in goodstranslog_sukids:
        sukid=log_sukid['sukid']
        storecode=log_sukid['storecode']
        whcode=log_sukid['whcode']
        doccode=log_sukid['doccode']
        vdate=log_sukid['vdate']
        ecode=log_sukid['ecode']
        saleatr=log_sukid['saleatr']

        if saleatr in SALEATRLIST:
            try:
                salehead =Salehead.objects.get(company=company,storecode=storecode,sukid=sukid,instorecode=storecode,inwhcode=whcode,doccode=doccode,vdate=vdate)
                salehead.saleatr=saleatr
                salehead.status = '20'
                salehead.vdate=vdate
                salehead.creater='sys_fill'
                salehead.save()
            except:
                salehead=Salehead.objects.create(company=company,instorecode=storecode,inwhcode=whcode,saleatr=saleatr,vdate=vdate,sukid=sukid,doccode=doccode,ecode=ecode,status='20',creater='sys_fill')


            log_items = Goodstranslog.objects.filter(company=company, sukid=sukid)
            # saledtl_cnt = Saledtl.objects.filter(company=company,sukid=sukid.sukid).count()
            for log_item in log_items:
                print('begin:',log_item.gcode,log_item.qty1)
                try:
                    saledtl_item = Saledtl.objects.get(
                        company=company,storecode=storecode,sukid=log_item.sukid,saleheadid=salehead,seqbar=log_item.seqbar)
                    print('Get:',log_item.gcode,log_item.goodsvaldate,log_item.qty1)
                except:
                    # saledtl_item = Saledtl.objects.create(
                    #     company=company,storecode=log_item.storecode,sukid=log_item.sukid,saleheadid=salehead,
                    #     seqbar=log_item.seqbar,gcode=log_item.gcode,goodsvaldate=log_item.goodsvaldate,
                    #     price=log_item.price1,qty=log_item.qty1,disc=1,mount=log_item.amount1,gdnote=log_item.goodsnote,creater='sys_fill'
                    # )
                    print('Create:', log_item.gcode, log_item.goodsvaldate, log_item.qty1)

    return HttpResponse("完成！", content_type="application/json")