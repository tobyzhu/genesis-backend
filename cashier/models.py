from django.db import models
from django.db.models import Sum,Avg,Count
import uuid
import datetime
from decimal import *

# Create your models here.
from common.constants import FLAG, SALESFLAG, COMPTYPE, TTYPE,STYPE,SCHEDULELIST,ARCHIVEMENTTYPE, GenesisModel,COMPANYID
from common.constants import StoreCommonBaseModel
import common
from common.views import getserno

from baseinfo.models import Appoption,Empl,Serviece,Goods,Cardtype,Paymode,Vip,Storeinfo,Cardsupertype,BankAccount
from adviser.models import Cardinfo,ExpenseHung,ExpvstollHung
from goods.models import *
# from cashier.emplarch_yfy import set_transitem_basenum_yfy,set_transitem_xamount_yfy_01,set_transitem_xamount_yfy_02,set_transitem_xamount_yfy_03,set_transitem_xamount_yfy_04,set_transitem_xamount_yfy_05
import baseinfo.models


class Discic(GenesisModel):
    # sukid = models.BigIntegerField(primary_key=True)
    vsdate = models.CharField(max_length=8, blank=True, null=True)
    vstime = models.CharField(max_length=8, blank=True, null=True)
    cardno = models.CharField(max_length=40, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    exptxserno = models.CharField(max_length=40)
    casher = models.CharField(max_length=10, blank=True, null=True)
    note = models.CharField(max_length=10, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'discic'

class Cardpayout(models.Model):
    payout_ukid = models.CharField(primary_key=True, max_length=40)
    cardownareacode = models.CharField(max_length=8)
    cardowncompany = models.CharField(max_length=16, blank=True, null=True)
    cardownstore = models.CharField(max_length=16)
    cardexpcompany = models.CharField(max_length=8, blank=True, null=True)
    cardexpstore = models.CharField(max_length=16)
    cardno = models.CharField(max_length=40)
    exptxserno = models.CharField(max_length=40)
    cardtype = models.CharField(max_length=8, blank=True, null=True)
    moneytype = models.CharField(max_length=8)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    vdate = models.CharField(max_length=8, blank=True, null=True)
    vtime = models.CharField(max_length=8, blank=True, null=True)
    vcode = models.CharField(max_length=16, blank=True, null=True)
    vname = models.CharField(max_length=32, blank=True, null=True)
    pcode = models.CharField(max_length=16, blank=True, null=True)
    pname = models.CharField(max_length=32, blank=True, null=True)
    casher = models.CharField(max_length=16, blank=True, null=True)
    cashername = models.CharField(max_length=32, blank=True, null=True)
    vflag = models.CharField(max_length=1, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)
    ttype = models.CharField(max_length=8, blank=True, null=True)
    srvcode = models.CharField(max_length=40, blank=True, null=True)
    srvname = models.CharField(max_length=64, blank=True, null=True)
    leftmoney = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cardpayout'

class Cpayatout(models.Model):
    ukid = models.CharField(primary_key=True, max_length=40)
    cardownstore = models.CharField(max_length=10)
    cardexpstore = models.CharField(max_length=10)
    cardno = models.CharField(max_length=40)
    exptxserno = models.CharField(max_length=40)
    cardtype = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    vdate = models.CharField(max_length=8, blank=True, null=True)
    vtime = models.CharField(max_length=8, blank=True, null=True)
    vcode = models.CharField(max_length=40, blank=True, null=True)
    vname = models.CharField(max_length=40, blank=True, null=True)
    pcode = models.CharField(max_length=10, blank=True, null=True)
    pname = models.CharField(max_length=10, blank=True, null=True)
    casher = models.CharField(max_length=10, blank=True, null=True)
    cashername = models.CharField(max_length=10, blank=True, null=True)
    vflag = models.CharField(max_length=1, blank=True, null=True)
    note = models.CharField(max_length=100, blank=True, null=True)
    updateflag = models.CharField(max_length=1, blank=True, null=True)
    ttype = models.CharField(max_length=8, blank=True, null=True)
    srvcode = models.CharField(max_length=40, blank=True, null=True)
    srvname = models.CharField(max_length=64, blank=True, null=True)
    leftmoney = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cpayatout'

class Sequence(GenesisModel):
    sequence = models.DecimalField(db_column='SEQUENCE', max_digits=20, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    tablecode = models.CharField(db_column='TABLECODE',  max_length=40)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sequence'

class Expvstoll(GenesisModel):
    ccode = models.CharField(max_length=40, blank=True, null=True)
    vcode = models.CharField(max_length=40, blank=True, null=True)
    sumdisc = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    mondisc = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    totmount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    times = models.CharField(max_length=1, blank=True, null=True)
    cdate = models.CharField(max_length=8, blank=True, null=True)
    mnote = models.CharField(max_length=100, blank=True, null=True)
    cardtype = models.CharField(max_length=16, blank=True, null=True)
    exptxserno = models.CharField(max_length=40 , blank=True,null=True)
    vsdate = models.CharField(max_length=8, blank=True, null=True)
    vstime = models.CharField(max_length=8, blank=True, null=True)
    ecode = models.CharField(max_length=10, blank=True, null=True)
    valiflag = models.CharField(max_length=1, blank=True, null=True)
    ttype = models.CharField(max_length=8, blank=True, null=True)
    point = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oldcustflag = models.CharField(max_length=16, blank=True, null=True)
    goodssaletype = models.CharField(max_length=10, blank=True, null=True)
    doccode = models.CharField(max_length=40, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    roomid = models.CharField(max_length=40, blank=True, null=True)
    totalmins = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    startdate = models.CharField(max_length=8, blank=True, null=True)
    starttime = models.CharField(max_length=8, blank=True, null=True)
    enddate = models.CharField(max_length=8, blank=True, null=True)
    endtime = models.CharField(max_length=8, blank=True, null=True)
    vipcode = models.CharField(max_length=16, blank=True, null=True)
    cardleftmoney = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flag1 = models.CharField(max_length=8, blank=True, null=True)
    flag2 = models.CharField(max_length=8, blank=True, null=True)
    flag3 = models.CharField(max_length=8, blank=True, null=True)
    comeinid = models.CharField(max_length=32, blank=True, null=True)
    incard = models.CharField(max_length=8, blank=True, null=True)
    nextecode = models.CharField(max_length=16, blank=True, null=True)
    pmcode = models.CharField(max_length=16, blank=True, null=True)
    icleftmoney = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    normalflag = models.CharField(max_length=16, blank=True, null=True)
    asscode1 = models.CharField(max_length=40, blank=True, null=True)
    asscode2 = models.CharField(max_length=40, blank=True, null=True)
    passedby = models.CharField(max_length=8, blank=True, null=True,verbose_name='审核人')
    storecode = models.CharField(max_length=8, blank=True, null=True)
    cashposition = models.CharField(max_length=8, blank=True, null=True)
    srvcost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True )
    status = models.CharField(max_length=8, blank=True, null=True,verbose_name='单据状态')
    bookingeventid = models.BigIntegerField(blank=True, null=True)
    promotionsid = models.CharField(max_length=16, blank=True, null=True)
    hungserno = models.CharField(max_length=40, blank=True,null=True)
    ttype1 = models.CharField(max_length=8, blank=True, null=True)
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')

    class Meta:
        managed = True
        db_table = 'expvstoll'

    def set_oldcustflag(self):
        print('self vipuuid',self.vipuuid.uuid,self.vipuuid.create_time.strftime('%Y%m%d'))
        print('2',self.create_time.strftime('%Y%m%d') )
        # vip = Vip.objects.get(uuid=self.vipuuid.uuid)
        # print('vip vname',vip.vname)
        # with Vip.objects.get(uuid=self.vipuuid) as vip:
        if self.create_time.strftime('%Y%m%d')==self.vipuuid.create_time.strftime('%Y%m%d'):
            self.oldcustflag='1'
            self.save()
            return 1

    def set_paymoderatio(self):

        pcodes = Toll.objects.filter(company=self.company).filter(transuuid=self.uuid)
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
            try:
                p = Paymode.objects.get(company=self.company, flag='Y', pcode=pcode.pcode)
            except:
                p = Paymode.objects.get(company=self.company, flag='Y', pcode='A')
                cardratio=0
                cashratio=0
                sendratio=0
                otherratio=0

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

        transitems = Expense.objects.filter(company=self.company,transuuid=self.uuid)
        for transitem in transitems:
            transitem.cashratio=cashratio
            transitem.cardratio=cardratio
            transitem.sendratio=sendratio
            transitem.otherratio=otherratio

            if transitem.s_mount == None:
                transitem.s_mount = 0
            if transitem.pmcode == None:
                transitem.pmcode = ''

            if transitem.asscode1 == None:
                transitem.asscode1 = ''
            if transitem.asscode2 == None:
                transitem.asscode2 = ''
            if transitem.s_qty == None:
                transitem.s_qty = 0

            transitem.save()

        return 0

    def set_cardhistory(self):
        print('self.ccode',self.company, self.ccode)
        if len(self.ccode) >0 :
            paycardinfo = Cardinfo.objects.get(company=self.company,flag='Y',ccode=self.ccode)
            print('paycardinfo',paycardinfo.ccode,paycardinfo.cardtype,paycardinfo.cardtypeuuid.cardname)
            defaultpaycode = paycardinfo.cardtypeuuid.defaultpaycode
            try:
                tollitem = Toll.objects.get(company=self.company,transuuid=self.uuid,pcode=defaultpaycode)
                cardpayamount = tollitem.totmount
            except:
                cardpayamount = 0

            cardhistory = Cardhistory.objects.get_or_create(company=self.company,storecode=self.storecode,vsdate=self.vsdate,ccode=self.ccode,exptxserno=self.exptxserno)[0]
            cardhistory.create_time = self.create_time
            cardhistory.last_modified = self.last_modified
            cardhistory.outamount = cardpayamount
            cardhistory.vipuuid = self.vipuuid
            cardhistory.cardinfouuid = paycardinfo
            cardhistory.cardtypeuuid = paycardinfo.cardtypeuuid
            cardhistory.comptype = paycardinfo.cardtypeuuid.comptype
            cardhistory.suptype = paycardinfo.cardtypeuuid.suptype
            cardhistory.transuuid = self
            # cardhistory.creater = 'buding'
            cardhistory.save()
            cardhistory.recalamount()

        if self.ttype in ('C','I'):
            cards = Expense.objects.filter(company=self.company, storecode=self.storecode, flag='Y', transuuid = self.uuid,ttype__in=('C','I'))
            for card in cards:
                cardinfo = Cardinfo.objects.get(company=self.company,flag='Y',ccode=card.srvcode)
                cardhistory = Cardhistory.objects.get_or_create(company=self.company,storecode=self.storecode,vsdate=self.vsdate, ccode=card.srvcode,exptxserno=self.exptxserno)[0]
                cardhistory.create_time = self.create_time
                cardhistory.last_modified = self.last_modified
                cardhistory.inamount = card.addvamoney
                cardhistory.vipuuid = self.vipuuid
                cardhistory.cardinfouuid = cardinfo
                cardhistory.cardtypeuuid = cardinfo.cardtypeuuid
                cardhistory.comptype = cardinfo.cardtypeuuid.comptype
                cardhistory.suptype = cardinfo.cardtypeuuid.suptype
                cardhistory.transuuid = self
                # cardhistory.creater = 'buding'
                cardhistory.save()
                cardhistory.recalamount()

    def set_transgoodstranslog(self):
        if self.ttype in ('S','G'):
            items = Expense.objects.filter(company=self.company,flag='Y',transuuid=self.uuid)
            for item in items:
                item.set_goodstranslog()

    def set_vipiteminfo(self):
        if self.ttype in ('S','G'):
            items = Expense.objects.filter(company=self.company,flag='Y',transuuid=self.uuid).order_by('ditem')
            for item in items:
                # item.set_deposite()
                item.set_vipitemtrans()

class Expense(GenesisModel):
    ttype = models.CharField(db_column='TTYPE', max_length=8, blank=True, null=True)  # Field name made lowercase.
    secdisc = models.DecimalField(db_column='SECDISC', max_digits=10, decimal_places=6, blank=True, null=True)  # Field name made lowercase.
    pmcode = models.CharField(db_column='PMCODE', max_length=10, blank=True, null=True)  # Field name made lowercase.
    pmperc = models.DecimalField(db_column='PMPERC', max_digits=6, decimal_places=5, blank=True, null=True)  # Field name made lowercase.
    asscode1 = models.CharField(db_column='ASSCODE1', max_length=10, blank=True, null=True)  # Field name made lowercase.
    asscode2 = models.CharField(db_column='ASSCODE2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    dnote = models.CharField(db_column='DNOTE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    exptxserno = models.CharField(max_length=40,blank=True,null=True,db_column='EXPTXSERNO')  # Field name made lowercase.
    ditem = models.CharField(db_column='DITEM', max_length=4)  # Field name made lowercase.
    s_price = models.DecimalField(db_column='S_PRICE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    s_qty = models.DecimalField(db_column='S_QTY', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    s_mount = models.DecimalField(db_column='S_MOUNT', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    secperc = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    srvcode = models.CharField(max_length=40, blank=True, null=True)
    addvamoney = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    pmguideperc = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    secguideperc = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    thprec = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pmpoint = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    secpoint = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    thrpoint = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    cpoint = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pmamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    secamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    thramount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_basenum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_secbasenum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_thrbasenum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    thrguideperc = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    goodssaletype = models.CharField(max_length=1, blank=True, null=True)
    srvactmount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    srvmondisc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oldcustflag = models.CharField(max_length=8, blank=True, null=True)
    srvcost = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    srvcostperc = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    s_pricecurrency = models.CharField(max_length=8, blank=True, null=True)
    s_mountcurrency = models.CharField(max_length=8, blank=True, null=True)
    doccode = models.CharField(max_length=64, blank=True, null=True)
    stdmins = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percdisc = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    stype = models.CharField(max_length=8, blank=True, null=True)
    otherserno = models.CharField(max_length=40, blank=True, null=True)
    oldcardtype = models.CharField(max_length=16, blank=True, null=True)
    newcardtype = models.CharField(max_length=16, blank=True, null=True)
    secoldcustflag = models.CharField(max_length=8, blank=True, null=True)
    throldcustflag = models.CharField(max_length=8, blank=True, null=True)
    owegoodsflag = models.CharField(max_length=8, blank=True, null=True)
    sendway = models.CharField(max_length=8, blank=True, null=True)
    purchaseflag = models.CharField(max_length=8, blank=True, null=True)
    sendamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True)
    promotionsamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oriamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True)
    transuuid = models.ForeignKey(Expvstoll,db_column='transuuid',on_delete=models.DO_NOTHING,blank=True,null=True)
    cashratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    cardratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    sendratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    otherratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True)
    ctype = models.CharField(max_length=16,default='C',blank=True,null=True,verbose_name='项次类型')
    depositeflag = models.CharField(max_length=8, blank=True, null=True,verbose_name='是否存院')

    class Meta:
        managed = True
        db_table = 'expense'
        unique_together = ('company','storecode','exptxserno', 'ditem')

    def transitem_cardtype(self):
        if self.ttype in ('C','I'):
            cardtype=Cardinfo.objects.filter(company=common.constants.COMPANYID,ccode=self.srvcode).select_related('cardtypeuuid')
            print('cardtyp', cardtype)
            # cardtype = Cardtype.objects.get(company=common.constants.COMPANYID,cardtype=card.cardtype)
        else:
            return ''

    def set_trans_ratio(self):
        pcodes = Toll.objects.filter(company=self.company).filter(transuuid=self.uuid)
        cashamount = 0
        totalamount = 0
        cardamount = 0
        sendamount = 0
        otheramount = 0
        for pcode in pcodes:
            print('pcode=', pcode.pcode)
            if pcode.totmount == None:
                pcode.totmount = 0

            totalamount = totalamount + Decimal(pcode.totmount)
            p = Paymode.objects.get(company=self.company, flag='Y', pcode=pcode.pcode)
            print(p, p.iscash)
            if p.iscash == None:
                p.iscash = '9'

            if p.iscash == '3':
                otheramount = pcode.totmount + Decimal(otheramount)
            if p.iscash == '2':
                sendamount = pcode.totmount + Decimal(sendamount)
            if p.iscash == '1':
                cashamount = pcode.totmount + Decimal(cashamount)
            if p.iscash == '0':
                cardamount = pcode.totmount + Decimal(cardamount)

        if totalamount == 0:
            cashratio = 1
            cardratio = 1
            sendratio = 1
            otherratio = 1
        else:
            cashratio = Decimal(cashamount / totalamount)
            cardratio = Decimal(cardamount / totalamount)
            sendratio = Decimal(sendamount / totalamount)
            otherratio = Decimal(otheramount / totalamount)

        print('cardratio', cardratio, 'sendration=', sendratio, 'cashratio=', cashratio)
        self.cardratio=cardratio
        self.cashratio=cashratio
        self.sendratio=sendratio
        self.otherratio=otherratio
        self.save()
        return 0

    @property
    def cashamount(self):
        return self.s_mount*self.cashratio

    @property
    def cardamount(self):
        return self.s_mount*self.cardratio

    @property
    def sendamount(self):
        return self.s_mount*self.sendratio

    @property
    def item(self):
        if self.ttype == 'S':
            return Serviece.objects.get(company=self.company,svrcdoe=self.srvcode)
        if self.ttype == 'G':
            return Goods.objects.get(company=self.company,gcode=self.srvcode)
        if self.ttype == 'C':
            return Cardinfo.objects.get(company=self.company,ccode=self.srvcode)

    @property
    def cardqty(self):
        if self.ttype in ('C','I'):
            return self.s_qty
        else:
            return 0

    def set_owegoods(self):
        if self.ttype == 'G' and self.owegoodsflag == 'Y':
            print('owelist')
            owelist = Owelist.objects.get_or_create(company=self.company,storecode=self.storecode,sernotype='T',
                                                    owetranserno=self.exptxserno,ttype=self.ttype, stype=self.stype,
                                                    sgccode=self.srvcode,s_qty =self.s_qty,s_mount=self.s_mount,
                                                    vcode=self.transuuid.vcode,vipuuid=self.transuuid.vipuuid,owetype='1')

    def set_goodstranslog(self):
        if self.ttype == 'G':
            salewhcode = Storeinfo.objects.get(company=self.company,storecode=self.storecode,flag='Y').salewhcode
            goodstranslog = Goodstranslog.objects.get_or_create(company=self.company,companyid=self.company,storecode=self.storecode,whcode=salewhcode,
                                                                sukid=self.exptxserno,saleatr=self.ttype,seqbar=self.ditem,
                                                                vdate=self.transuuid.vsdate,gcode=self.srvcode)[0]
            goodstranslog.qty1 = self.s_qty
            goodstranslog.price1 = self.s_price
            goodstranslog.amount = self.s_mount
            goodstranslog.transuuid= self.transuuid.uuid
            goodstranslog.transdesc = self.transuuid.vipuuid.vname +'-' + self.transuuid.vipuuid.vcode
            goodstranslog.save()
            goodstranslog.set_qty2()
            goodstranslog.set_qty3()

        if self.ttype == 'S':
            usewhcode = Storeinfo.objects.get(company=self.company,storecode=self.storecode,flag='Y').usewhcode
            print('skip serviece use goodstranslog!')

    def set_deposite(self):
        if self.ttype == 'G':
            try:
                hung = ExpenseHung.objects.get(company=self.company,storecode=self.storecode,exptxserno_hung=self.transuuid.hungserno,ditem_hung=self.ditem)
                self.depositeflag = hung.depositeflag
                self.save()
                print('expense.depositeflag',self.depositeflag)
                # if hung.depositeflag == 'Y':
                if self.depositeflag == 'N':
                    vipgoodslog = Vgtranslog.objects.get_or_create(company=self.company,storecode=self.storecode,sukid=self.exptxserno,itemid=self.ditem,
                                                                   vsdate=self.transuuid.vsdate,vstime=self.transuuid.vstime,vcode=self.transuuid.vcode,
                                                                   gcode=self.srvcode,transtype='I',s_qty=self.s_qty,valiflag='Y',vipuuid=self.transuuid.vipuuid)[0]
                    vipgoodslog.save()

                # M: 存店，后续自取或者邮件
                # if hung.depositeflag == 'M':
                if self.depositeflag == 'M':
                    print('deposite info', self.company, self.storecode, self.exptxserno, self.transuuid.hungserno,self.ditem, self.srvcode)
                    vipiteminfo = VipItemInfo.objects.get_or_create(flag='Y',company=self.company, ttype=self.ttype,vip=self.transuuid.vipuuid,itemcode=self.srvcode)[0]
                    # vipiteminfo.price =self.s_price
                    vipitemtranslog = VipItemTranslog.objects.get_or_create(company=self.company,storecode=self.storecode, vip=self.transuuid.vipuuid,
                                                                            vipiteminfo=vipiteminfo,transitemuuid=self)[0]
                    vipitemtranslog.vcode =self.transuuid.vcode
                    vipitemtranslog.sukid =self.exptxserno
                    vipitemtranslog.ttype = self.ttype
                    vipitemtranslog.ditem = self.ditem
                    vipitemtranslog.itemcode = self.srvcode
                    vipitemtranslog.stype =self.stype
                    vipitemtranslog.transqty = self.s_qty
                    vipitemtranslog.price = self.s_price
                    vipitemtranslog.transamount = self.s_mount
                    vipitemtranslog.transtype ='G'
                    try:
                        vipitemtranslog.goodsuuid = Goods.objects.get(flag='Y', company=self.company, gcode=self.srvcode)
                    except Exception as e:
                        print('get vipitemtranslog.goodsuuid',e)
                        vipitemtranslog.goodsuuid=None
                    vipitemtranslog.save()
                    vipitemtranslog.set_leftqty()



                    if vipiteminfo.leftqty == None:
                        vipiteminfo.leftqty = 0
                    vipiteminfo.last_modified = datetime.datetime.now()
                    vipiteminfo.vcode = self.transuuid.vcode
                    vipiteminfo.comptype ='qty'
                    try:
                        vipiteminfo.goodsuuid = Goods.objects.get(flag='Y', company=self.company, gcode=self.srvcode)
                    except Exception as e:
                        print('vipiteminfo.goodsuuid', e)
                    vipiteminfo.valdate= '2099-12-31'
                    vipiteminfo.set_leftqty()
                    vipiteminfo.save()
            except Exception as e:
                print(self.exptxserno,self.ditem,' skipped',e)

        return 0

    def set_vipitemtrans(self):
        if self.ttype == 'G':
            if self.depositeflag == 'M':
                try:
                    print('deposite info', self.company, self.storecode, self.exptxserno, self.transuuid.hungserno,self.ditem, self.srvcode)
                    vipiteminfo = VipItemInfo.objects.get_or_create(flag='Y',company=self.company, ttype=self.ttype,vip=self.transuuid.vipuuid,itemcode=self.srvcode)[0]
                    try:
                        vipitemtranshead = VipItemTransHead.objects.get(flag='Y',company=self.company,storecode=self.storecode,vip=self.transuuid.vipuuid,transdate=datetime.datetime.today(),
                                                                              doccode=self.exptxserno,transtype='M')
                        if vipitemtranshead.status == None:
                            vipitemtranshead.status='10'
                    except:
                        vipitemtranshead = VipItemTransHead.objects.create(flag='Y',company=self.company,storecode=self.storecode,vip=self.transuuid.vipuuid,transdate=datetime.datetime.today(),
                                                                              doccode=self.exptxserno,transtype='M')
                        vipitemtranshead.status='10'

                    vipitemtransdetail = VipItemTransDetail.objects.get_or_create(flag='Y',company=self.company,storecode=self.storecode, vipitemtrans=vipitemtranshead,vipiteminfo=vipiteminfo,
                                                                                transtype=vipitemtranshead.transtype,ttype=self.ttype,itemcode=self.srvcode,ditem=self.ditem)[0]
                    vipitemtransdetail.transqty =self.s_qty
                    vipitemtransdetail.price =self.s_price
                    vipitemtransdetail.transamount =self.s_mount
                    vipitemtransdetail.applyecode=self.pmcode
                    vipitemtransdetail.stype=self.stype
                    vipitemtransdetail.ttype=self.ttype
                    try:
                        goods=Goods.objects.get(flag='Y',company=self.company,gcode=self.srvcode)
                        vipitemtransdetail.goodsuuid =goods
                    except Exception as e:
                        print('not find goods',self.srvcode)

                    sukid = getserno(self.company, self.storecode,'vipitemtrans')
                    vipitemtranshead.sukid=sukid
                    vipitemtransdetail.sukid =sukid
                    vipitemtranshead.save()
                    vipitemtransdetail.save()

                except Exception as e:
                    print('exceiption',self.exptxserno, self.ditem,e)



    @property
    def cash_amount(self):
        return self.s_mount*self.cashratio

    @property
    def card_amount(self):
        return self.s_mount*self.cardratio

    @property
    def send_amount(self):
        return self.s_mount*self.sendratio

class Toll(GenesisModel):
    pcode = models.CharField(db_column='PCODE', max_length=10)  # Field name made lowercase.
    expvssvern = models.CharField(db_column='EXPVSSVERN', max_length=4)  # Field name made lowercase.
    totmount = models.DecimalField(db_column='TOTMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tnote = models.CharField(db_column='TNOTE', max_length=40, blank=True, null=True)  # Field name made lowercase.
    exptxserno = models.CharField(max_length=40,blank=True,null=True,db_column='EXPTXSERNO')  # Field name made lowercase.
    currency = models.CharField(max_length=8, blank=True, null=True)
    custperc = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    qty = models.DecimalField(db_column='qty',max_digits=8, decimal_places=1, blank=True, null=True)
    transuuid = models.ForeignKey(Expvstoll,db_column='transuuid',on_delete=models.DO_NOTHING,blank=True,null=True)
    ccode = models.CharField(db_column='ccode',max_length=40,blank=True,null=True)
    bankaccount =  models.ForeignKey(BankAccount,db_column='bankaccount',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='银行账号')
    confirm_ecode = models.ForeignKey(Empl,db_column='confirm_ecode', blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='财务确认人')

    class Meta:
        managed = True
        db_table = 'toll'
        unique_together = (('company','storecode','expvssvern', 'exptxserno'),)

    @property
    def sec_itemcnt(self):
        if self.company=='yiren':
            if self.ttype == 'S':
                return self.stdmins * self.secperc

class EmplArchivementDetail(GenesisModel):
    trans=models.ForeignKey(Expvstoll,db_column='transuuid',blank=True,null=True,verbose_name='交易')
    exptxserno = models.CharField(max_length=40,blank=True,null=True,db_column='exptxserno')
    ecode = models.CharField(max_length=16,blank=True,null=True,db_column='员工')
    sale_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='销售业绩')
    consume_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=2,blank=True,null=True,verbose_name='消耗业绩')

class Oldcardtonew(GenesisModel):
    # ukid = models.CharField(primary_key=True, max_length=40)
    storecode = models.CharField(max_length=10, blank=True, null=True)
    oldcardtype = models.CharField(max_length=10, blank=True, null=True)
    oldcardno = models.CharField(max_length=40, blank=True, null=True)
    oldamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    custcode = models.CharField(max_length=40, blank=True, null=True)
    isoldic = models.CharField(max_length=1, blank=True, null=True)
    vsdate = models.CharField(max_length=8, blank=True, null=True)
    newcardno = models.CharField(max_length=40)
    newamount = models.DecimalField(max_digits=10, decimal_places=2)
    casher = models.CharField(max_length=10)
    cardtype = models.CharField(max_length=10)
    note = models.CharField(max_length=500, blank=True, null=True)
    newisic = models.CharField(max_length=8, blank=True, null=True)
    opendate = models.CharField(max_length=8, blank=True, null=True)
    issuedate = models.CharField(max_length=8, blank=True, null=True)
    valdate = models.CharField(max_length=8, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)
    srvcode = models.CharField(max_length=16, blank=True, null=True)
    s_price = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    s_qty = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')

    class Meta:
        managed = True
        db_table = 'oldcardtonew'

class Forfeit(GenesisModel):
#    for_serno = models.CharField(primary_key=True, max_length=40)
#     uuid = models.UUIDField(primary_key=True,auto_created=True,default=uuid.uuid4,null=False)
    for_date = models.CharField(max_length=8, blank=True, null=True)
    for_time = models.CharField(max_length=6, blank=True, null=True)
    for_checkdate = models.CharField(max_length=8, blank=True, null=True)
    ecode = models.CharField(db_column='Ecode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=100, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    empcode = models.CharField(db_column='Empcode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ttype = models.CharField(max_length=8, blank=True, null=True)
    srvcode = models.CharField(max_length=32, blank=True, null=True)
    s_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name='员工奖罚'
        verbose_name_plural='员工奖罚'
        managed = True
        db_table = 'forfeit'

class Payout(GenesisModel):
    # po_serno = models.CharField(primary_key=True, max_length=40)
    ecode = models.CharField(max_length=10, db_column='po_ecode',blank=True, null=True)
    reason = models.CharField(max_length=1000, blank=True, null=True)
    po_amount = models.DecimalField(max_digits=14, db_column='po_amount',decimal_places=2, blank=True, null=True)
    po_checker = models.CharField(max_length=10, blank=True, null=True)
    po_date = models.CharField(max_length=8, blank=True, null=True)
    po_time = models.CharField(max_length=6, blank=True, null=True)
    po_sflag = models.CharField(max_length=1, blank=True, null=True)
    po_checkdate = models.CharField(max_length=8, blank=True, null=True)
    po_backmoney = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    storecode = models.CharField(max_length=8,blank=True,null=True,verbose_name='店铺')

    class Meta:
        verbose_name='日常支出'
        verbose_name_plural='日常支出'
        managed = True
        db_table = 'payout'

CARDSUPTYPE = Cardsupertype.objects.filter(company=common.constants.COMPANYID,flag='Y').values_list('code','name')
class Cardhistory(GenesisModel):
    transuuid = models.ForeignKey(Expvstoll,db_column='transuuid',on_delete=models.DO_NOTHING,blank=True,null=True)
    # transuuid = models.CharField(max_length=32,blank=True,null=True)
    exptxserno = models.CharField(max_length=40,blank=True,null=True,verbose_name='交易流水号')
    ccode = models.CharField(max_length=32, blank=True, null=True,verbose_name='卡号')
    vsdate = models.CharField(max_length=8, blank=True, null=True,verbose_name='交易日期')
    oriamount = models.DecimalField(max_digits=10, decimal_places=2,default=0, blank=True, null=True)
    inamount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True,verbose_name='充值金额')
    outamount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True,verbose_name='消费金额')
    leftmoney = models.DecimalField(max_digits=10, decimal_places=2, default=0,blank=True, null=True,verbose_name='余额')
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    cardinfouuid =   models.ForeignKey('adviser.Cardinfo',db_column='cardinfouuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='卡号uuid')
    cardtypeuuid = models.ForeignKey('baseinfo.Cardtype',db_column='cardtypeuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='卡类')
    comptype = models.CharField(max_length=8, blank=True,default='amount', choices=COMPTYPE,null=True,verbose_name='消费模式')
    suptype = models.CharField(max_length=8, choices=CARDSUPTYPE,blank=True, null=True,verbose_name='卡大类')

    class Meta:
        verbose_name='卡余额变动日志'
        verbose_name_plural='卡悦变动日志'
        managed = True
        db_table = 'cardhistory'

    def recalamount(self):
        if self.inamount == None:
            self.inamount = 0

        if self.outamount == None:
            self.outamount = 0

        historys =  Cardhistory.objects.filter(company=self.company,ccode=self.ccode,create_time__lt=self.create_time)
        if historys.count() == 0 :
            lastleftmoney = Cardinfo.objects.get(flag='Y',company=self.company,ccode=self.ccode).leftmoney
            print('cardhistory lastleftmoney',lastleftmoney)
            self.leftmoney = lastleftmoney
            self.oriamount = self.leftmoney - self.inamount + self.outamount
            print('history 1st recodr',self.oriamount,self.inamount,self.outamount,self.leftmoney)
            self.save()
            return
        else:
            try:
                # lastleftmoney = Cardhistory.objects.filter(company=self.company,ccode=self.ccode,create_time__lt=self.create_time).order_by('create_time').last().leftmoney
                lastleftmoney = historys.order_by('create_time').last().leftmoney
                print('11',type(lastleftmoney),lastleftmoney)
                if lastleftmoney == None:
                    lastleftmoney = Cardinfo.objects.filter(company=self.company,ccode=self.ccode)[0].leftmoney
                    # lastleftmoney =0
            except:
                lastleftmoney=0
            self.oriamount = lastleftmoney
            self.leftmoney = lastleftmoney + self.inamount - self.outamount
            self.save()
            return

class EmplDailyData(GenesisModel):
    empl = models.ForeignKey(Empl,db_column='empl',blank=True,null=True,verbose_name='员工')
    vsdate = models.DateField(blank=True,null=True,verbose_name='日期')
    vipcount = models.IntegerField(default=0,blank=True,null=True,verbose_name='客人数')
    newvipcount = models.IntegerField(default=0, blank=True, null=True, verbose_name='新客人数')
    vip10count = models.IntegerField(default=0,blank=True,null=True,verbose_name='会员数')
    vip20count = models.IntegerField(default=0,blank=True,null=True,verbose_name='散客数')
    vipscount = models.IntegerField(default=0, blank=True, null=True, verbose_name='服务客人数')
    vipgcount =  models.IntegerField(default=0,blank=True,null=True,verbose_name='销售商品会员数')
    vipccount = models.IntegerField(default=0, blank=True, null=True, verbose_name='售卡会员数')
    archivementtype = models.CharField(max_length=8,choices=ARCHIVEMENTTYPE,blank=True,null=True,verbose_name='数据类型')
    qty = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='数量')
    ticheng = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='百分比提成')
    guideamount = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='服务业绩')
    point = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='固定提成')

    class Meta:
        verbose_name='员工每日业绩'
        verbose_name_plural='员工每日业绩'
        managed = True
        db_table = 'empldailidata'


EMSTATUS=Appoption.objects.filter(company='common',seg='earneststatus',flag='Y').values_list('itemname','itemvalues')
# 定金清单
class EarnestMoney(GenesisModel):
    # vsdate = models.CharField(max_length=16,blank=True,null=True,verbose_name='交易日期')
    hunguuid = models.ForeignKey(ExpvstollHung,db_column='hungsuuid',blank=True,null=True,verbose_name='开单记录')
    transuuid = models.ForeignKey(Expvstoll,db_column='transuuid',blank=True,null=True,verbose_name='交易记录')
    # exptxserno = models.CharField(max_length=32,blank=True,null=True,verb
    # ose_name='交易流水号')
    # ditem = models.CharField(max_length=8,blank=True,null=True,verbose_name='项次')
    vipuuid = models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,on_delete=None,verbose_name='客人')
    vcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='会员号')
    ttype = models.CharField(max_length=8,blank=True,null=True,verbose_name='类型')
    itemcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='项目编号')
    price =  models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='单价')
    planqty = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='计划购买数量')
    planamount =  models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='计划支付金额')
    payedamount =  models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='已付金额')
    oweamount =  models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠款金额')

    # payedqty = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='已付金额折合数量')
    # payedleftmeony = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='已经金额折合卡余额')

    # oweqty = models.DecimalField(max_length=16,max_digits=2,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠款数量')
    # oweleftmoeny = models.DecimalField(max_length=16,max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠款金额折合卡余额')
    ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='负责员工')

    status = models.CharField(max_length=8,choices=EMSTATUS,blank=True,null=True,verbose_name='当前状态')
    remark = models.CharField(max_length=128,blank=True,null=True,verbose_name='备注')

    class Meta:
        verbose_name='客户定金清单'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'earnestmoney'

    def __str__(self):
        return self.itemcode+' owed:'+ self.oweamount

class VipItemInfo(GenesisModel):
    vip =  models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客人')
    vcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='会员号')
    ttype = models.CharField(max_length=16,choices=TTYPE,blank=True,null=True,verbose_name='项目类型')
    goodsuuid = models.ForeignKey(baseinfo.models.Goods,db_column='goodsuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='商品')
    srvuuid = models.ForeignKey(baseinfo.models.Serviece,db_column='srvuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='服务项目')
    itemuuid = models.ForeignKey(baseinfo.models.Item,db_column='itemuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='项目')
    itemcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='项目编号')
    stype = models.CharField(max_length=8,choices=STYPE,blank=True,null=True,verbose_name='是否赠送')
    comptype =  models.CharField(max_length=8,choices=COMPTYPE,blank=True,null=True,verbose_name='计算方法')
    leftqty = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='剩余数量')
    price = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='单价')
    leftmoney = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='剩余金额')
    valdate = models.DateTimeField(auto_now_add=False,blank=True,null=True,editable=True,verbose_name='有效期')
    status = models.CharField(max_length=8,choices=FLAG,blank=True,null=True,verbose_name='状态')
    valiflag = models.CharField(max_length=8,choices=FLAG,blank=True,null=True,verbose_name='是否有效')
    description =  models.CharField(max_length=128,choices=FLAG,blank=True,null=True,verbose_name='备注')

    class Meta:
        verbose_name='会员项目结存信息'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'vipiteminfo'


    def set_leftqty(self):
        try:
            logs= VipItemTranslog.objects.filter(company=self.company,vip=self.vip,vipiteminfo=self)
            lastqty = VipItemTranslog.objects.filter(company=self.company,vip=self.vip,vipiteminfo=self).last().leftqty
        except:
            lastqty = 0
        self.leftqty = lastqty
        self.save()
        return 0

VIPITEMTRANSTYPE=(
    ('G','购入'),
    ('S','服务'),
    ('ZT','自提'),
    ('M','快递'),
    ('U','在店使用')
)
VIPITEMTANSSTATUS=(
    ('10','申请'),
    ('30','完成')
)
class VipItemTransHead(GenesisModel):
    sukid = models.CharField(max_length=32, blank=True, null=True, verbose_name='系统单号')
    vip =  models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客人')
    outwhcode = models.CharField(max_length=32, blank=True, null=True, verbose_name='发货仓库')
    doccode  = models.CharField(max_length=32, blank=True, null=True, verbose_name='手工单号')
    transdate =  models.DateField(auto_now_add=False, editable=True, blank=True, null=True, verbose_name='申请日期')
    transtype = models.CharField(max_length=16, choices=VIPITEMTRANSTYPE, blank=True, null=True, verbose_name='项目交易类型')
    expressaddress =  models.ForeignKey(baseinfo.models.VipAddress,db_column='expressaddress',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='快递地址')
    expresscompany = models.CharField(max_length=16, blank=True, null=True, verbose_name='快递公司')
    expressdoccode = models.CharField(max_length=24, blank=True, null=True, verbose_name='快递单号')
    expressdate = models.DateField(auto_now_add=False, editable=True, blank=True, null=True, verbose_name='快递日期')
    applyecode = models.CharField(max_length=16, blank=True, null=True, verbose_name='申请人')
    confirmecode = models.CharField(max_length=16, blank=True, null=True, verbose_name='发货人')
    description = models.CharField(max_length=128, blank=True, null=True, verbose_name='描述')
    status = models.CharField(max_length=16, blank=True, null=True, verbose_name='单号状态')

    class Meta:
        verbose_name = '会员项目交易信息'
        verbose_name_plural = verbose_name
        managed = True
        db_table = 'vipitemtranshead'

    def __str__(self):
        return self.vip.vname

    def sef_vipitemtranslog(self):
        if self.status =='30':
            items = VipItemTransDetail.objects.filter(flag='Y',company=self.company,vipitemtrans=self )
            for item in items:
                print('head sef_vipitemtranslog',len(items),item.sukid, item.itemcode,item.ditem,self.vip,self.uuid)
                leftqty = item.set_detailtolog()

class VipItemTransDetail(GenesisModel):
    sukid = models.CharField(max_length=32, blank=True, null=True, verbose_name='系统单号')
    ditem = models.CharField(max_length=8, blank=True, null=True, verbose_name='项次')
    vipitemtrans  =  models.ForeignKey(VipItemTransHead,db_column='vipitemtransuuid',blank=True,null=True,verbose_name='会员项目交易')
    vipiteminfo = models.ForeignKey(VipItemInfo,db_column='vipiteminfouuid',blank=True,null=True,verbose_name='会员项目')
    transtype = models.CharField(max_length=16, choices=VIPITEMTRANSTYPE,blank=True, null=True,verbose_name='项目交易类型')
    itemuuid = models.ForeignKey(baseinfo.models.Item,db_column='itemuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='项目')
    ttype = models.CharField(max_length=16,choices=TTYPE,blank=True,null=True,verbose_name='项目类型')
    itemcode = models.CharField(max_length=32, blank=True, null=True,verbose_name='项目编号')
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True,verbose_name='商品有效期')
    transqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='交易数量')
    price = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='单价')
    transamount = models.DecimalField(max_digits=32,decimal_places=2,default=0,blank=True,null=True,verbose_name='交易金额')
    # leftqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='交易后数量')
    # leftamount = models.DecimalField(max_digits=32,decimal_places=2,default=0,blank=True,null=True,verbose_name='交易后金额')
    description = models.CharField(max_length=128,blank=True,null=True,verbose_name='描述')
    applycode = models.CharField(max_length=16, blank=True, null=True,verbose_name='申请员工')
    stype = models.CharField(max_length=8,choices=STYPE,blank=True,null=True,verbose_name='是否赠送')

    class Meta:
        verbose_name = '会员项目交易信息明细'
        verbose_name_plural = verbose_name
        managed = True
        db_table = 'vipitemtransdetail'

    def __str__(self):
        return self.vipitem.vip.vname

    def set_detailtolog(self):
        try:
            vipitemtranslog = VipItemTranslog.objects.get(flag='Y', company=self.company,vip=self.vipitemtrans.vip,
                                                                    vipitemtrans=self.vipitemtrans, ditem=self.ditem)
            leftqty = vipitemtranslog.leftqty
        except:
            vipitemtranslog = VipItemTranslog.objects.create(flag='Y', company=self.company,vip=self.vipitemtrans.vip,
                                                                    vipitemtrans=self.vipitemtrans, ditem=self.ditem)
            vipitemtranslog.storecode = self.storecode
            vipitemtranslog.vipiteminfo = self.vipiteminfo
            vipitemtranslog.vcode = self.vipitemtrans.vip.vcode
            vipitemtranslog.transtype = self.vipitemtrans.transtype
            vipitemtranslog.vipiteminfo = self.vipiteminfo
            print('vipitemtranslog',vipitemtranslog.ditem)
            vipitemtranslog.ttype = self.ttype
            vipitemtranslog.sukid =self.sukid
            print('sukid')
            vipitemtranslog.ditem =self.ditem
            print('1321')
            vipitemtranslog.goodsuuid = Goods.objects.get(flag='Y',company=self.company,gcode=self.itemcode)
            print('qwqwe')
            vipitemtranslog.itemcode =self.itemcode
            vipitemtranslog.stype =self.stype
            vipitemtranslog.transqty =self.transqty
            vipitemtranslog.price =self.price
            vipitemtranslog.transamount = self.transamount
            vipitemtranslog.save()
            print('before save')
            leftqty = vipitemtranslog.set_leftqty()
            print('after save1')
            self.vipiteminfo.leftqty = leftqty
            self.vipiteminfo.save()
            print('after save2')
        return leftqty

class VipItemTranslog(StoreCommonBaseModel):
    transdate =  models.DateField(auto_now_add=False, editable=True, blank=True, null=True, verbose_name='提货日期')
    vip = models.ForeignKey(baseinfo.models.Vip, db_column='vipuuid', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='客人')
    vcode = models.CharField(max_length=32, blank=True, null=True, verbose_name='会员号')
    vipiteminfo = models.ForeignKey(VipItemInfo,db_column='vipiteminfouuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='会员项目')
    transtype = models.CharField(max_length=16, choices=VIPITEMTRANSTYPE, blank=True, null=True, verbose_name='项目交易类型')
    ttype = models.CharField(max_length=16, choices=TTYPE,default='G', blank=True, null=True, verbose_name='项目类型')
    transitemuuid = models.ForeignKey(Expense,db_column='expenseuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='购入交易单')
    vipitemtrans = models.ForeignKey(VipItemTransHead,db_column='vipitemtransuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='提货交易单')
    sukid = models.CharField(max_length=32,blank=True,null=True,verbose_name='系统流水号')
    ditem = models.CharField(max_length=8,blank=True,null=True,verbose_name='项次')
    goodsuuid = models.ForeignKey(baseinfo.models.Goods,db_column='goodsuuid', blank=True, null=True, on_delete=models.SET_NULL,verbose_name='商品')
    srvuuid = models.ForeignKey(baseinfo.models.Serviece,db_column='srvuuid', blank=True, null=True, on_delete=models.SET_NULL,verbose_name='服务项目')
    itemuuid = models.ForeignKey(baseinfo.models.Item,db_column='itemuuid', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='项目')
    itemcode = models.CharField(max_length=32, blank=True, null=True, verbose_name='项目编号')
    stype = models.CharField(max_length=8, choices=STYPE, blank=True, null=True, verbose_name='是否赠送')
    transqty = models.DecimalField(max_digits=32,decimal_places=2,blank=True,null=True,verbose_name='交易数量')
    price = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='单价')
    transamount = models.DecimalField(max_digits=32,decimal_places=2,blank=True,null=True,verbose_name='金额')
    leftqty  = models.DecimalField(max_digits=32,decimal_places=2,blank=True,null=True,verbose_name='剩余数量')


    class Meta:
        verbose_name = '会员项目交易信息日志'
        verbose_name_plural = verbose_name
        managed = True
        db_table = 'vipitemtranslog'

    def __str__(self):
        return self.vip.vname


    def set_leftqty(self):
        try:
            lastqty = VipItemTranslog.objects.filter(company=self.company,vip=self.vip, vipiteminfo = self.vipiteminfo , id__lt=self.id).last().leftqty
            if lastqty == None:
                lastqty = 0
        except:
            lastqty = 0

        print('lastqty',self.itemcode,lastqty)

        if self.transtype == 'C':
            self.leftqty = lastqty + self.transqty

        if self.transtype ==  'G':
            self.leftqty = lastqty + self.transqty

        if self.transtype in ('ZT','MAIL'):
            self.leftqty = lastqty - self.transqty

        print('self.leftqty',self.itemcode, self.leftqty)

        self.save()
        return self.leftqty
