#coding = utf-8
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render
from datetime import datetime,timedelta
import json
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from django.db.models import Sum
from decimal import *
import requests

from .models import Expvstoll,Expense,Toll,Cardhistory,EmplArchivementDetail,VipItemInfo,VipItemTransHead,VipItemTransDetail,VipItemTranslog
from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode,Vip,Cardsupertype
from adviser.models import Cardinfo,ExpvstollHung,ExpenseHung

from common.models import Sequence

from .emplarch_yfy import EMPL_ARCHEMENT_BYMONTH_YFY
from .emplarch_yfy import set_exp_basenum_yfy_01,set_exp_xamount_yfy_01,set_exp_basenum_yfy_55,set_exp_xamount_yfy_02,set_exp_xamount_yfy_03,set_exp_xamount_yfy_04,set_exp_xamount_yfy_05

from adviser.views import (
    sql_to_json,
    _parse_uuid_loose,
    _parse_request_param_json,
    _hung_line_ttypename,
    _resolve_paycard_plan_info,
)
import common.constants
from .emplarch_yiren import cal_emplarchivement_yiren,process_pertrans_yiren,EmplArchivement
from .emplarch_yfy import process_pertrans_yfy

from common.views import getserno
from common.views import _resolve_hung_itemname

# 选品接口重导出（保持 cashier URL 不变）
from adviser.views import service_items, goods_items, cardtype_items

# Create your views here.

from collections import defaultdict
import traceback
from django.db.models import Q, Min, Max, Sum

def get_emplarch_bymonth(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    month = request.GET['month']
    ecode = request.GET['ecode']

    delta = timedelta(days=-90)
    print(delta)
    now = datetime.now()

    fromdate = datetime.strftime((now + delta),'%Y%m%d')
    todate = datetime.strftime( datetime.now()  ,'%Y%m%d')
    print('fromdate:',fromdate,'todate:',todate)

    # if request.method == 'GET':
    if company=='yfy':
        sql = EMPL_ARCHEMENT_BYMONTH_YFY
    else:
        sql =  EMPL_ARCHEMENT_BYMONTH_YFY
    params = (company + ' ' + storecode + ' ' + month + ' ' + ecode + '  '+company + ' ' + storecode + ' ' + month +  ' ' + ecode +'  '+ company + ' ' + storecode + ' ' + month +  ' ' + ecode  ).split()
    print(sql, params)
    json_data = sql_to_json(sql, params)
    return HttpResponse(json_data, content_type="application/json")

def cal_emplarchivement(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storecode=request.GET['storecode']
    except:
        storecode='01'

    try:
        fromdate=request.GET['fromdate']
    except:
        fromdate='20191001'

    try:
        todate = request.GET['todate']
    except:
        todate ='20991231'

    if company=='yiren':
        cal_emplarchivement_yiren(company, storecode,fromdate,todate)

    if company=='yfy':
        if storecode == '01':
            set_exp_basenum_yfy_01(storecode, fromdate, todate)
            set_exp_xamount_yfy_01(fromdate, todate)

        if storecode == '02':
            print(storecode, fromdate, todate)
            set_exp_basenum_yfy_55(storecode, fromdate, todate)
            set_exp_xamount_yfy_02(fromdate, todate)

        if storecode == '03':
            set_exp_basenum_yfy_55(storecode, fromdate, todate)
            set_exp_xamount_yfy_03(fromdate, todate)

        if storecode == '04':
            set_exp_basenum_yfy_55(storecode, fromdate, todate)
            set_exp_xamount_yfy_04(fromdate, todate)

        if storecode == '05':
            set_exp_basenum_yfy_55(storecode, fromdate, todate)
            set_exp_xamount_yfy_05(fromdate, todate)

    return HttpResponse('OK', content_type="application/json")

def process_pertrans(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storecode=request.GET['storecode']
    except:
        storecode='01'

    try:
        txserno = request.GET['txserno']
    except:
        txserno=''

    try:
        transuuid = request.GET['transuuid']
    except:
        transuuid=''

    if transuuid.__len__() >0:
        trans = Expvstoll.objects.get(company=company,storecode=storecode,uuid=transuuid)

        trans.last_modified = datetime.now()
        trans.save()

        # set cashration cardratio sendratio
        trans.set_paymoderatio()

        transitems = Expense.objects.filter(transuuid=trans)
        print('len(transitems)', len(transitems))
        for transitem in transitems:
            print('transitm', transitem.exptxserno,transitem.ditem,transitem.srvcode)
            # 设置商品邮寄单信息   vipiteminfo, vipitemtranslog
            if transitem.ttype =='G':
                transitem.set_deposite()


    if company == 'yiren' :
        process_pertrans_yiren(company, storecode, txserno, transuuid)

    if company == 'yfy':
        print('process_pertrans_yfy')
        process_pertrans_yfy(company, storecode, txserno, transuuid)

    return HttpResponse('OK', content_type="application/json")

class hung_to_trans(object):
    def __init__(self,**kwargs):
        self.company=kwargs.get('company','demo')
        self.storecode = kwargs.get('storecode','88')
        self.hungserno = kwargs.get('hungserno','')
        self.paydetails = kwargs.get('paydetails','')
        self.hunguuid = kwargs.get('hunguuid','')
        self.cashier = kwargs.get('cashier','admin')

        self.transcards = []
        self.tolls = []

        now = datetime.now()
        self.vsdate=now.date().__format__('%Y%m%d')
        self.vstime = now.time().__format__('%H%M%S')

        if len(self.hunguuid) >0:
            self.expvstollhung = ExpvstollHung.objects.get(company=self.company,storecode=self.storecode,flag='Y',valiflag_hung='Y',uuid = self.hunguuid)
            self.hung = self.expvstollhung
            self.expensehung = ExpenseHung.objects.filter(company=self.company, storecode=self.storecode, flag='Y', hunguuid=self.expvstollhung.uuid)

            self.vip = self.expvstollhung.vipuuid
            self.viptype = self.vip.viptype
            self.totalamount =0
            self.totalqty = 0

            if self.expvstollhung.ccode_hung == None:
                self.expvstollhung.ccode_hung=''
            if len(self.expvstollhung.ccode_hung) > 0 :
                try:
                    self.paycardinfo = Cardinfo.objects.get(company=self.company,ccode=self.expvstollhung.ccode_hung)
                    # self.paycardinfo = vipcardlist.objects.get(ccode=self.expvstollhung.ccode_hung)
                    self.payccode = self.expvstollhung.ccode_hung
                    self.comptype = self.paycardinfo.cardtypeuuid.comptype


                    self.cardsupertype = Cardsupertype.objects.get(flag='Y',company=self.company,code=self.paycardinfo.cardtypeuuid.suptype)

                    self.cardpcode = self.cardsupertype.pcode
                    if self.paycardinfo.cardtypeuuid.stype =='N':
                        self.cardpcode = self.cardsupertype.normal_pcode
                    if self.paycardinfo.cardtypeuuid.stype =='P':
                        self.cardpcode = self.cardsupertype.present_pcode
                    self.paycardflag='Y'
                except:
                    self.payccode = self.expvstollhung.ccode_hung
                    self.paycardflag='N'
            else:
                self.paycardflag='N'
                self.payccode=''

    def check_cardinfo(self):
        if self.paycardinfo.stats == 'C':
            print('此卡已经作废，无法结帐')
            return 'C'
        if self.paycardinfo.status == 'P':
            print('未结帐卡，请先完成疗程卡购买')
            return 'P'

    def set_exptxserno(self):
        serno = getserno(self.company, self.storecode, 'EXPVSTOLL')
        self.exptxserno = serno
        self.expvstoll.exptxserno = serno
        self.expvstoll.save(update_fields=['exptxserno'])
        Expense.objects.filter(
            company=self.company, transuuid=self.expvstoll,
        ).update(exptxserno=serno)
        Toll.objects.filter(
            company=self.company, transuuid=self.expvstoll,
        ).update(exptxserno=serno)

        try:
            self.expvstoll.cardleftmoney = self.paycardinfo.leftmoney
        except:
            self.expvstoll.cardleftmoney = 0

        self.expvstoll.creater = self.cashier
        self.expvstoll.save(0)

        for item in self.expenses:
            item.exptxserno = self.exptxserno
            item.creater = self.cashier
            item.save()

        for item in self.tolls:
            item.exptxserno = self.exptxserno
            item.creater = self.cashier
            item.currency = 'RMB'
            item.custperc = 1
            item.save()

        self.expvstoll.set_paymoderatio()
        self.expvstoll.set_cardhistory()
        if self.expvstoll.ttype == 'G':
            self.expvstoll.set_transgoodstranslog()
            self.expvstoll.set_vipiteminfo()

        try:
            self.paycardinfo.save()
        except:
            print("no pcaycardinfo")

        for card in self.transcards:
            print('card status',card.status)
            card.create = self.cashier
            card.save()


    def hungtoexpvstoll(self):
        print('hungtoexpvstoll',self.company,self.storecode,self.hung.exptxserno_hung,self)
        if len(self.hung.exptxserno_hung)>0:
            self.expvstoll = Expvstoll.objects.get_or_create(flag='Y',company=self.company,storecode=self.storecode,hungserno=self.hung.exptxserno_hung)[0]
            # self.exptxserno = getserno(self.company, self.storecode,'EXPVSTOLL')
            # print('self.exptxsenro',self.exptxserno)
            # self.expvstoll.exptxserno = self.exptxserno
            self.expvstoll.vsdate =self.vsdate
            self.expvstoll.vstime =self.vstime
            self.expvstoll.valiflag='Y'
            self.expvstoll.vcode= self.hung.vcode_hung
            self.expvstoll.ccode= self.hung.ccode_hung
            self.expvstoll.vipuuid = self.hung.vipuuid
            if self.hung.sumdisc_hung == None:
                self.expvstoll.sumdisc = 1
            else:
                self.expvstoll.sumdisc = self.hung.sumdisc_hung

            if self.hung.mondisc_hung == None:
                self.expvstoll.mondisc =0
            else:
                self.expvstoll.mondisc = self.hung.mondisc_hung
            self.expvstoll.totmount = self.hung.totmount_hung
            self.expvstoll.cardtype = self.hung.cardtype_hung
            if self.expvstoll.ccode and not self.expvstoll.cardtype:
                try:
                    _ci = Cardinfo.objects.filter(company=self.company, ccode=self.expvstoll.ccode).select_related('cardtypeuuid').first()
                    if _ci and _ci.cardtypeuuid:
                        self.expvstoll.cardtype = _ci.cardtypeuuid.cardtype
                except:
                    pass
            self.expvstoll.hungserno = self.hung.exptxserno_hung
            self.expvstoll.ttype = self.hung.ttype_hung
            self.expvstoll.normalflag ='Y'
            self.expvstoll.bookingeventid = self.hung.bookingeventid
            self.expvstoll.terminalid = self.hung.terminalid
            self.expvstoll.save()

            self.tx_qty = 0
            self.tx_amount = 0
            hungitems = ExpenseHung.objects.filter(flag='Y',company=self.company,storecode=self.storecode,exptxserno_hung=self.hung.exptxserno_hung)
            item =0
            self.expenses=[]
            self.transcards=[]
            for hungitem in hungitems:
                item =item +1
                ditem ='000'+item.__str__()
                expense = Expense.objects.get_or_create(flag='Y',company=self.company,storecode=self.storecode,transuuid=self.expvstoll,ditem=hungitem.ditem_hung)[0]
                # expense.exptxserno = self.exptxserno
                expense.ttype = hungitem.ttype_hung
                expense.ditem = ditem
                expense.srvcode = hungitem.srvcode_hung
                expense.s_qty = hungitem.s_qty_hung
                expense.s_price = hungitem.s_price_hung
                expense.secdisc = hungitem.secdisc_hung
                expense.s_mount = hungitem.s_mount_hung
                expense.addvamoney = hungitem.addvamoney_hung
                expense.srvactmount = hungitem.srvactmount_hung
                expense.srvmondisc = hungitem.srvmondisc_hung
                expense.pmcode = hungitem.pmcode_hung
                expense.asscode1 = hungitem.asscode1_hung
                expense.asscode2 = hungitem.asscode2_hung
                expense.stype = hungitem.stype_hung
                expense.newcardtype = hungitem.newcardtype_hung
                expense.depositeflag = hungitem.depositeflag
                expense.owegoodsflag = hungitem.owegoodsflag
                expense.hunguuid = hungitem.uuid

                print('expense.ditem',expense.ditem, hungitem.ttype_hung,hungitem.srvcode_hung)

                if hungitem.ttype_hung == 'C':
                    # transcard = self.newcards.get(ccode=hungitem.srvcode_hung)
                    transcard = Cardinfo.objects.filter(flag='Y', company=self.company,
                                                            vipuuid=self.vip,ccode=hungitem.srvcode_hung).first()
                    if transcard:
                        transcard.status='O'
                        self.transcards.append(transcard)
                        transcard.save()
                        print('transcard.status',transcard.status)

                if hungitem.ttype_hung =='I':
                    print('Processing item:', hungitem.srvcode_hung,hungitem.ttype_hung,self.vip.uuid,self.vip.vcode)
                    transcard = Cardinfo.objects.filter(flag='Y', company=self.company,
                                                            vipuuid=self.vip,ccode=hungitem.srvcode_hung)[0]

                    print('transcard',transcard.ccode, transcard.cardtypeuuid.comptype, transcard.leftqty, transcard.leftmoney,hungitem.addvamoney_hung)
                    if transcard.cardtypeuuid.comptype =='times':
                        transcard.leftqty = transcard.leftqty + hungitem.s_qty_hung
                        

                    transcard.leftmoney= transcard.leftmoney + hungitem.addvamoney_hung
                    print('transcard.leftmoney',transcard.leftmoney)
                    self.transcards.append(transcard)
                    transcard.save()
                    print('transcard.leftmoney',transcard.leftmoney)

                self.tx_qty = self.tx_qty + hungitem.s_qty_hung
                self.tx_amount = self.tx_amount + hungitem.s_mount_hung

                self.expenses.append(expense)


                expense.save()

            # self.set_toll()

        if self.expvstoll.ttype == 'G':
            self.expvstoll.set_transgoodstranslog()
            self.expvstoll.set_vipiteminfo()

    def set_toll(self):
        print('set_toll')
        self.tolls =[]
        if len(self.expvstollhung.ccode_hung) > 0:
            try:
                self.paycardinfo = Cardinfo.objects.get(company=self.company, ccode=self.expvstollhung.ccode_hung)
                self.payccode = self.expvstollhung.ccode_hung
                self.comptype = self.paycardinfo.cardtypeuuid.comptype

                if self.paycardinfo.status == 'C':
                    print('此卡已经作废，无法结帐')
                    return -1
                if self.paycardinfo.status == 'P':
                    print('未结帐卡，请先完成疗程卡购买')
                    return -1

                self.cardsupertype = Cardsupertype.objects.get(flag='Y', company=self.company,
                                                               code=self.paycardinfo.cardtypeuuid.suptype)
                self.cardpcode = self.cardsupertype.pcode
                if self.paycardinfo.stype == 'N':
                    self.cardpcode = self.cardsupertype.normal_pcode
                if self.paycardinfo.stype == 'N':
                    self.cardpcode = self.cardsupertype.present_pcode
                self.paycardflag = 'Y'
                print('self.paycarflag')

                if self.paycardinfo.cardtypeuuid.comptype =='amount':
                    if self.paycardinfo.leftmoney >= self.tx_amount:
                        print('all cardpay')
                        toll = Toll.objects.get_or_create(flag='Y',company=self.company,storecode=self.storecode, transuuid = self.expvstoll,pcode=self.cardpcode)[0]

                        # toll.pcode=self.cardpcode
                        toll.expvssvern = '1'
                        toll.qty = self.tx_qty
                        toll.totmount = self.tx_amount
                        print(2)
                        # toll.exptxserno = self.expvstoll.exptxserno
                        toll.transuuid = self.expvstoll
                        toll.currency='RMB'
                        toll.custperc=1
                        print(3)
                        self.tolls.append(toll)
                        print(4)
                        # toll.save()

                        self.paycardinfo.leftmoney = self.paycardinfo.leftmoney - self.tx_amount
                        # self.paycardinfo.save()

                        self.expvstoll.cardleftmoney = self.paycardinfo.leftmoney
                        # self.expvstoll.save()
                    else:
                    # if self.paycardinfo.leftmoney < self.tx_amount:
                        print('part cardpay')
                        toll = Toll.objects.get_or_create(flag='Y', company=self.company, storecode=self.storecode,
                                                          transuuid=self.expvstoll,pcode=self.cardpcode)[0]
                        # toll.pcode = self.cardpcode
                        toll.expvssvern = '2'
                        toll.qty = 1
                        toll.totmount = self.paycardinfo.leftmoney
                        # toll.exptxserno = self.expvstoll.exptxserno
                        toll.transuuid = self.expvstoll
                        toll.currency = 'RMB'
                        toll.custperc = 1
                        self.tolls.append(toll)
                        # toll.save()

                        # default_sec_pcode  = common.constants.DEFAULT_NORMAL_PCODE
                        toll = Toll.objects.get_or_create(flag='Y', company=self.company, storecode=self.storecode,
                                                          transuuid=self.expvstoll, pcode=common.constants.DEFAULT_NORMAL_PCODE)[0]
                        # toll.pcode = self.cardpcode
                        toll.expvssvern = '2'
                        toll.qty = 1
                        toll.totmount = self.tx_amount - self.paycardinfo.leftmoney
                        # toll.exptxserno = self.expvstoll.exptxserno
                        toll.transuuid = self.expvstoll
                        toll.currency = 'RMB'
                        toll.custperc = 1
                        self.tolls.append(toll)
                        # toll.save()

                        self.paycardinfo.leftmoney  = 0
                        # self.paycardinfo.save()

                        self.expvstoll.cardleftmoney = self.paycardinfo.leftmoney
                        # self.expvstoll.save()

                if self.paycardinfo.cardtypeuuid.comptype == 'times':
                    if self.paycardinfo.leftqty >= self.tx_qty:
                        print('all cardpay')
                        toll = Toll.objects.get_or_create(flag='Y', company=self.company, storecode=self.storecode,
                                                          transuuid=self.expvstoll, pcode=self.cardpcode)[0]
                        # toll.pcode=self.cardpcode
                        toll.expvssvern = '1'
                        toll.qty = self.tx_qty
                        toll.totmount = self.tx_amount
                        # toll.exptxserno = self.expvstoll.exptxserno
                        toll.transuuid = self.expvstoll
                        toll.currency = 'RMB'
                        toll.custperc = 1
                        self.tolls.append(toll)
                        # toll.save()
                        self.paycardinfo.leftqty = self.paycardinfo.leftqty - self.tx_qty
                        self.paycardinfo.leftmoney = self.paycardinfo.leftmoney - self.tx_amount
                        # self.paycardinfo.save()

                        self.expvstoll.cardleftmoney = self.paycardinfo.leftmoney
                        # self.expvstoll.save()

                    else:
                        # self.paycardinfo.leftqty < self.tx_qty:
                        print('error')



            except:
                self.payccode = self.expvstollhung.ccode_hung
                self.paycardflag = 'N'
                print('no cardpay')
                toll = Toll.objects.get_or_create(flag='Y', company=self.company, storecode=self.storecode,
                                                  transuuid=self.expvstoll,
                                                  pcode=common.constants.DEFAULT_NORMAL_PCODE)[0]
                # toll.pcode = self.cardpcode
                toll.expvssvern = '1'
                toll.qty = 1
                toll.totmount = self.tx_amount
                # toll.exptxserno = self.expvstoll.exptxserno
                toll.transuuid = self.expvstoll
                toll.currency = 'RMB'
                toll.custperc = 1

                self.tolls.append(toll)
                # toll.save()
        else:
            self.paycardflag = 'N'
            self.payccode = ''
            print('no cardpay')
            toll = Toll.objects.get_or_create(flag='Y', company=self.company, storecode=self.storecode,
                                              transuuid=self.expvstoll,
                                              pcode=common.constants.DEFAULT_NORMAL_PCODE)[0]
            # toll.pcode = self.cardpcode
            toll.expvssvern = '1'
            toll.qty = 1
            toll.totmount = self.tx_amount
            # toll.exptxserno = self.expvstoll.exptxserno
            toll.transuuid = self.expvstoll
            toll.currency = 'RMB'
            toll.custperc = 1
            self.tolls.append(toll)
            # toll.save()

        return 0

    @transaction.atomic
    def settrans(self):
        payccode = self.expvstollhung.ccode_hung
        _cardtype = self.expvstollhung.cardtype_hung
        if payccode and not _cardtype:
            try:
                _ci = Cardinfo.objects.filter(company=self.company, ccode=payccode).select_related('cardtypeuuid').first()
                if _ci and _ci.cardtypeuuid:
                    _cardtype = _ci.cardtypeuuid.cardtype
            except:
                pass

        self.expvstoll = Expvstoll.objects.get_or_create(company=self.expvstollhung.company,storecode=self.expvstollhung.storecode,
                                               vcode=self.expvstollhung.vcode_hung,ccode=self.expvstollhung.ccode_hung,cardtype=_cardtype,vipuuid=self.expvstollhung.vipuuid,
                                               hungserno=self.expvstollhung.exptxserno_hung,bookingeventid=self.expvstollhung.bookingeventid,promotionsid=self.expvstollhung.promotionsid,
                                               ttype=self.expvstollhung.ttype_hung,sumdisc=self.expvstollhung.sumdisc_hung,mondisc=self.expvstollhung.sumdisc_hung)[0]
        self.expvstoll.vsdate = self.vsdate
        self.expvstoll.vstime = self.vstime
        self.expvstoll.valiflag='Y'
        self.expvstoll.exptxserno =getserno(self.company,self.expvstollhung.storecode,'EXPVSTOLL')

        self.expvstoll.save()

        self.items = ExpenseHung.objects.filter(company=self.company,exptxserno_hung=self.expvstollhung.exptxserno_hung)
        for item in self.items:
            expense = Expense.objects.get_or_create(company=self.company,storecode=item.storecode,hungserno=item.exptxserno_hung,ditem=item.ditem_hung)[0]
            expense.ttype= item.ttype_hung
            expense.stype =item.stype_hung
            expense.srvcode = item.srvcode_hung
            expense.s_qty = item.s_qty_hung
            expense.s_price = item.s_price_hung
            expense.s_mount = item.s_mount_hung
            expense.pmcode = item.pmcode_hung
            expense.asscode1 = item.asscode1_hung
            expense.asscode2 = item.asscode2_hung
            expense.oldcustflag = item.oldcustflag_hung
            expense.secoldcustflag =item.secoldcustflag_hung
            expense.throldcustflag = item.throldcustflag_hung
            expense.owegoodsflag = item.owegoodsflag
            expense.oldcardtype = item.oldcardtype_hung
            expense.newcardtype = item.newcardtype_hung
            expense.goodsvaldate = item.goodsvaldate
            expense.exptxserno = self.expvstoll.exptxserno

            self.totalamount = self.totalamount + expense.s_mount
            self.totalqty = self.totalqty + expense.s_qty


            # expense.hunguuid = str(expvstoll.uuid)
            expense.save()


        self.set_toll()

        if self.expvstollhung.ttype_hung in ('S','G'):
            self.sg_trans()

        if self.expvstollhung.ttype_hung == 'C':
            print('c')

         # return '0'

    def c_tran(self):
        if self.hung.ttype_hung =='C':
            self.hungtoexpvstoll()
            self.set_toll()
            self.set_exptxserno()
            # for card in self.newcards:
            #     print('card status',card.status)
            #     card.save()

            self.hung.psstatus_hung='70'
            self.hung.save()

    def i_tran(self):
        if self.hung.ttype_hung == 'I':
            print('I')
            self.hungtoexpvstoll()
            self.set_toll()
            self.set_exptxserno()
            # for card in self.newcards:
            #     print('card status',card.status)
            #     card.save()

            self.hung.psstatus_hung='70'
            self.hung.save()

    def sg_tran(self):
        print('SG')
        if self.hung.ttype_hung in ('S','G'):
            print('I')
            self.hungtoexpvstoll()
            self.set_toll()
            self.set_exptxserno()
            self.hung.psstatus_hung = '70'
            self.hung.save()

            # if self.hung.ttype_hung =='G':
            #     self.expvstoll.set_transgoodstranslog()
            #     self.expvstoll.set_deposite()

    def hunguuid_trans(self):
        if self.hung.ttype_hung == 'C':
            self.c_tran()

        if self.hung.ttype_hung == 'I':
            self.i_tran()

        if self.hung.ttype_hung == 'S':
            self.sg_tran()

        if self.hung.ttype_hung == 'G':
            self.sg_tran()

        self.set_exptxserno()

class pre_trans_byvip(object):
    def __init__(self,**kwargs):
        self.company=kwargs.get('company','demo')
        self.storecode=kwargs.get('storecode','88')
        self.cashier = kwargs.get('cashier','admin')
        self.vipuuid = kwargs.get('vipuuid','')

        self.vip = Vip.objects.get(flag='Y',company=self.company,uuid=self.vipuuid)
        psstatuslist = ['10', '20', '30', '40', '50', '60']
        self.hungs = ExpvstollHung.objects.filter(flag='Y',company=self.company,storecode=self.storecode,valiflag_hung='Y',psstatus_hung__in=psstatuslist,vipuuid=self.vip).order_by('ccode_hung')
        self.willpayamount = 0

    def c_trans_checkout(self):
        c_hungs = self.hungs.filter(ttype_hung='C').order_by('create_time')
        for hung in c_hungs:
            hung_param ={
                'company':self.company,
                'storecode':self.storecode,
                'cashier':self.cashier,
                'hungserno':hung.exptxserno_hung,
                'hunguuid':hung.uuid
            }
            hung_to_tran = hung_to_trans(**hung_param)
            hung_to_tran.c_tran()

    def i_trans_checkout(self):
        i_hungs = self.hungs.filter(ttype_hung='I').order_by('create_time')
        for hung in i_hungs:
            hung_param ={
                'company':self.company,
                'storecode':self.storecode,
                'cashier': self.cashier,
                'hungserno':hung.exptxserno_hung,
                'hunguuid':hung.uuid
            }
            hung_to_tran = hung_to_trans(**hung_param)
            hung_to_tran.i_tran()

    def sg_trans_checkout(self):
        sg_hungs = self.hungs.filter(ttype_hung__in=('S','G')).order_by('create_time')
        for hung in sg_hungs:
            hung_param = {
                'company': self.company,
                'storecode': self.storecode,
                'cashier': self.cashier,
                'hungserno': hung.exptxserno_hung,
                'hunguuid': hung.uuid
            }
            hung_to_tran = hung_to_trans(**hung_param)
            hung_to_tran.sg_tran()

# 对已经成交的交易进行处理
class trans(object):
    def __init__(self,**kwargs):
        print(kwargs)
        self.company=kwargs.get('company','demo')
        self.storecode = kwargs.get('storecode','88')
        self.transuuid = kwargs.get('transuuid','')

        now = datetime.now()
        self.vsdate=now.date().__format__('%Y%m%d')
        self.vstime = now.time().__format__('%H%M%S')

        self.trans_expvstoll = Expvstoll.objects.get_or_create(flag='Y',company=self.company,uuid=self.transuuid)[0]
        self.trans_expense = Expense.objects.filter(flag='Y',company=self.company,transuuid=self.transuuid)
        self.trans_toll = Toll.objects.filter(flag='Y',company=self.company,transuuid=self.transuuid)
        print(self.company,self.storecode, self.transuuid)

    def change_paymode(self,**kwargs):
        oldpcode = kwargs.get('oldpcode','')
        newpcode = kwargs.get('newpcode','')
        amount = kwargs.get('amount',0)
        print('change_paymode')
        oldpaymode = Paymode.objects.get(flag='Y',company=self.company,pcode=newpcode)
        newpaymode = Paymode.objects.get(flag='Y',company=self.company,pcode=newpcode)


    def reculate_trans(self):
        if self.trans_expvstoll.ttype =='G':
            self.trans_expvstoll.set_transgoodstranslog()
            self.trans_expvstoll.set_vipiteminfo()

    def offset_trans(self):
        try:
            trans_expvstoll = Expvstoll.objects.get(flag='Y',company=self.company,uuid=self.transuuid)
            trans_expense = Expense.objects.filter(flag='Y',company=self.company,transuuid=self.transuuid)
            trans_toll = Toll.objects.filter(flag='Y',company=self.company,transuuid=self.transuuid)

            find = Expvstoll.objects.filter(flag='Y',company=self.company,hungserno=trans_expvstoll.exptxserno)
            if len(find) >0 :
                print('已经红冲，不能再次红冲')
                return 0

            find = trans_expvstoll.hungserno.find('EXPVSTOLL')
            if find == 0:
                print('已经是红冲的单子，不能再对冲')
                return 0

            if trans_expvstoll.totmount <=0:
                print('退单不能对冲')
                return 0

            if len(trans_expvstoll.ccode) > 0:
                paycardinfo = Cardinfo.objects.get(flag='Y',company=self.company,ccode=trans_expvstoll.ccode)


            exptxserno = getserno(self.company,self.storecode,'EXPVSTOLL')

            trans_expvstoll.pk = None
            trans_expvstoll.totmount = - trans_expvstoll.totmount
            trans_expvstoll.hungserno = trans_expvstoll.exptxserno
            trans_expvstoll.exptxserno = exptxserno
            trans_expvstoll.vsdate = self.vsdate
            trans_expvstoll.vstime = self.vstime
            trans_expvstoll.passedby = None

            trans_expvstoll.save()

            for trans_item in  trans_expense:
                print(trans_item.ditem)
                trans_item.pk = None
                trans_item.transuuid=trans_expvstoll
                trans_item.s_qty = - trans_item.s_qty
                trans_item.s_mount = - trans_item.s_mount
                trans_item.exptxserno = exptxserno
                if trans_item.ttype in ( 'C','I'):
                    trans_item.ttype ='I'
                    trans_item.addvamoney = trans_item.s_mount
                    # trans_item.save()

                if trans_item.ttype == 'G':
            #         如果是商品，需要处理商品
                    print('G')

                if trans_item.ttype in ( 'C','I'):
                    # 如果是充值或者售卡，需要退回卡余额
                    print('C','I')
                    trans_cardinfo = Cardinfo.objects.get(company=self.company,ccode=trans_item.srvcode)
                    if trans_cardinfo.cardtypeuuid.comptype =='amount':
                        trans_cardinfo.leftmoney = trans_cardinfo.leftmoney - trans_item.addvamoney

                    if trans_cardinfo.cardtypeuuid.comptype == 'times':
                        trans_cardinfo.leftqty = trans_cardinfo.leftqty + trans_item.s_qty
                        trans_cardinfo.leftmoney = trans_cardinfo.leftmoney + trans_item.s_mount
                    trans_cardinfo.save()

                trans_item.save()

            print('trans_toll',len(trans_toll))
            for trans_pay in trans_toll:
                print('trans_pay',trans_pay.pcode,trans_pay.qty,trans_pay.totmount)
                trans_pay.pk = None
                print(1)

                if trans_pay.qty == None:
                    qty = 0
                else:
                    qty = trans_pay.qty

                trans_pay.qty = - qty
                print(2)
                if trans_pay.totmount == None:
                    totamount = 0
                else:
                    totamount = trans_pay.totmount
                trans_pay.totmount = - totamount
                trans_pay.transuuid = trans_expvstoll
                trans_pay.exptxserno = exptxserno
                trans_pay.save()

                paymode= Paymode.objects.get(flag='Y',company=self.company, pcode=trans_pay.pcode)
                if paymode.iscash =='0':
                    # 如果是卡付，需要处理卡的余额
                    print('before leftmoney',paycardinfo.leftmoney)
                    paycardinfo.leftmoney = paycardinfo.leftmoney - trans_pay.totmount
                    paycardinfo.save()
                    print('after leftmoney',paycardinfo.leftmoney)
                    trans_expvstoll.cardleftmoney = paycardinfo.leftmoney

            trans_expvstoll.save()
            trans_expvstoll.set_cardhistory()
            trans_expvstoll.set_transgoodstranslog()
        except Exception as e:
            print('trans_toll Excepition ',e)
            return '0'

def get_emplarchivementbyecode(request):
    company = request.GET['company']
    storecode=request.GET['storecode']
    openid = request.GET['openid']
    ecode = request.GET['ecode']
    fromdate = request.GET['fromdate']
    todate=request.GET['todate']
    param = {
        company:company,
        storecode:storecode,
        ecode:ecode,
        fromdate:fromdate,
        todate:todate
    }
    result = EmplArchivement(company=company,storecode=storecode,ecode=ecode,fromdate=fromdate,todate=todate)
    result.get_vipcnt()
    result.get_viptimes()
    result.get_itemcnt()
    result.get_amounts()
    return_data={}
    print('result',result.reportdata,type(result.reportdata))
    return_data = result.reportdata

    # return HttpResponse(return_data, content_type="application/json")
    return JsonResponse(return_data,safe=False)

def reculate_trans(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']

    items = Expvstoll.objects.filter(flag='Y',company=company, storecode=storecode, valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    for item in items:
        # transuuid = request.GET['transuuid']
        transuuid = item.uuid
        param ={
            'company':company,
            'storecode':storecode,
            'transuuid':transuuid
        }
        print('in param',param)
        tran = trans(**param)
        tran.reculate_trans()

    return HttpResponse('OK', content_type="application/json")

def offset_trans(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    transuuid = request.GET['transuuid']
    param ={
        'company':company,
        'storecode':storecode,
        'transuuid':transuuid
    }
    print('in param',param)
    tran = trans(**param)
    tran.offset_trans()

    return HttpResponse('OK', content_type="application/json")

def checkout_byvip(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    cashier = request.GET['cashier']
    vipuuid = request.GET['vipuuid']
    print('company',company)
    param ={
        'company':company,
        'storecode':storecode,
        'vipuuid':vipuuid
    }
    print('in param',param)

    pre_trans_byvip1 = pre_trans_byvip(**param)
    pre_trans_byvip1.c_trans_checkout()
    pre_trans_byvip1.i_trans_checkout()
    pre_trans_byvip1.sg_trans_checkout()

    # tran.offset_trans()

    return HttpResponse('OK', content_type="application/json")

def checkout_byhunguuid(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    cashier = request.GET['cashier']
    hunguuid = request.GET['hunguuid']
    print('company',company)
    param ={
        'company':company,
        'storecode':storecode,
        'cashier':cashier,
        'hunguuid':hunguuid
    }
    print('in param',param)

    tran = hung_to_trans(**param)
    tran.hunguuid_trans()

    return HttpResponse('OK', content_type="application/json")

def vipitemtrans_confirm(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    cashier = request.GET['cashier']
    vipitemtransuuid = request.GET['vipitemtransuuid']
    param ={
        'company':company,
        'storecode':storecode,
        'cashier':cashier,
        'vipitemtransuuid':vipitemtransuuid
    }
    try:
        print('vipitemtrans_confirm ',company, storecode, vipitemtransuuid)
        vipitemtranshead = VipItemTransHead.objects.get(flag='Y', company=company,uuid=vipitemtransuuid)
        vipitemtranshead.status='30'
        vipitemtranshead.sef_vipitemtranslog()
        vipitemtranshead.creater = cashier
        vipitemtranshead.save()
        print('finished!')
    except Exception as e:
        print('vipitemtrans_confirm Error:', e)



    return HttpResponse('200', content_type="application/json")

def fillcardhistory(request):
    company=request.GET['company']
    storelist =['01','02','03']
    trans = Expvstoll.objects.filter(flag='Y',company=company,storecode__in=storelist,vsdate__lte='20201030').order_by('storecode','create_time','exptxserno')
    for tran in trans:
        print(tran.storecode, tran.vsdate,tran.exptxserno,tran.ttype)
        if len(tran.ccode) > 0:
            try:
                cardhistorys = Cardhistory.objects.filter(flag='Y',company=tran.company, exptxserno = tran.exptxserno)
                if len(cardhistorys) ==0:
                    print('cardhistory not find ', tran.vsdate,tran.exptxserno,tran.ttype, tran.ccode)
                    tran.set_cardhistory()
            except Exception as e:
                print('error',tran.storecode, tran.vsdate,tran.exptxserno,tran.ttype,e)
        else:
            if tran.ttype in ('C','I'):
                try:
                    cardhistorys = Cardhistory.objects.filter(flag='Y', company=tran.company,exptxserno=tran.exptxserno)
                    if len(cardhistorys) == 0:
                        print('cardhistory not find ', tran.storecode, tran.vsdate,tran.exptxserno,tran.ttype,tran.ccode)
                        tran.set_cardhistory()
                except Exception as e:
                    print('error',tran.storecode, tran.vsdate,tran.exptxserno,tran.ttype, e)


    # trans2 = Expense.objects.filter(flag='Y',company=company,storecode__in=storelist,ttype__in=('C','I'),create_time__lte='2020-10-30')
    # for tran2 in trans2:
    #     try:
    #         cardhistorys = Cardhistory.objects.filter(flag='Y', company=tran.company, exptxserno=tran.exptxserno)
    #         if len(cardhistorys) == 0:
    #             print('cardhistory not find ', tran.ccode)
    #             tran.set_cardhistory()
    #     except Exception as e:
    #         print('error', e)
    #
    return HttpResponse('200', content_type="application/json")

# ====== 手动开单 API ======


# ====== 结账接口（从 adviser 迁入） ======

@csrf_exempt
@transaction.atomic
def checkout_hungs(request):
    """
    会员挂单结账：
    - 仅允许结算未完成挂单（10~60）
    - 计次卡：余次充足才可结账，按选中挂单总次数扣减 leftqty
    - 计费卡：余额充足才可结账，按选中挂单总金额扣减 leftmoney
    """
    try:
        payload = _parse_request_param_json(request)
    except Exception:
        return JsonResponse({'ok': False, 'message': '参数格式错误'}, status=400)

    company = payload.get('company') or request.GET.get('company') or common.constants.COMPANYID
    storecode = payload.get('storecode') or request.GET.get('storecode') or '88'
    vipuuid_raw = payload.get('vipuuid') or request.GET.get('vipuuid') or ''
    hunguuids_raw = payload.get('hunguuids') or []
    extra_payments = payload.get('extra_payments') or []
    extra_paymode = (payload.get('extra_paymode') or '').strip()
    try:
        extra_pay_amount = Decimal(str(payload.get('extra_pay_amount') or '0'))
    except Exception:
        extra_pay_amount = Decimal('0')
    if extra_pay_amount < 0:
        extra_pay_amount = Decimal('0')
    if not isinstance(extra_payments, list):
        extra_payments = []

    if not vipuuid_raw:
        return JsonResponse({'ok': False, 'message': '缺少会员参数'}, status=400)
    if not isinstance(hunguuids_raw, list) or len(hunguuids_raw) == 0:
        return JsonResponse({'ok': False, 'message': '请至少选择一笔开单'}, status=400)

    try:
        vipuuid = _parse_uuid_loose(vipuuid_raw)
    except Exception:
        return JsonResponse({'ok': False, 'message': '会员参数无效'}, status=400)

    hunguuids = []
    for h in hunguuids_raw:
        try:
            hunguuids.append(_parse_uuid_loose(h))
        except Exception:
            continue
    if not hunguuids:
        return JsonResponse({'ok': False, 'message': '结账单据参数无效'}, status=400)

    open_status = ('10', '20', '30', '40', '50', '60')
    try:
        hungs = list(
            ExpvstollHung.objects.select_for_update().filter(
                company=company,
                storecode=storecode,
                flag='Y',
                valiflag_hung='Y',
                vipuuid=vipuuid,
                psstatus_hung__in=open_status,
                uuid__in=hunguuids,
            )
        )
        if len(hungs) != len(hunguuids):
            return JsonResponse({'ok': False, 'message': '部分开单已失效或不可结账'}, status=400)

        grouped = {}
        total_amount = Decimal('0')
        total_qty = Decimal('0')
        h_stype_map = {}
        for eh in ExpenseHung.objects.filter(company=company, hunguuid__in=hunguuids, flag='Y').only('hunguuid', 'stype_hung', 'ditem_hung').order_by('ditem_hung'):
            k = str(eh.hunguuid_id)
            if k not in h_stype_map:
                h_stype_map[k] = eh.stype_hung
        for h in hungs:
            ccode = (h.ccode_hung or '').strip()
            h_stype = h_stype_map.get(str(h.uuid), 'N')
            payinfo = _resolve_paycard_plan_info(company, ccode, h.cardtype_hung, h_stype)
            pcode = (payinfo.get('paytype') or '').strip()
            p_iscash = ''
            if pcode:
                pm = (
                    Paymode.objects.filter(company=company, pcode=pcode)
                    .values_list('iscash', flat=True)
                    .first()
                )
                p_iscash = (pm or '').strip()
            if not p_iscash:
                # 无法映射付款方式时按非卡付类处理，避免误走卡号校验导致 400
                p_iscash = '1'
            grp_key = ccode + '|' + pcode + '|' + p_iscash
            if grp_key not in grouped:
                grouped[grp_key] = {
                    'ccode': ccode,
                    'pcode': pcode,
                    'iscash': p_iscash,
                    'amount': Decimal('0'),
                    'qty': Decimal('0'),
                    'hungs': [],
                }
            grouped[grp_key]['amount'] += Decimal(h.sumamount or 0)
            grouped[grp_key]['qty'] += Decimal(h.sumqty or 0)
            grouped[grp_key]['hungs'].append(h)
            total_amount += Decimal(h.sumamount or 0)
            total_qty += Decimal(h.sumqty or 0)

        amount_deductions = []
        total_extra_due = Decimal('0')
        noncard_due = Decimal('0')
        h_card_alloc = {}
        h_noncard_need = {}
        h_paymeta = {}
        for _, bucket in grouped.items():
            ccode = bucket['ccode']
            pcode = bucket['pcode']
            iscash = bucket['iscash']
            for hh in bucket['hungs']:
                h_paymeta[str(hh.uuid)] = {'ccode': ccode, 'pcode': pcode, 'iscash': iscash}
            # 非卡付类（iscash=1/2）不校验卡号和卡余额
            if iscash in ('1', '2'):
                noncard_due += bucket['amount']
                for hh in bucket['hungs']:
                    h_noncard_need[str(hh.uuid)] = Decimal(hh.sumamount or 0)
                continue
            # 卡付类（iscash=0 或未知）才走卡号/余额校验
            if not ccode:
                return JsonResponse({'ok': False, 'message': '卡付类结账存在未设置付款卡号的开单'}, status=400)
            paycard = (
                Cardinfo.objects.select_for_update()
                .select_related('cardtypeuuid')
                .filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            if not paycard:
                return JsonResponse({'ok': False, 'message': '付款卡不存在或不属于该客人：' + ccode}, status=400)

            comptype = ''
            if paycard.cardtypeuuid and paycard.cardtypeuuid.comptype:
                comptype = paycard.cardtypeuuid.comptype
            if comptype not in ('times', 'amount'):
                return JsonResponse({'ok': False, 'message': '付款卡不支持结账：' + ccode}, status=400)

            if comptype == 'times':
                leftqty = Decimal(paycard.leftqty or 0)
                need_qty = bucket['qty']
                if leftqty < need_qty:
                    lack = need_qty - leftqty
                    return JsonResponse(
                        {
                            'ok': False,
                            'code': 'INSUFFICIENT_TIMES',
                            'message': '付款卡余次不足，无法结账：' + ccode,
                            'payccode': ccode,
                            'need_qty': float(lack),
                            'left_qty': float(leftqty),
                            'total_qty': float(need_qty),
                        },
                        status=400,
                    )
                paycard.leftqty = leftqty - need_qty
                paycard.save(update_fields=['leftqty'])
                for hh in bucket['hungs']:
                    h_amt = Decimal(hh.sumamount or 0)
                    h_card_alloc[str(hh.uuid)] = h_amt
                    h_noncard_need[str(hh.uuid)] = Decimal('0')
            else:
                leftmoney = Decimal(paycard.leftmoney or 0)
                need_amount = bucket['amount']
                if leftmoney < need_amount:
                    lack = need_amount - leftmoney
                    total_extra_due += lack
                    amount_deductions.append((paycard, leftmoney))
                    remain = leftmoney
                    for hh in bucket['hungs']:
                        h_amt = Decimal(hh.sumamount or 0)
                        card_part = h_amt if remain >= h_amt else remain
                        if card_part < 0:
                            card_part = Decimal('0')
                        remain = remain - card_part
                        h_card_alloc[str(hh.uuid)] = card_part
                        h_noncard_need[str(hh.uuid)] = h_amt - card_part
                else:
                    amount_deductions.append((paycard, need_amount))
                    for hh in bucket['hungs']:
                        h_amt = Decimal(hh.sumamount or 0)
                        h_card_alloc[str(hh.uuid)] = h_amt
                        h_noncard_need[str(hh.uuid)] = Decimal('0')

        declared_total = Decimal('0')
        for ep in extra_payments:
            pcode = str(ep.get('pcode') or '').strip()
            if not pcode:
                continue
            try:
                amt = Decimal(str(ep.get('amount') or '0'))
            except Exception:
                amt = Decimal('0')
            if amt <= 0:
                continue
            pm = (
                Paymode.objects.filter(company=company, flag='Y', visibleflag='Y', pcode=pcode)
                .exclude(iscash='0')
                .first()
            )
            if pm:
                declared_total += amt

        # 兼容旧参数
        if declared_total <= 0 and extra_pay_amount > 0 and extra_paymode:
            pm = (
                Paymode.objects.filter(company=company, flag='Y', visibleflag='Y', pcode=extra_paymode)
                .exclude(iscash='0')
                .first()
            )
            if pm:
                declared_total = extra_pay_amount

        required_noncard = noncard_due + total_extra_due
        auto_added_amount = Decimal('0')
        auto_added_pcode = ''
        if required_noncard > 0:
            if declared_total < required_noncard:
                # 第一种付款方式不足时，自动补第二种默认付款方式（现金优先）
                auto_added_amount = required_noncard - declared_total
                dpm = (
                    Paymode.objects.filter(company=company, flag='Y', visibleflag='Y')
                    .exclude(iscash='0')
                    .order_by('pcode')
                    .first()
                )
                if dpm:
                    auto_added_pcode = dpm.pcode or ''
                declared_total = required_noncard

        for paycard, deduct_amount in amount_deductions:
            leftmoney = Decimal(paycard.leftmoney or 0)
            real_deduct = deduct_amount if deduct_amount <= leftmoney else leftmoney
            paycard.leftmoney = leftmoney - real_deduct
            paycard.save(update_fields=['leftmoney'])

        # 组装非卡付款池（支持最多两种，第二种可自动补齐）
        extra_pool = []
        for ep in extra_payments:
            pcode = str(ep.get('pcode') or '').strip()
            try:
                amt = Decimal(str(ep.get('amount') or '0'))
            except Exception:
                amt = Decimal('0')
            if pcode and amt > 0:
                extra_pool.append({'pcode': pcode, 'amount': amt})
        if auto_added_amount > 0:
            extra_pool.append({'pcode': auto_added_pcode or extra_paymode or common.constants.DEFAULT_NORMAL_PCODE, 'amount': auto_added_amount})

        now = datetime.now()
        vsdate_now = now.strftime('%Y%m%d')
        vstime_now = now.strftime('%H%M%S')
        created_exptxsernos = []
        created_toll_count = 0
        created_cardhistory_count = 0

        # 落库：expvstoll / expense / toll
        for h in hungs:
            h_id = str(h.uuid)
            ccode_val = h.ccode_hung or ''
            cardtype_val = h.cardtype_hung or ''
            if ccode_val and not cardtype_val:
                try:
                    _ci = Cardinfo.objects.filter(company=company, ccode=ccode_val).select_related('cardtypeuuid').first()
                    if _ci and _ci.cardtypeuuid:
                        cardtype_val = _ci.cardtypeuuid.cardtype
                except:
                    pass
            card_out_changes = {}
            exptxserno = GetSerno(company, storecode, 'EXPVSTOLL')
            created_exptxsernos.append(exptxserno)
            trans = Expvstoll.objects.create(
               company=company,
               storecode=storecode,
               vipuuid=h.vipuuid,
               vcode=h.vcode_hung or '',
                ccode=ccode_val,
                cardtype=cardtype_val,
                exptxserno=exptxserno,
                vsdate=vsdate_now,
                vstime=vstime_now,
                valiflag='Y',
                ttype=h.ttype_hung or '',
                hungserno=h.exptxserno_hung or '',
                totmount=Decimal(h.sumamount or 0),
                mondisc=h.mondisc_hung,
                sumdisc=h.sumdisc_hung,
                ecode=h.ecode_hung or '',
                pmcode=h.pmcode_hung or '',
                asscode1=h.asscode1_hung or '',
                asscode2=h.asscode2_hung or '',
                promotionsid=h.promotionsid or '',
                bookingeventid=h.bookingeventid,
            )

            lines = list(ExpenseHung.objects.filter(company=company, hunguuid=h.uuid, flag='Y').order_by('ditem_hung'))
            created_expenses = []
            for ln in lines:
                exp_row = Expense.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    ditem=ln.ditem_hung or '0001',
                    ttype=ln.ttype_hung or '',
                    stype=ln.stype_hung or '',
                    srvcode=ln.srvcode_hung or '',
                    s_qty=ln.s_qty_hung,
                    s_price=ln.s_price_hung,
                    s_mount=ln.s_mount_hung,
                    secdisc=ln.secdisc_hung,
                    srvmondisc=ln.srvmondisc_hung,
                    pmcode=ln.pmcode_hung or '',
                    asscode1=ln.asscode1_hung or '',
                    asscode2=ln.asscode2_hung or '',
                    dnote=ln.dnote_hung or '',
                    oldcardtype=ln.oldcardtype_hung or '',
                    newcardtype=ln.newcardtype_hung or '',
                    addvamoney=ln.addvamoney_hung,
                )
                created_expenses.append(exp_row)
                # 商品结账同步写入商品进出记录（仓库取门店销售仓：storeinfo.salewhcode）
                if (exp_row.ttype or '') == 'G':
                    exp_row.set_goodstranslog()

            paymeta = h_paymeta.get(h_id, {})
            pcode = (paymeta.get('pcode') or common.constants.DEFAULT_NORMAL_PCODE)
            iscash = (paymeta.get('iscash') or '1')
            expvssvern_no = 1

            # 卡付部分
            card_amt = Decimal(h_card_alloc.get(h_id, Decimal('0')))
            if card_amt > 0 and iscash == '0':
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=pcode,
                    totmount=card_amt,
                    qty=Decimal(h.sumqty or 0),
                    currency='RMB',
                    custperc=1,
                    ccode=paymeta.get('ccode') or '',
                )
                created_toll_count += 1
                ccode_key = paymeta.get('ccode') or ''
                if ccode_key:
                    card_out_changes[ccode_key] = card_out_changes.get(ccode_key, Decimal('0')) + card_amt
                expvssvern_no += 1

            # 非卡部分（含本身非卡交易 + 卡不足补差）
            noncard_amt = Decimal(h_noncard_need.get(h_id, Decimal('0')))
            while noncard_amt > 0 and len(extra_pool) > 0:
                ep = extra_pool[0]
                use_amt = ep['amount'] if ep['amount'] <= noncard_amt else noncard_amt
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=ep['pcode'],
                    totmount=use_amt,
                    qty=1,
                    currency='RMB',
                    custperc=1,
                    ccode='',
                )
                created_toll_count += 1
                expvssvern_no += 1
                noncard_amt -= use_amt
                ep['amount'] -= use_amt
                if ep['amount'] <= 0:
                    extra_pool.pop(0)

            # 兜底：若仍有未分配金额，挂默认现金类
            if noncard_amt > 0:
                fallback_pcode = auto_added_pcode or extra_paymode or common.constants.DEFAULT_NORMAL_PCODE
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=fallback_pcode,
                    totmount=noncard_amt,
                    qty=1,
                    currency='RMB',
                    custperc=1,
                    ccode='',
                )
                created_toll_count += 1

            # 售卡交易：挂账售卡阶段卡状态为 P，结账后转 O，并同步卡类
            for exp_row in created_expenses:
                if (exp_row.ttype or '') == 'C':
                    sold_ccode = (exp_row.srvcode or '').strip()
                    if not sold_ccode:
                        continue
                    sold_card = (
                        Cardinfo.objects.filter(company=company, ccode=sold_ccode)
                        .order_by('-create_time')
                        .first()
                    )
                    if not sold_card:
                        continue
                    changed_fields = []
                    if sold_card.status == 'P':
                        sold_card.status = 'O'
                        changed_fields.append('status')
                    if exp_row.newcardtype and sold_card.cardtype != exp_row.newcardtype:
                        sold_card.cardtype = exp_row.newcardtype
                        changed_fields.append('cardtype')
                    if changed_fields:
                        sold_card.save(update_fields=changed_fields)

            # 卡余额变更日志（cardhistory）
            # 1) 支付卡扣减（outamount）
            for ccode_key, out_amt in card_out_changes.items():
                if out_amt <= 0:
                    continue
                pay_card = (
                    Cardinfo.objects.filter(company=company, ccode=ccode_key)
                    .select_related('cardtypeuuid')
                    .order_by('-create_time')
                    .first()
                )
                if not pay_card:
                    continue
                ch, ch_created = Cardhistory.objects.get_or_create(
                    company=company,
                    storecode=storecode,
                    vsdate=vsdate_now,
                    ccode=ccode_key,
                    exptxserno=exptxserno,
                )
                if ch_created:
                    created_cardhistory_count += 1
                ch.outamount = out_amt
                ch.inamount = ch.inamount or Decimal('0')
                ch.vipuuid = trans.vipuuid
                ch.cardinfouuid = pay_card
                ch.cardtypeuuid = pay_card.cardtypeuuid
                if pay_card.cardtypeuuid_id and pay_card.cardtypeuuid:
                    ch.comptype = pay_card.cardtypeuuid.comptype
                    ch.suptype = pay_card.cardtypeuuid.suptype
                ch.transuuid = trans
                ch.save()
                try:
                    ch.recalamount()
                except Exception:
                    pass

            # 2) 售卡/充值入账（inamount）
            for exp_row in created_expenses:
                if (exp_row.ttype or '') not in ('C', 'I'):
                    continue
                sold_ccode = (exp_row.srvcode or '').strip()
                if not sold_ccode:
                    continue
                sold_card = (
                    Cardinfo.objects.filter(company=company, ccode=sold_ccode)
                    .select_related('cardtypeuuid')
                    .order_by('-create_time')
                    .first()
                )
                if not sold_card:
                    continue
                in_amt = Decimal(exp_row.addvamoney or 0)
                if in_amt <= 0:
                    in_amt = Decimal(exp_row.s_mount or 0)
                ch, ch_created = Cardhistory.objects.get_or_create(
                    company=company,
                    storecode=storecode,
                    vsdate=vsdate_now,
                    ccode=sold_ccode,
                    exptxserno=exptxserno,
                )
                if ch_created:
                    created_cardhistory_count += 1
                ch.inamount = in_amt
                ch.outamount = ch.outamount or Decimal('0')
                ch.vipuuid = trans.vipuuid
                ch.cardinfouuid = sold_card
                ch.cardtypeuuid = sold_card.cardtypeuuid
                if sold_card.cardtypeuuid_id and sold_card.cardtypeuuid:
                    ch.comptype = sold_card.cardtypeuuid.comptype
                    ch.suptype = sold_card.cardtypeuuid.suptype
                ch.transuuid = trans
                ch.save()
                try:
                    ch.recalamount()
                except Exception:
                    pass

        for _, bucket in grouped.items():
            ccode = bucket['ccode']
            paycard = (
                Cardinfo.objects.filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            for h in bucket['hungs']:
                h.cardtype_hung = paycard.cardtype if paycard else (h.cardtype_hung or '')
                h.ccode_hung = ccode
                h.psstatus_hung = '70'
                h.save(update_fields=['psstatus_hung', 'ccode_hung', 'cardtype_hung'])

        settled = len(hungs)

        return JsonResponse(
            {
                'ok': True,
                'message': '结账成功',
                'settled_count': settled,
                'total_amount': float(total_amount),
                'total_qty': float(total_qty),
                'total_extra_due': float(total_extra_due),
                'noncard_due': float(noncard_due),
                'required_noncard': float(required_noncard),
                'extra_paymode': extra_paymode,
                'extra_pay_amount': float(extra_pay_amount),
                'auto_added_pcode': auto_added_pcode,
                'auto_added_amount': float(auto_added_amount),
                'exptxsernos': created_exptxsernos,
                'toll_count': created_toll_count,
                'cardhistory_count': created_cardhistory_count,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                'ok': False,
                'code': 'CHECKOUT_SERVER_ERROR',
                'message': '结账落库异常',
                'detail': str(e),
                'trace': traceback.format_exc().splitlines()[-1] if traceback.format_exc() else '',
            },
            status=400,
        )





@csrf_exempt
def get_checkout_shortfall(request):
    company = request.GET.get('company', common.constants.COMPANYID)
    storecode = request.GET.get('storecode', '88')
    vipuuid_raw = request.GET.get('vipuuid', '')
    hraw = request.GET.get('hunguuids', '[]')
    try:
        hlist = json.loads(hraw) if isinstance(hraw, str) else []
    except Exception:
        hlist = []
    if not isinstance(hlist, list):
        hlist = []
    try:
        vipuuid = _parse_uuid_loose(vipuuid_raw)
    except Exception:
        vipuuid = None
    hunguuids = []
    for h in hlist:
        try:
            hunguuids.append(_parse_uuid_loose(h))
        except Exception:
            continue
    total_extra_due = Decimal('0')
    noncard_due = Decimal('0')
    total_selected_amount = Decimal('0')
    if vipuuid and hunguuids:
        open_status = ('10', '20', '30', '40', '50', '60')
        hungs = list(
            ExpvstollHung.objects.filter(
                company=company,
                storecode=storecode,
                flag='Y',
                valiflag_hung='Y',
                vipuuid=vipuuid,
                psstatus_hung__in=open_status,
                uuid__in=hunguuids,
            )
        )
        grouped = {}
        h_stype_map = {}
        for eh in ExpenseHung.objects.filter(company=company, hunguuid__in=hunguuids, flag='Y').only('hunguuid', 'stype_hung', 'ditem_hung').order_by('ditem_hung'):
            k = str(eh.hunguuid_id)
            if k not in h_stype_map:
                h_stype_map[k] = eh.stype_hung
        for h in hungs:
            total_selected_amount += Decimal(h.sumamount or 0)
            ccode = (h.ccode_hung or '').strip()
            h_stype = h_stype_map.get(str(h.uuid), 'N')
            payinfo = _resolve_paycard_plan_info(company, ccode, h.cardtype_hung, h_stype)
            pcode = (payinfo.get('paytype') or '').strip()
            p_iscash = ''
            if pcode:
                p_iscash = (
                    Paymode.objects.filter(company=company, pcode=pcode)
                    .values_list('iscash', flat=True)
                    .first()
                    or ''
                )
            grp_key = ccode + '|' + pcode + '|' + p_iscash
            grouped[grp_key] = grouped.get(grp_key, Decimal('0')) + Decimal(h.sumamount or 0)
        for grp_key, need_amount in grouped.items():
            parts = grp_key.split('|')
            ccode = parts[0] if len(parts) > 0 else ''
            iscash = parts[2] if len(parts) > 2 else ''
            if iscash in ('1', '2'):
                noncard_due += need_amount
                continue
            paycard = (
                Cardinfo.objects.filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            leftmoney = Decimal(paycard.leftmoney or 0) if paycard else Decimal('0')
            if leftmoney < need_amount:
                total_extra_due += need_amount - leftmoney

    paymodes = list(
        Paymode.objects.filter(company=company, flag='Y', visibleflag='Y')
        .exclude(iscash='0')
        .values('pcode', 'pname', 'iscash')
        .order_by('pcode')
    )
    return JsonResponse(
        {
            'ok': True,
            'total_extra_due': float(total_extra_due),
            'noncard_due': float(noncard_due),
            'required_noncard': float(total_extra_due + noncard_due),
            'card_paid_amount': float(max(total_selected_amount - (total_extra_due + noncard_due), Decimal('0'))),
            'paymodes': paymodes,
        }
    )



def customer_checkout(request):
    '''客户级结账汇总：按支付方式分类待结项目'''
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '01')
    vipuuid = request.GET.get('vipuuid', '')
    if not company or not vipuuid:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        vip = Vip.objects.get(uuid=vipuuid)
    except Vip.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '会员不存在'})
    open_status = ('10', '20', '30', '40', '50', '60')
    hungs = list(ExpvstollHung.objects.filter(
        company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
        psstatus_hung__in=open_status, vipuuid=vip,
    ).order_by('ccode_hung'))
    if not hungs:
        return JsonResponse({'ok': True, 'total': 0, 'orders': 0, 'items': 0, 'summary': {}})
    hung_uuids = [h.uuid for h in hungs]
    item_qs = ExpenseHung.objects.filter(hunguuid__in=hung_uuids, flag='Y').values(
        'hunguuid_id', 'ttype_hung', 'srvcode_hung', 'stype_hung',
        's_qty_hung', 's_price_hung', 's_mount_hung',
        'otherserno_hung', 'pmcode_hung', 'asscode1_hung', 'asscode2_hung'
    ).order_by('ditem_hung')
    all_items = list(item_qs)
    all_ccodes = {it['otherserno_hung'] for it in all_items if it.get('otherserno_hung')}
    card_info = {}
    if all_ccodes:
        for c in Cardinfo.objects.filter(company=company, ccode__in=list(all_ccodes), flag='Y')                .select_related('cardtypeuuid'):
            card_info[c.ccode] = {
                'comptype': c.cardtypeuuid.comptype if c.cardtypeuuid else '',
                'balance': float(c.leftmoney or 0),
                'leftqty': float(c.leftqty or 0),
            }
        times_map = defaultdict(list)
    card_map = defaultdict(list)
    gift_items = []
    pending_items = []
    total = 0
    for it in all_items:
        ccode = it.get('otherserno_hung', '') or ''
        stype = it.get('stype_hung', '') or 'N'
        mount = float(it.get('s_mount_hung', 0) or 0)
        total += mount
        ci = card_info.get(ccode)
        if ccode and ci and ci['comptype'] == 'times':
            times_map[ccode].append(it)
        elif ccode and ci:
            card_map[ccode].append(it)
        elif stype == 'P':
            gift_items.append(it)
        else:
            pending_items.append(it)
    hung_order_map = {str(h.uuid): h.exptxserno_hung for h in hungs}
    def resolve_item(it, status=''):
        name = _resolve_hung_itemname(company, it.get('ttype_hung','') or '', it.get('srvcode_hung','') or '')
        return {'name': name or it.get('srvcode_hung','') or '', 'order_no': hung_order_map.get(str(it.get('hunguuid_id','') or ''), '') or '',
                'qty': float(it.get('s_qty_hung',0) or 0),
                'price': float(it.get('s_price_hung',0) or 0),
                'mount': float(it.get('s_mount_hung',0) or 0),
                'stype': (it.get('stype_hung','') or 'N'),
                'pmcode': it.get('pmcode_hung','') or '',
                'asscode1': it.get('asscode1_hung','') or '',
                'asscode2': it.get('asscode2_hung','') or ''}
    times_cards = []
    for ccode, its in times_map.items():
        ci = card_info.get(ccode, {})
        total_qty = int(sum(it.get('s_qty_hung',1) or 1 for it in its))
        times_cards.append({
            'ccode': ccode, 'comptype': 'times',
            'leftqty': ci.get('leftqty', 0) if ci else 0,
            'leftmoney': ci.get('balance', 0) if ci else 0,
            'deduct_qty': total_qty,
            'items': [resolve_item(it, 'times') for it in its],
        })
    auto_cards = []
    for ccode, its in card_map.items():
        ci = card_info.get(ccode, {})
        total_amt = sum(float(it.get('s_mount_hung',0) or 0) for it in its)
        auto_cards.append({
            'ccode': ccode, 'comptype': 'amount',
            'balance': ci.get('balance', 0) if ci else 0,
            'deduct_amount': round(total_amt, 2),
            'items': [resolve_item(it, 'times') for it in its],
        })
    gift_total = sum(float(it.get('s_mount_hung',0) or 0) for it in gift_items)
    pending_total = sum(float(it.get('s_mount_hung',0) or 0) for it in pending_items)
    return JsonResponse({
        'ok': True,
        'vipuuid': str(vip.uuid),
        'vname': vip.vname or '',
        'vcode': vip.vcode or '',
        'total': round(total, 2),
        'orders': len(hungs),
        'items': len(all_items),
        'summary': {
            'times_cards': times_cards,
            'auto_cards': auto_cards,
            'gift': {'items': [resolve_item(it, 'gift') for it in gift_items], 'total': round(gift_total, 2)},
            'pending': {'items': [resolve_item(it, 'pending') for it in pending_items], 'total': round(pending_total, 2)},
        },
    })



@csrf_exempt
def customer_checkout_confirm(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '\u4ec5\u652f\u6301 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    company = data.get('company', '')
    storecode = data.get('storecode', '01')
    vipuuid = data.get('vipuuid', '')
    cashier = data.get('cashier', '')
    payments = data.get('payments', [])
    if not company or not vipuuid or not cashier:
        return JsonResponse({'ok': False, 'message': '\u7f3a\u5c11\u5fc5\u8981\u53c2\u6570'})
    try:
        vip = Vip.objects.get(uuid=vipuuid)
    except Vip.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '\u4f1a\u5458\u4e0d\u5b58\u5728'})
    open_status = ('10', '20', '30', '40', '50', '60')
    hungs = list(ExpvstollHung.objects.filter(
        company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
        psstatus_hung__in=open_status, vipuuid=vip,
    ))
    if not hungs:
        return JsonResponse({'ok': False, 'message': '\u8be5\u4f1a\u5458\u6ca1\u6709\u5f85\u7ed3\u8d26\u7684\u6302\u5355'})
        results = []
    total_amount = Decimal('0')
    for hung in hungs:
        try:
            total_amount += hung.totmount_hung or Decimal('0')
            tran = hung_to_trans(
                company=company, storecode=storecode,
                cashier=cashier,
                hungserno=hung.exptxserno_hung,
                hunguuid=str(hung.uuid),
            )
            tran.hunguuid_trans()
            results.append({'uuid': str(hung.uuid), 'exptxserno': hung.exptxserno_hung, 'ok': True, 'amount': float(hung.totmount_hung or 0)})
        except Exception as e:
            results.append({'uuid': str(hung.uuid), 'ok': False, 'message': str(e)})
    ok_count = sum(1 for r in results if r.get('ok'))
    if payments and ok_count > 0:
        succeeded = [r for r in results if r.get('ok')]
        for p in payments:
            pcode = str(p.get('pcode', '') or '')
            amount = Decimal(str(p.get('amount', 0) or 0))
            if amount <= 0:
                continue
            total_ok = sum(Decimal(str(r.get('amount', 0) or 0)) for r in succeeded)
            for r in succeeded:
                try:
                    trans = Expvstoll.objects.filter(company=company, hungserno=r['exptxserno']).first()
                    if not trans:
                        continue
                    ratio = Decimal(str(r['amount'])) / total_ok if total_ok > 0 else Decimal('1')
                    split_amount = (amount * ratio).quantize(Decimal('0.01'))
                    if split_amount > 0:
                        toll = Toll.objects.create(
                            company=company, storecode=storecode,
                            transuuid=trans, pcode=pcode,
                            expvssvern='1', totmount=split_amount,
                            ccode='', currency='RMB', custperc=1,
                        )
                        toll.exptxserno = trans.exptxserno if trans else ''
                        toll.save()
                except Exception:
                    pass
    return JsonResponse({
        'ok': True,
        'orders': ok_count,
        'total': float(total_amount),
        'results': results,
        'payments': payments,
    })


@csrf_exempt
def payment_methods(request):
    '''获取付款方式列表（Paymode）+ 默认付款方式编码'''
    company = request.GET.get('company', '')
    paymodes = Paymode.objects.filter(company=company, flag='Y').values('pcode', 'pname', 'iscash').order_by('iscash', 'pcode')
    pm_list = list(paymodes)
    normal_def = next((p for p in pm_list if p['iscash'] == '1'), None)
    send_def = next((p for p in pm_list if p['iscash'] == '2'), None)
    return JsonResponse({
        'paymodes': pm_list,
        'defaults': {
            'normal_pcode': normal_def['pcode'] if normal_def else '',
            'send_pcode': send_def['pcode'] if send_def else '',
        }
    })



@csrf_exempt
def batch_checkout(request):
    '''批量结账：对指定的挂单进行结账（调用 cashier.hung_to_trans）'''
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    company = data.get('company', '')
    storecode = data.get('storecode', '01')
    cashier = data.get('cashier', '')
    uuids = data.get('uuids', [])
    if not company or not uuids:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'})
    if not cashier:
        return JsonResponse({'ok': False, 'message': '请输入收银员工号'})

    payments = data.get('payments', {})

    print('batch_checkout post',company, uuids, payments)
    results = []
    for hunguuid in uuids:
        try:
            uuid_obj = _parse_uuid_loose(hunguuid)
            hung = ExpvstollHung.objects.get(uuid=uuid_obj, company=company, flag='Y', valiflag_hung='Y')
            if hung.psstatus_hung == '70':
                results.append({'uuid': hunguuid, 'exptxserno': hung.exptxserno_hung, 'ok': False, 'message': '已结账'})
                continue
            # 更新付款方式（结账时可修改）
            if hunguuid in payments:
                new_ccode = (payments[hunguuid] or '').strip()
                if new_ccode != (hung.ccode_hung or ''):
                    hung.ccode_hung = new_ccode
                    hung.save(update_fields=['ccode_hung'])
            # 多支付方式拆分
            splits = data.get('splits', {})
            hung_splits = splits.get(hunguuid, [])
            if hung_splits and len(hung_splits) > 0:
                print(f'[batch_checkout] SPLIT BRANCH: {hunguuid} splits={hung_splits}')
                # 使用 hung_to_trans 创建 expvstoll + expense，跳过 set_toll()
                st = hung_to_trans(
                    company=company, storecode=storecode,
                    cashier=cashier,
                    hungserno=hung.exptxserno_hung,
                    hunguuid=str(hung.uuid),
                )
                st.hungtoexpvstoll()
                # 手工创建多条 Toll 记录
                total_split = 0
                for sp in hung_splits:
                    print('sp')
                    pcode = sp.get('pcode', '')
                    ccode = sp.get('ccode', '') or ''
                    amount = float(sp.get('amount', 0))
                    print('sp pcode, amount',pcode, amount)
                    if amount <= 0:
                        continue
                    total_split += amount
                    toll, _ = Toll.objects.get_or_create(
                        company=company, storecode=storecode,
                        transuuid=st.expvstoll, pcode=pcode,
                        defaults={
                            'expvssvern': '1', 'totmount': amount,
                            'ccode': ccode, 'currency': 'RMB', 'custperc': 1,
                        }
                    )
                    if not toll.pk:
                        toll.expvssvern = '1'
                        toll.totmount = amount
                        toll.ccode = ccode
                        toll.currency = 'RMB'
                        toll.custperc = 1
                    toll.totmount = amount
                    toll.save()
                    st.tolls.append(toll)
                    # 卡付款：扣余额
                    if ccode:
                        try:
                            card = Cardinfo.objects.get(company=company, ccode=ccode, flag='Y')
                            ct = card.cardtypeuuid
                            if ct and ct.comptype == 'amount' and (card.leftmoney or 0) >= Decimal(str(amount)):
                                card.leftmoney = (card.leftmoney or Decimal('0')) - Decimal(str(amount))
                                card.save()
                            elif ct and ct.comptype == 'times' and (card.leftqty or 0) >= Decimal(str(amount)):
                                card.leftqty = (card.leftqty or Decimal('0')) - Decimal(str(amount))
                                card.save()
                        except Cardinfo.DoesNotExist:
                            pass

                # 激活售卡产生的卡片（Expense.ttype='C' → Cardinfo status P→O）
                for _exp in Expense.objects.filter(company=company, transuuid=st.expvstoll, ttype='C'):
                    if _exp.srvcode:
                        Cardinfo.objects.filter(company=company, ccode=_exp.srvcode, status='P').update(status='O')
                st.set_exptxserno()
                # 记录卡片流水（付款卡扣款 + 新卡充值）
                hung.psstatus_hung = '70'
                hung.save()
                try:
                    st.expvstoll.set_cardhistory()
                except:
                    pass
                continue
            tran = hung_to_trans(
                company=company, storecode=storecode,
                cashier=cashier,
                hungserno=hung.exptxserno_hung,
                hunguuid=str(hung.uuid),
            )
            tran.hunguuid_trans()
            print(f'[batch_checkout] NON-SPLIT BRANCH: {hunguuid}')
            hung.psstatus_hung = "70"
            hung.save()
            results.append({'uuid': hunguuid, 'exptxserno': hung.exptxserno_hung, 'ok': True})
        except ExpvstollHung.DoesNotExist:
            results.append({'uuid': hunguuid, 'ok': False, 'message': '挂单不存在'})
        except Exception as e:
                        results.append({'uuid': hunguuid, 'ok': False, 'message': str(e)})
    ok_count = sum(1 for r in results if r.get('ok'))
    return JsonResponse({'ok': True, 'total': len(results), 'success': ok_count, 'results': results})



@csrf_exempt
def get_checkedout_orders(request):
    """获取会员已结账的订单（用于退款），默认最近一个月"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '88')
    vipuuid = request.GET.get('vipuuid', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if not company or not vipuuid:
        return JsonResponse([], safe=False)
    try:
        v_uuid = _parse_uuid_loose(vipuuid)
    except:
        return JsonResponse([], safe=False)

    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y%m%d')

    qs = ExpvstollHung.objects.filter(
        company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
        psstatus_hung='70', vipuuid=v_uuid,
        vsdate_hung__gte=date_from, vsdate_hung__lte=date_to,
    ).order_by('-vsdate_hung', '-vstime_hung')[:100]

    data = []
    for h in qs:
        vname = ''
        if h.vipuuid_id:
            try:
                v = Vip.objects.get(uuid=h.vipuuid_id)
                vname = v.vname
            except:
                pass
        data.append({
            'uuid': str(h.uuid),
            'exptxserno': h.exptxserno_hung or '',
            'vcode': h.vcode_hung or '',
            'vname': vname,
            'vsdate': h.vsdate_hung or '',
            'vstime': h.vstime_hung or '',
            'totmount': float(h.totmount_hung or 0),
            'itemcount': ExpenseHung.objects.filter(hunguuid=h.uuid, flag='Y').count(),
        })
    return JsonResponse(data, safe=False)



@csrf_exempt

@csrf_exempt
def update_checkedout(request):
    """修改已结账单据（员工信息等）"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    company = data.get('company', '')
    exptxserno = data.get('exptxserno', '')
    changes = data.get('changes', {})
    if not company or not exptxserno:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'})
    try:
        trans = Expvstoll.objects.filter(company=company, hungserno=exptxserno).first()
        if not trans:
            trans = Expvstoll.objects.filter(company=company, exptxserno=exptxserno).first()
        if not trans:
            return JsonResponse({'ok': False, 'message': '交易记录不存在'})
        if 'ecode' in changes:
            trans.ecode = changes['ecode']
        trans.save()
        expense_updates = changes.get('expenses', [])
        for upd in expense_updates:
            ditem = upd.get('ditem', '')
            if not ditem:
                continue
            exp = Expense.objects.filter(company=company, transuuid=trans, exptxserno=exptxserno, ditem=ditem).first()
            if not exp:
                continue
            if 'pmcode' in upd:
                exp.pmcode = upd['pmcode']
            if 'asscode1' in upd:
                exp.asscode1 = upd['asscode1']
            if 'asscode2' in upd:
                exp.asscode2 = upd['asscode2']
            exp.save()
        payment_updates = changes.get('payments', [])
        for pc in payment_updates:
            old_pcode = pc.get('old_pcode', '')
            new_pcode = pc.get('new_pcode', '')
            if old_pcode and new_pcode and old_pcode != new_pcode:
                Toll.objects.filter(company=company, transuuid=trans, pcode=old_pcode).update(pcode=new_pcode)

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


def get_receipt(request):
    '''获取已完成交易的消费单数据（按客人+日期聚合所有已结账记录）'''
    company = request.GET.get('company', '')
    hunguuid = request.GET.get('hunguuid', '')
    if not company or not hunguuid:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'})
    try:
        
# 选品接口从 adviser 重导出（保持 cashier URL 不变）

        uuid_obj = _parse_uuid_loose(hunguuid)
        source_hung = ExpvstollHung.objects.get(
            Q(uuid=uuid_obj) | Q(exptxserno_hung=hunguuid),
            company=company, flag='Y'
        )
        vipuuid_id = source_hung.vipuuid_id
        vsdate = source_hung.vsdate_hung or ''
        # 获取会员信息
        vip_name = ''
        vip_code = ''
        if vipuuid_id:
            try:
                vip = Vip.objects.get(uuid=vipuuid_id)
                vip_name = vip.vname or ''
                vip_code = vip.vcode or ''
            except Vip.DoesNotExist:
                pass
        # 按客人+日期查找所有已结账的挂单
        all_hungs = list(ExpvstollHung.objects.filter(
            company=company, flag='Y', valiflag_hung='Y',
            psstatus_hung='70',
            vipuuid=vipuuid_id,
            vsdate_hung=vsdate,
        ).order_by('exptxserno_hung'))
        if not all_hungs:
            all_hungs = [source_hung]
        # 批量查询所有关联的员工信息
        all_trans = []
        for hung in all_hungs:
            trans = Expvstoll.objects.filter(
                company=company, hungserno=hung.exptxserno_hung
            ).first()
            if trans:
                all_trans.append((hung, trans))
        # 一次性收集所有员工编码
        all_emp_codes = set()
        for hung, trans in all_trans:
            exps = Expense.objects.filter(company=company, transuuid=trans.uuid).only(
                'pmcode', 'asscode1', 'asscode2')
            for ex in exps:
                if ex.pmcode: all_emp_codes.add(ex.pmcode)
                if ex.asscode1: all_emp_codes.add(ex.asscode1)
                if ex.asscode2: all_emp_codes.add(ex.asscode2)
        emp_map = {}
        if all_emp_codes:
            for em in Empl.objects.filter(company=company, ecode__in=list(all_emp_codes)).only('ecode', 'ename'):
                emp_map[em.ecode] = em.ename
        # 处理每个挂单
        orders = []
        all_items = []
        payments = []
        total = 0
        all_ccodes = set()
        for hung, trans in all_trans:
            order_items = []
            expenses = Expense.objects.filter(company=company, transuuid=trans.uuid).order_by('ditem')
            for ex in expenses:
                item_name = _resolve_hung_itemname(company, ex.ttype or '', ex.srvcode or '')
                raw_stype = (ex.stype or 'N').strip().upper()
                stype_name = '赠送' if raw_stype == 'P' else '正常'
                emp_parts = []
                if ex.pmcode and ex.pmcode in emp_map:
                    emp_parts.append(emp_map[ex.pmcode])
                if ex.asscode1 and ex.asscode1 in emp_map:
                    emp_parts.append(emp_map[ex.asscode1])
                if ex.asscode2 and ex.asscode2 in emp_map:
                    emp_parts.append(emp_map[ex.asscode2])
                amt = float(ex.s_mount or 0)
                if ex.otherserno:
                    all_ccodes.add(ex.otherserno)
                    # 统计卡充值/售卡金额
                    if ex.ttype in ('C', 'I'):
                        c = ex.otherserno
                        if c not in card_added:
                            card_added[c] = {'qty': 0.0, 'amount': 0.0}
                        card_added[c]['amount'] += float(ex.s_mount or 0)
                        card_added[c]['qty'] += float(ex.s_qty or 0)
                item_dict = {
                    'name': item_name or ex.srvcode or '',
                    'qty': float(ex.s_qty or 0),
                    'price': float(ex.s_price or 0),
                    'amount': amt,
                    'ttypename': _hung_line_ttypename(ex.ttype or ''),
                    'stype': stype_name,
                    'stypeabbr': '赠' if raw_stype == 'P' else '',
                    'empName': ', '.join(emp_parts),
                }
                order_items.append(item_dict)
                all_items.append(item_dict)
            orders.append({
                'serno': hung.exptxserno_hung or '',
                'items': order_items,
            })
            # 付款方式
            tolls = Toll.objects.filter(company=company, transuuid=trans.uuid).order_by('pcode')
            for tl in tolls:
                if tl.ccode:
                    all_ccodes.add(tl.ccode)
                pcode = (tl.pcode or '').strip()
                if pcode:
                    try:
                        pm = Paymode.objects.get(company=company, flag='Y', pcode=pcode)
                        pname = pm.pname or pcode
                    except Paymode.DoesNotExist:
                        pname = pcode
                else:
                    ccode = (tl.ccode or '').strip()
                    if ccode:
                        try:
                            ci = Cardinfo.objects.filter(company=company, ccode=ccode, flag='Y').select_related('cardtypeuuid').first()
                            if ci and ci.cardtypeuuid:
                                pname = ci.cardtypeuuid.cardname or '卡付'
                            else:
                                pname = '卡付'
                        except Exception:
                            pname = '卡付'
                    else:
                        raw = (tl.pcode or '').strip()
                        pname = raw if raw else '卡付（未指定）'
                amt = float(tl.totmount or 0)
                payments.append({'method': pname, 'amount': amt})
                total += amt
        # 金额校验：项目合计 vs 付款合计
        item_total = sum(it['amount'] for it in all_items)
        if payments and abs(item_total - total) > 0.01:
            diff = round(total - item_total, 2)
            diff_item = {
                'name': '（充值/售卡）',
                'qty': 1,
                'price': diff,
                'amount': diff,
                'stype': '正常', 'stypeabbr': '', 'empName': '',
            }
            if orders:
                orders[-1]['items'].append(diff_item)
            all_items.append(diff_item)
        if not payments:
            total = float(source_hung.totmount_hung or 0)
        # 统计各卡本次消费量（从 Toll 取，用 ccode 关联卡号）
        card_added = {}
        card_consumed = {}
        if trans:
            for tl in tolls:
                ccode = (tl.ccode or '').strip()
                if not ccode:
                    continue
                if ccode not in card_consumed:
                    card_consumed[ccode] = {'qty': 0.0, 'amount': 0.0}
                card_consumed[ccode]['amount'] += float(tl.totmount or 0)
                card_consumed[ccode]['qty'] += float(tl.qty or 0)
        # 卡余额
        cards = []
        for ccode in all_ccodes:
            if not ccode: continue
            try:
                ci = Cardinfo.objects.filter(company=company, ccode=ccode, flag='Y').select_related('cardtypeuuid').first()
                if ci:
                    ct = ci.cardtypeuuid
                    consumed = card_consumed.get(ccode, {'qty': 0.0, 'amount': 0.0})
                    added = card_added.get(ccode, {'qty': 0.0, 'amount': 0.0})
                    cards.append({
                        'ccode': ccode,
                        'cardname': ct.cardname if ct else '',
                        'comptype': ct.comptype if ct else 'amount',
                        'leftmoney': float(ci.leftmoney or 0),
                        'leftqty': float(ci.leftqty or 0),
                        'consumed_qty': consumed['qty'],
                        'consumed_amount': consumed['amount'],
                        'added_qty': added['qty'],
                        'added_amount': added['amount'],
                    })
            except Exception:
                pass
        cashier_name = source_hung.ecode_hung or ''
        return JsonResponse({
            'ok': True,
            'vipName': vip_name,
            'vipCode': vip_code,
            'date': (vsdate or '')[:8] if vsdate else '',
            'orders': orders,
            'cards': cards,
            'payments': payments,
            'total': total,
            'cashierName': cashier_name,
            'cashierCode': cashier_name,
        })
    except ExpvstollHung.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '挂单不存在'})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


@csrf_exempt
def shift_handover(request):
    """交班：标记班次号并生成付款汇总"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    company = data.get('company', '')
    storecode = data.get('storecode', '')
    if not company:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        qs = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            cdate__isnull=True,
        )
        if not qs.exists():
            return JsonResponse({'ok': False, 'message': '没有待交班的单据'})
        minvsdate = qs.aggregate(m=Min('vsdate'))['m']
        max_t = qs.aggregate(m=Max('times'))['m']
        t = int(max_t) if max_t else 0
        new_times = str(t + 1)
        qs.filter(vsdate__gte=minvsdate, times__isnull=True).update(times=new_times)
        shift_qs = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            vsdate__gte=minvsdate, times=new_times,
        )
        order_uuids = list(shift_qs.values_list('uuid', flat=True))

        tolls = Toll.objects.filter(company=company, transuuid__in=order_uuids)
        payment_summary = {}
        for tl in tolls:
            pc = tl.pcode or ''
            if pc not in payment_summary:
                pm = Paymode.objects.filter(company=company, pcode=pc).values_list('pname', flat=True).first()
                payment_summary[pc] = {'name': pm or pc, 'total': 0.0, 'count': 0}
            payment_summary[pc]['total'] += float(tl.totmount or 0)
            payment_summary[pc]['count'] += 1

        total_amount = float(shift_qs.aggregate(s=Sum('totmount'))['s'] or 0)

        details = []
        for exp in shift_qs:
            tl_list = Toll.objects.filter(company=company, transuuid=exp.uuid)
            payments = []
            for tl in tl_list:
                pm = Paymode.objects.filter(company=company, pcode=tl.pcode).values_list('pname', flat=True).first()
                payments.append({'pcode': tl.pcode or '', 'name': pm or tl.pcode or '', 'amount': float(tl.totmount or 0)})
            details.append({
                'exptxserno': exp.exptxserno or '',
                'vsdate': exp.vsdate or '',
                'totmount': float(exp.totmount or 0),
                'payments': payments,
            })

        return JsonResponse({
            'ok': True,
            'shift_no': int(new_times),
            'minvsdate': minvsdate,
            'order_count': shift_qs.count(),
            'total_amount': total_amount,
            'payment_summary': payment_summary,
            'details': details,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


def payment_report(request):
    """按日期范围查询各付款方式的交易明细汇总"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if not company or not date_from or not date_to:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        exps = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            vsdate__gte=date_from, vsdate__lte=date_to,
        )
        tolls = Toll.objects.filter(company=company, transuuid__in=exps.values('uuid'))
        pm_names = {}
        for pm in Paymode.objects.filter(company=company, flag='Y'):
            pm_names[pm.pcode] = pm.pname

        pmt_summary = {}
        for tl in tolls:
            pc = tl.pcode or ''
            if pc not in pmt_summary:
                pmt_summary[pc] = {'name': pm_names.get(pc, pc), 'total': 0.0, 'count': 0, 'orders': []}
            pmt_summary[pc]['total'] += float(tl.totmount or 0)
            pmt_summary[pc]['count'] += 1

        exp_map = {str(e.uuid): e for e in exps}
        for pc, info in pmt_summary.items():
            orders = []
            for exp_uuid, exp in exp_map.items():
                tls = [tl for tl in tolls if str(tl.transuuid_id) == exp_uuid and tl.pcode == pc]
                for tl in tls:
                    orders.append({
                        'exptxserno': exp.exptxserno or '',
                        'vsdate': exp.vsdate or '',
                        'totmount': float(exp.totmount or 0),
                        'payment_amount': float(tl.totmount or 0),
                    })
            info['orders'] = orders

        return JsonResponse({
            'ok': True,
            'order_count': exps.count(),
            'total_amount': float(exps.aggregate(Sum('totmount'))['s'] or 0),
            'payment_summary': pmt_summary,
            'date_from': date_from,
            'date_to': date_to,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


@csrf_exempt
def daily_settlement(request):
    """日结：标记指定 vsdate 的所有单据为已日结，生成汇总。preview=1 只预览不执行"""
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'ok': False, 'message': '仅支持 GET/POST'})
    if request.method == 'GET':
        data = request.GET.dict()
    else:
        try:
            data = json.loads(request.body)
        except:
            data = request.POST.dict()
    company = data.get('company', '')
    storecode = data.get('storecode', '')
    preview = data.get('preview', '') in ('1', 'true')
    if not company:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        qs = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            cdate__isnull=True,
        )
        if not qs.exists():
            return JsonResponse({'ok': False, 'message': '没有待日结的单据', 'has_pending': False})
        minvsdate = qs.aggregate(m=Min('vsdate'))['m']
        day_qs = qs.filter(vsdate__gte=minvsdate)
        order_count = day_qs.count()
        total_amount = float(day_qs.aggregate(s=Sum('totmount'))['s'] or 0)

        if preview:
            return JsonResponse({
                'ok': True, 'has_pending': True, 'preview': True,
                'business_date': minvsdate, 'order_count': order_count, 'total_amount': total_amount,
            })

        now = datetime.now()
        settle_date = minvsdate
        day_qs.update(cdate=settle_date)

        order_uuids = list(day_qs.values_list('uuid', flat=True))
        tolls = Toll.objects.filter(company=company, transuuid__in=order_uuids)

        payment_summary = {}
        for tl in tolls:
            pc = tl.pcode or ''
            if pc not in payment_summary:
                pm = Paymode.objects.filter(company=company, pcode=pc).values_list('pname', flat=True).first()
                payment_summary[pc] = {'name': pm or pc, 'total': 0.0, 'count': 0}
            payment_summary[pc]['total'] += float(tl.totmount or 0)
            payment_summary[pc]['count'] += 1

        pm_map = {}
        for tl in tolls:
            if tl.pcode and tl.pcode not in pm_map:
                name = Paymode.objects.filter(company=company, pcode=tl.pcode).values_list('pname', flat=True).first()
                pm_map[tl.pcode] = name or tl.pcode

        from collections import defaultdict
        toll_by_exp = defaultdict(list)
        for tl in tolls:
            toll_by_exp[str(tl.transuuid_id)].append(tl)

        shift_summary = {}
        for exp in day_qs:
            sk = exp.times or '0'
            if sk not in shift_summary:
                shift_summary[sk] = {'count': 0, 'total': 0.0, 'payment_summary': {}}
            shift_summary[sk]['count'] += 1
            shift_summary[sk]['total'] += float(exp.totmount or 0)

            for tl in toll_by_exp.get(str(exp.uuid), []):
                pc = tl.pcode or ''
                if pc not in shift_summary[sk]['payment_summary']:
                    shift_summary[sk]['payment_summary'][pc] = {'name': pm_map.get(pc, pc), 'total': 0.0, 'count': 0}
                shift_summary[sk]['payment_summary'][pc]['total'] += float(tl.totmount or 0)
                shift_summary[sk]['payment_summary'][pc]['count'] += 1
        return JsonResponse({
            'ok': True,
            'settle_date': settle_date,
            'business_date': minvsdate,
            'order_count': order_count,
            'total_amount': total_amount,
            'shift_summary': shift_summary,
            'payment_summary': payment_summary,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e), 'has_pending': False})


@csrf_exempt
def settlement_history(request):
    """获取所有已日结的日期列表"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    if not company:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        dates = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            cdate__isnull=False,
        ).values_list('cdate', flat=True).distinct().order_by('-cdate')
        return JsonResponse({'ok': True, 'dates': list(dates)})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


@csrf_exempt
def settlement_detail(request):
    """获取指定日结日期的完整汇总"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    cdate = request.GET.get('cdate', '')
    if not company or not cdate:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        qs = Expvstoll.objects.filter(
            company=company, storecode=storecode,
            flag='Y', valiflag='Y',
            cdate=cdate,
        )
        if not qs.exists():
            return JsonResponse({'ok': False, 'message': '未找到记录'})
        total = float(qs.aggregate(s=Sum('totmount'))['s'] or 0)
        order_count = qs.count()
        order_uuids = list(qs.values_list('uuid', flat=True))
        tolls = Toll.objects.filter(company=company, transuuid__in=order_uuids)

        pm_map = {}
        for tl in tolls:
            if tl.pcode and tl.pcode not in pm_map:
                name = Paymode.objects.filter(company=company, pcode=tl.pcode).values_list('pname', flat=True).first()
                pm_map[tl.pcode] = name or tl.pcode

        payment_summary = {}
        for tl in tolls:
            pc = tl.pcode or ''
            if pc not in payment_summary:
                payment_summary[pc] = {'name': pm_map.get(pc, pc), 'total': 0.0, 'count': 0}
            payment_summary[pc]['total'] += float(tl.totmount or 0)
            payment_summary[pc]['count'] += 1

        from collections import defaultdict
        toll_by_exp = defaultdict(list)
        for tl in tolls:
            toll_by_exp[str(tl.transuuid_id)].append(tl)

        shift_summary = {}
        for exp in qs:
            sk = exp.times or '0'
            if sk not in shift_summary:
                shift_summary[sk] = {'count': 0, 'total': 0.0, 'payment_summary': {}}
            shift_summary[sk]['count'] += 1
            shift_summary[sk]['total'] += float(exp.totmount or 0)
            for tl in toll_by_exp.get(str(exp.uuid), []):
                pc = tl.pcode or ''
                if pc not in shift_summary[sk]['payment_summary']:
                    shift_summary[sk]['payment_summary'][pc] = {'name': pm_map.get(pc, pc), 'total': 0.0, 'count': 0}
                shift_summary[sk]['payment_summary'][pc]['total'] += float(tl.totmount or 0)
                shift_summary[sk]['payment_summary'][pc]['count'] += 1

        return JsonResponse({
            'ok': True,
            'cdate': cdate,
            'order_count': order_count,
            'total_amount': total,
            'shift_summary': shift_summary,
            'payment_summary': payment_summary,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})


@csrf_exempt
def get_order_payment(request):
    """获取指定已结账单据的付款方式信息"""
    company = request.GET.get('company', '')
    exptxserno = request.GET.get('exptxserno', '')
    if not company or not exptxserno:
        return JsonResponse({'ok': False, 'payments': []})
    try:
        trans = Expvstoll.objects.filter(company=company, hungserno=exptxserno).first()
        if not trans:
            trans = Expvstoll.objects.filter(company=company, exptxserno=exptxserno).first()
        if not trans:
            return JsonResponse({'ok': False, 'payments': []})
        tolls = Toll.objects.filter(company=company, transuuid=trans.uuid)
        payments = []
        for tl in tolls:
            pm = Paymode.objects.filter(company=company, pcode=tl.pcode).values_list('pname', flat=True).first()
            payments.append({'pcode': tl.pcode or '', 'name': pm or tl.pcode or '', 'amount': float(tl.totmount or 0)})
        return JsonResponse({'ok': True, 'payments': payments})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e), 'payments': []})


@csrf_exempt
def search_by_payment(request):
    """按付款方式查询已结账交易记录"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    pcode = request.GET.get('pcode', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if not company or not pcode:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        tolls = Toll.objects.filter(company=company, pcode=pcode)
        if not tolls.exists():
            return JsonResponse({'ok': True, 'orders': [], 'total_amount': 0, 'order_count': 0})
        uuids = list(tolls.values_list('transuuid', flat=True).distinct())
        qs = Expvstoll.objects.filter(company=company, storecode=storecode, uuid__in=uuids, flag='Y', valiflag='Y')
        if date_from:
            qs = qs.filter(vsdate__gte=date_from)
        if date_to:
            qs = qs.filter(vsdate__lte=date_to)
        qs = qs.order_by('-vsdate', '-exptxserno')[:100]

        pm = Paymode.objects.filter(company=company, pcode=pcode).values_list('pname', flat=True).first()
        pname = pm or pcode

        toll_by_exp = {}
        for tl in Toll.objects.filter(company=company, pcode=pcode, transuuid__in=[e.uuid for e in qs]):
            key = str(tl.transuuid_id)
            toll_by_exp[key] = float(tl.totmount or 0)

        orders = []
        total_amount = 0.0
        for exp in qs:
            pmt_amt = toll_by_exp.get(str(exp.uuid), 0.0)
            vname = ''
            if exp.vipuuid_id:
                try:
                    v = Vip.objects.get(uuid=exp.vipuuid_id)
                    vname = v.vname or ''
                except:
                    pass
            orders.append({
                'exptxserno': exp.exptxserno or '',
                'vsdate': exp.vsdate or '',
                'vcode': exp.vcode or '',
                'vname': vname,
                'totmount': float(exp.totmount or 0),
                'payment_method': pname,
                'payment_amount': pmt_amt,
            })
            total_amount += pmt_amt

        return JsonResponse({
            'ok': True,
            'orders': orders,
            'total_amount': total_amount,
            'order_count': len(orders),
            'payment_name': pname,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})
