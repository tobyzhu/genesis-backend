#coding = utf-8
from django.db import transaction
from django.shortcuts import render
from datetime import datetime,timedelta
import json
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from decimal import *
import requests

from .models import Expvstoll,Expense,Toll,Cardhistory,EmplArchivementDetail,VipItemInfo,VipItemTransHead,VipItemTransDetail,VipItemTranslog
from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode,Vip,Cardsupertype
from adviser.models import Cardinfo,ExpvstollHung,ExpenseHung

from common.models import Sequence

from .emplarch_yfy import EMPL_ARCHEMENT_BYMONTH_YFY
from .emplarch_yfy import set_exp_basenum_yfy_01,set_exp_xamount_yfy_01,set_exp_basenum_yfy_55,set_exp_xamount_yfy_02,set_exp_xamount_yfy_03,set_exp_xamount_yfy_04,set_exp_xamount_yfy_05

from adviser.views import sql_to_json
import common.constants
from .emplarch_yiren import cal_emplarchivement_yiren,process_pertrans_yiren,EmplArchivement
from .emplarch_yfy import process_pertrans_yfy

# from common.views import getserno

# Create your views here.

def getserno(company,storecode, tablecode):
    try:
        sequence = Sequence.objects.get(company=company, storecode=storecode, tablecode=tablecode)
    except:
        sequence = Sequence.objects.create(company=company, storecode=storecode, tablecode=tablecode, sequence=0)
    print('sequence', sequence)
    sequence.sequence = sequence.sequence + 1
    sequence.save()

    return company  + storecode +'_'+ tablecode+'_' + str(sequence.sequence)

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
        transitems = Expense.objects.filter(transuuid=trans)
        print('len(transitems)',len(transitems))
        for transitem in transitems:
            print('transitm',transitem.exptxserno,transitem.ditem,transitem.srvcode)
            # 设置商品邮寄单信息   vipiteminfo, vipitemtranslog
            if transitem.ttype =='G':
                transitem.set_deposite()


    if company=='yiren':
        process_pertrans_yiren(company, storecode,txserno,transuuid)

    if company=='yfy':
        print('process_pertrans_yfy')
        process_pertrans_yfy(company, storecode,txserno,transuuid)

    return HttpResponse('OK', content_type="application/json")

class hung_to_trans(object):
    def __init__(self,**kwargs):
        self.company=kwargs.get('company','demo')
        self.storecode = kwargs.get('storecode','88')
        self.hungserno = kwargs.get('hungserno','')
        self.paydetails = kwargs.get('paydetails','')
        self.hunguuid = kwargs.get('hunguuid','')
        self.cashier = kwargs.get('cashier','admin')

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
                    if self.paycardinfo.cardtypeuuid.stype =='N':
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
        self.exptxserno = getserno(self.company, self.storecode, 'EXPVSTOLL')
        print('self.exptxsenro', self.exptxserno)
        self.expvstoll.exptxserno = self.exptxserno

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
            self.expvstoll.hungserno = self.hung.exptxserno_hung
            self.expvstoll.ttype = self.hung.ttype_hung
            self.expvstoll.normalflag ='Y'
            self.expvstoll.bookingeventid = self.hung.bookingeventid
            self.expvstoll.terminalid = self.hung.terminalid
            # self.expvstoll.save()

            self.tx_qty = 0
            self.tx_amount = 0
            hungitems = ExpenseHung.objects.filter(flag='Y',company=self.company,storecode=self.storecode,exptxserno_hung=self.hung.exptxserno_hung)
            item =0
            self.expenses=[]
            self.transcards=[]
            for hungitem in hungitems:
                item =item +1
                # ditem ='000'+item.__str__()
                expense = Expense.objects.get_or_create(flag='Y',company=self.company,storecode=self.storecode,transuuid=self.expvstoll,ditem=hungitem.ditem_hung)[0]
                # expense.exptxserno = self.exptxserno
                expense.ttype = hungitem.ttype_hung
                # expense.ditem = ditem
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

                print('expense.ditem',expense.ditem)

                if hungitem.ttype_hung == 'C':
                    # transcard = self.newcards.get(ccode=hungitem.srvcode_hung)
                    transcard = Cardinfo.objects.filter(flag='Y', company=self.company,
                                                            vipuuid=self.vip,ccode=hungitem.srvcode_hung)[0]
                    transcard.status='O'
                    self.transcards.append(transcard)
                    # transcard.save()
                    print('transcard.status',transcard.status)

                if hungitem.ttype_hung =='I':
                    transcard = Cardinfo.objects.filter(flag='Y', company=self.company,
                                                            vipuuid=self.vip,ccode=hungitem.srvcode_hung)[0]
                    if transcard.cardtypeuuid.comptype =='times':
                        transcard.leftqty = transcard.leftqty + hungitem.s_qty_hung

                    transcard.leftmoney= transcard.leftmoney + hungitem.addvamoney_hung
                    self.transcards.append(transcard)
                    # transcard.save()
                    print('transcard.leftmoney',transcard.leftmoney)

                self.tx_qty = self.tx_qty + hungitem.s_qty_hung
                self.tx_amount = self.tx_amount + hungitem.s_mount_hung

                self.expenses.append(expense)


                # expense.save()

            self.set_tol
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

        self.expvstoll = Expvstoll.objects.get_or_create(company=self.expvstollhung.company,storecode=self.expvstollhung.storecode,
                                               vcode=self.expvstollhung.vcode_hung,ccode=self.expvstollhung.ccode_hung,cardtype=self.expvstollhung.cardtype_hung,vipuuid=self.expvstollhung.vipuuid,
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