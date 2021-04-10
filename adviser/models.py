#coding = utf-8

from django.db import models
from django.db.models import Sum
import sys
import uuid,datetime

#from common import constants
from common.constants import FLAG, SALESFLAG, COMPTYPE, TTYPE,SCHEDULELIST,STYPE,DEFAULT_NORMAL_PCODE,DEFAULT_SEND_PCODE,CAN_CHECKOUT_FLAG
from common.models import Sequence
# from common.views import getserno
from baseinfo.models import *
# from cashier.models import Expvstoll,Expense,Toll


# from baseinfo.models import GenesisModel,Serviece, Goods, Cardtype

class paydetail(object):
    def __init__(self,**kwargs):
        self.company=kwargs.get('company','demo')
        self.storecode=kwargs.get('storecode','88')
        self.hunguuid = kwargs.get('hunguuid','')
        self.hungserno = kwargs.get('hungserno','')
        self.pcode=kwargs.get('pcode')
        self.amount = kwargs.get('amount')
        self.qty = kwargs.get('qty')


class Cardinfo(GenesisModel):
    ccode = models.CharField(db_column='CCODE', max_length=40,blank=True,null=False,verbose_name='卡号')  # Field name made lowercase.
    vcode = models.CharField(max_length=32,blank=True, null=True,verbose_name='会员号')  # Field name made lowercase.
    senddate = models.CharField(db_column='SENDDATE', max_length=8, blank=True, null=True)  # Field name made lowercase.
    svalue = models.DecimalField(db_column='SVALUE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pvalue = models.DecimalField(db_column='PVALUE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pinno = models.CharField(db_column='PINNO', max_length=10, blank=True, null=True,verbose_name='密码')  # Field name made lowercase.
    status = models.CharField(db_column='STATUS', choices=FLAG,max_length=1, blank=True, null=True,verbose_name='状态')  # Field name made lowercase.
    cardtype = models.CharField(db_column='CARDTYPE', max_length=16,blank=True,null=True,verbose_name='卡类')  # Field name made lowercase.
    valdate = models.CharField(db_column='VALDATE', max_length=8, blank=True, null=True,verbose_name='有效期截止日期')  # Field name made lowercase.
    leftmoney = models.DecimalField(db_column='LEFTMONEY', max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='余额')  # Field name made lowercase.
    cardnote = models.CharField(db_column='CARDNOTE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    owevalue = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    point = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    opendate = models.CharField(max_length=12, blank=True, null=True,verbose_name='开始使用日期')
    issuedate = models.CharField(max_length=8, blank=True, null=True,verbose_name='销售日期')
    isic = models.CharField(max_length=1, blank=True, null=True)
    rfmac = models.CharField(max_length=16, blank=True, null=True)
    sector = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)
    suptype = models.CharField(max_length=8, blank=True, null=True)
    s_price = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    leftqty = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    pricetype = models.CharField(max_length=8, blank=True, null=True)
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='所属店铺')
    promotionsid = models.CharField(max_length=16, blank=True, null=True,verbose_name='购买时活动编号')
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',on_delete=models.SET_NULL,blank=True,null=True,verbose_name='客户唯一号')
    stype = models.CharField(max_length=8,choices=STYPE,default='N',blank=True,null=True,verbose_name='是否赠送')
    cardtypeuuid = models.ForeignKey('baseinfo.Cardtype',db_column='cardtypeuuid', on_delete=models.DO_NOTHING,blank=True,null=True,related_name='cardtypeuuid', verbose_name='卡类')  # Field name made lowercase.


    class Meta:
        verbose_name='会员卡'
        verbose_name_plural='会员卡'
        managed = True
        db_table = 'cardinfo'
        indexes = [
            models.Index(
                fields=['company','storecode','ccode'],
                name='company_store_ccode_idx',
            ),
        ]

    # @property
    # def cardtypeuuid(self):
    #     try:
    #         cardtype = Cardtype.objects.get(company=self.company,cardtype=self.cardtype)
    #         return self.cardtype
    #     except:
    #         return None

class Cardblacklist(GenesisModel):
    cardownareacode = models.CharField(max_length=8, blank=True, null=True)
    cardowncompay = models.CharField(max_length=16, blank=True, null=True)
    cardownstore = models.CharField(max_length=16)
    ccode = models.CharField( max_length=40)
    vdate = models.CharField(max_length=8, blank=True, null=True)
    vtime = models.CharField(max_length=8, blank=True, null=True)
    description = models.CharField(max_length=512, blank=True, null=True)
    ecode = models.CharField(max_length=16, blank=True, null=True)
    flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        verbose_name='卡黑名单'
        verbose_name_plural='卡黑名单'
        managed = True
        db_table = 'cardblacklist'



    # def save(self,*args, **kwargs):
    #     hunguuid = ExpvstollHung.objects.get(uuid=self.hunguuid)
    #
    #     sum_amount= ExpenseHung.objects.filter(flag='Y',hunguuid=hunguuid).values('hunguuid').annotate(totamount=Sum('s_mount_hung')).values('hunguuid','totamount')[0].totamount
    #     print(sum_amount)
    #     hunguuid.totmount_hung=sum_amount
    #     hunguuid.save()
    #     return 0

# flag1_hung:   A10: 开单时，付款卡为计费卡，卡余额不足，无法直接结帐。
#               T10：计次卡, 开单时，未完成销售或者余次不足
#               T30：        开单时，开单时余次充足，可以直接结帐
#               T80：疗程卡  开单时：开单时，余次充足，但之前已经存在开单记录


class ExpvstollHung(GenesisModel):
    ccode_hung = models.CharField(max_length=40, blank=True, null=True)
    vcode_hung = models.CharField(max_length=40, blank=True, null=True)
    sumdisc_hung = models.DecimalField(max_digits=6, decimal_places=5, default=1,blank=True, null=True)
    mondisc_hung = models.DecimalField(max_digits=14, decimal_places=2,default=0, blank=True, null=True)
    totmount_hung = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    times_hung = models.CharField(max_length=1, blank=True, null=True)
    cdate_hung = models.CharField(max_length=8, blank=True, null=True)
    mnote_hung = models.CharField(max_length=100, blank=True, null=True)
    cardtype_hung = models.CharField(max_length=16, blank=True, null=True)
    exptxserno_hung = models.CharField( max_length=40,blank=True,null=True)
    vsdate_hung = models.CharField(max_length=8, blank=True, null=True)
    vstime_hung = models.CharField(max_length=8, blank=True, null=True)
    ecode_hung = models.CharField(max_length=16, blank=True, null=True)
    valiflag_hung = models.CharField(max_length=1, blank=True, null=True)
    ttype_hung = models.CharField(max_length=8, blank=True, null=True)
    point_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oldcustflag_hung = models.CharField(max_length=1, blank=True, null=True)
    goodssaletype_hung = models.CharField(max_length=16, blank=True, null=True)
    doccode_hung = models.CharField(max_length=40, blank=True, null=True)
    remark_hung = models.CharField(max_length=255, blank=True, null=True)
    psstatus_hung = models.CharField(max_length=8, blank=True, null=True)
    roomid_hung = models.CharField(max_length=40, blank=True, null=True)
    # totalmins_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # startdate_hung = models.CharField(max_length=8, blank=True, null=True)
    # starttime_hung = models.CharField(max_length=8, blank=True, null=True)
    # enddate_hung = models.CharField(max_length=8, blank=True, null=True)
    # endtime_hung = models.CharField(max_length=8, blank=True, null=True)
    vipcode = models.CharField(max_length=16, blank=True, null=True)
    pmcode_hung = models.CharField(max_length=16, blank=True, null=True)
    asscode1_hung = models.CharField(max_length=40, blank=True, null=True)
    asscode2_hung = models.CharField(max_length=40, blank=True, null=True)
    storecode_hung = models.CharField(max_length=16, blank=True, null=True)
    cashposition_hung = models.CharField(max_length=168, blank=True, null=True)
    flag1_hung = models.CharField(max_length=8, blank=True, null=True)
    flag2_hung = models.CharField(max_length=8, blank=True, null=True)
    flag3_hung = models.CharField(max_length=8, blank=True, null=True)
    bookingeventid = models.BigIntegerField(blank=True, null=True)
    promotionsid = models.CharField(max_length=16, blank=True, null=True)
    # ttype1 = models.CharField(max_length=8, blank=True, null=True)
    terminalid = models.CharField(max_length=36, blank=True, null=True)
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    # vsdatetime_hung = models.DateTimeField(blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'expvstoll_hung'


    @property
    def sumamount(self):
        sumamount =0
        hungdetails = ExpenseHung.objects.filter(company=self.company, flag='Y', exptxserno_hung=self.exptxserno_hung)
        for hungdetail in hungdetails:
            sumamount = sumamount + hungdetail.s_mount_hung
        return sumamount

    @property
    def normal_amount(self):
        normal_amount =0
        print(self.company,self.uuid)
        hungdetails = ExpenseHung.objects.filter(company=self.company, flag='Y',stype_hung='N', exptxserno_hung=self.exptxserno_hung)
        print(hungdetails.count())
        for hungdetail in hungdetails:
            print('ditem',hungdetail.s_mount_hung)
            normal_amount = normal_amount + hungdetail.s_mount_hung

        return normal_amount

    @property
    def send_amount(self):
        send_amount =0
        hungdetails = ExpenseHung.objects.filter(company=self.company, flag='Y', stype_hung='S',
                                                 exptxserno_hung=self.exptxserno_hung)
        for hungdetail in hungdetails:
            send_amount = send_amount + hungdetail.s_mount_hung
        return send_amount

    @property
    def sumqty(self):
        sumqty =0
        hungdetails = ExpenseHung.objects.filter(company=self.company, flag='Y',exptxserno_hung=self.exptxserno_hung)
        for hungdetail in hungdetails:
            sumqty = sumqty + hungdetail.s_qty_hung
        return sumqty


    @property
    def willpayamount(self):
        if len(self.ccode_hung) > 0:
            paycardinfo = Cardinfo.objects.get(company=self.company, flag='Y', status='O', ccode=self.ccode_hung)
            if paycardinfo.leftmoney >= self.sumamount:
                willpayamount = 0
            else:
                willpayamount =  (self.sumamount - paycardinfo.leftmoney)
        else:
            willpayamount = self.sumamount

        return willpayamount

    @property
    def defaultpcode(self):
        if len(self.ccode_hung) > 0:
            paycardinfo = Cardinfo.objects.get(company=self.company, flag='Y', status='O', ccode=self.ccode_hung)
            if paycardinfo.cardtypeuuid.comptype=='amount':
                print('amount')
                defaultpcode = paycardinfo.cardtypeuuid.defaultpaycode

            if paycardinfo.cardtypeuuid.comptype == 'times':
                print('times')


            if len(defaultpcode) == 0:
                defaultpcode='B'
        else:
            defaultpcode=DEFAULT_NORMAL_PCODE
        return  defaultpcode

    def defaultpaylist(self):
        defaultpaylist = dict()
        paylist=[]
        willpayamount = 0
        print(self.ccode_hung)
        if len(self.ccode_hung) > 0:
            paycardinfo = Cardinfo.objects.get(company=self.company, flag='Y', status='O', ccode=self.ccode_hung)
            print('leftmoney',paycardinfo.leftmoney,self.sumamount)
            if paycardinfo.cardtypeuuid.comptype == 'amount':
                if paycardinfo.leftmoney >= self.sumamount:
                    # willpayamount =   0
                    defaultpaylist[self.defaultpcode] = self.sumamount
                else:
                    willpayamount = self.sumamount - paycardinfo.leftmoney
                    defaultpaylist[self.defaultpcode] = paycardinfo.leftmoney
                    defaultpaylist[DEFAULT_NORMAL_PCODE] = willpayamount

            if paycardinfo.cardtypeuuid.comptype == 'times':
                if paycardinfo.leftqty >= self.sumqty:
                    # willpayamount =   0
                    defaultpaylist[self.defaultpcode] = self.sumamount
                    self.paylist[0]= paydetail()
                    self.paydetail[0].company=self.company
                    self.paydetail[0].storecode=self.storecode
                    self.paydetail[0].pcode=self.defaultpcode
                    self.paydetail[0].amount= self.sumamount
                    self.paydetail[0].qty = self.sumqty
                else:
                    willpayamount = self.sumamount - paycardinfo.leftmoney
                    defaultpaylist[self.defaultpcode] = paycardinfo.leftmoney
                    defaultpaylist[DEFAULT_NORMAL_PCODE] = willpayamount

        else:
            willpayamount = self.sumamount
            if self.send_amount >0 :
                defaultpaylist[DEFAULT_NORMAL_PCODE]=self.send_amount

            if self.normal_amount >0:
                defaultpaylist[DEFAULT_NORMAL_PCODE] = self.normal_amount
        print(type(defaultpaylist))
        return defaultpaylist

    def set_check_out_flag(self):
        try:
            cardinfo = Cardinfo.objects.get(flag='Y',company=self.company,vipuuiid=self.vipuuid,ccode=self.ccode_hung,status='O')[0]
            if cardinfo.cardtypeuuid.comptype == 'times':
                self.flag1_hung = CAN_CHECKOUT_FLAG
                self.save()
        except:
            print('not get cardinfo', self.company,self.ccode_hung)



class ExpenseHung(GenesisModel):
    ttype_hung = models.CharField(db_column='TTYPE_hung', max_length=8, blank=True,
                                  null=True)  # Field name made lowercase.
    secdisc_hung = models.DecimalField(db_column='SECDISC_hung', max_digits=10, decimal_places=6, blank=True,
                                       null=True)  # Field name made lowercase.
    pmcode_hung = models.CharField(db_column='PMCODE_hung', max_length=10, blank=True,
                                   null=True)  # Field name made lowercase.
    pmperc_hung = models.DecimalField(db_column='PMPERC_hung', max_digits=6, decimal_places=5, blank=True,
                                      null=True)  # Field name made lowercase.
    asscode1_hung = models.CharField(db_column='ASSCODE1_hung', max_length=10, blank=True,
                                     null=True)  # Field name made lowercase.
    asscode2_hung = models.CharField(db_column='ASSCODE2_hung', max_length=10, blank=True,
                                     null=True)  # Field name made lowercase.
    dnote_hung = models.CharField(db_column='DNOTE_hung', max_length=100, blank=True,
                                  null=True)  # Field name made lowercase.
    exptxserno_hung = models.CharField(db_column='EXPTXSERNO_hung', max_length=40)  # Field name made lowercase.
    ditem_hung = models.CharField(db_column='DITEM_hung', max_length=4)  # Field name made lowercase.
    s_price_hung = models.DecimalField(db_column='S_PRICE_hung', max_digits=10, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    s_qty_hung = models.DecimalField(db_column='S_QTY_hung', max_digits=10, decimal_places=2, blank=True,
                                     null=True)  # Field name made lowercase.
    s_mount_hung = models.DecimalField(db_column='S_MOUNT_hung', max_digits=14, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    secperc_hung = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    srvcode_hung = models.CharField(max_length=40, blank=True, null=True)
    addvamoney_hung = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    pmguideperc_hung = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    secguideperc_hung = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    thprec_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pmpoint_hung = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    secpoint_hung = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    thrpoint_hung = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    cpoint_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pmamount_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    secamount_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    thramount_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_basenum_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_secbasenum_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exp_thrbasenum_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    thrguideperc_hung = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    goodssaletype_hung = models.CharField(max_length=1, blank=True, null=True)
    srvactmount_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    srvmondisc_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oldcustflag_hung = models.CharField(max_length=8, blank=True, null=True)
    srvcost_hung = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    srvcostperc_hung = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    s_pricecurrency_hung = models.CharField(max_length=8, blank=True, null=True)
    s_mountcurrency_hung = models.CharField(max_length=8, blank=True, null=True)
    stdmins_hung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stype_hung = models.CharField(max_length=8, blank=True, null=True)
    otherserno_hung = models.CharField(max_length=40, blank=True, null=True)
    oldcardtype_hung = models.CharField(max_length=16, blank=True, null=True)
    newcardtype_hung = models.CharField(max_length=16, blank=True, null=True)
    secoldcustflag_hung = models.CharField(max_length=8, blank=True, null=True)
    throldcustflag_hung = models.CharField(max_length=8, blank=True, null=True)
    depositeflag = models.CharField(max_length=8, blank=True, null=True)
    owegoodsflag = models.CharField(max_length=8, blank=True, null=True)
    pregoodsflag = models.CharField(max_length=8, blank=True, null=True)
    returnway = models.CharField(max_length=8, blank=True, null=True)
    peiliaoflag = models.CharField(max_length=8, blank=True, null=True)
    emplflag = models.CharField(max_length=8, blank=True, null=True)
    vipflag = models.CharField(max_length=8, blank=True, null=True)
    jiezhangflag = models.CharField(max_length=8, blank=True, null=True)
    billingstatus = models.IntegerField(blank=True, null=True)
    sendamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotionsamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oriamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True)
    hunguuid = models.CharField(max_length=32,blank=True,null=True)
    # hunguuid = models.ForeignKey(ExpvstollHung, db_column='hunguuid', blank=True, null=True,on_delete=models.SET_NULL)

    class Meta:
        managed = True
        db_table = 'expense_hung'
        unique_together = (('exptxserno_hung', 'ditem_hung'),)

# 预约时间段
class Timeset(models.Model):
    timeid = models.CharField(primary_key=True, max_length=8)
    flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        verbose_name='时间段'
        verbose_name_plural=''
        managed = True
        db_table = 'timeset'

class Emplschedule(GenesisModel):
    vsdate = models.CharField(max_length=8,verbose_name='日期')
    ecode = models.CharField(max_length=16,verbose_name='员工')
    scheduleid = models.CharField(max_length=16, blank=True,choices=SCHEDULELIST, null=True,verbose_name='班次')
    operno = models.CharField(max_length=8, blank=True, null=True,verbose_name='预约表顺序')
    flag = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'emplschedule'
        unique_together = (('company','storecode','vsdate', 'ecode'),)

    def __str__(self):
        return self.ecode

class Instrument(GenesisModel):
    instrumentid = models.IntegerField(default=0,blank=False)
    instrumentname = models.CharField(max_length=64, blank=True, null=True,verbose_name='仪器')
    # storecode = models.ForeignKey('baseinfo.Storeinfo',db_column='storecode', blank=True, null=True,on_delete=models.SET_NULL,verbose_name='所在店铺')
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='所属店铺')
    instatus = models.CharField(max_length=8, choices=FLAG,blank=True, null=True)

    class Meta:
        verbose_name_plural='仪器'
        verbose_name='仪器'
        managed = True
        db_table = 'instrument'



    def __str__(self):
        return self.instrumentname

class Room(GenesisModel):
    roomid = models.CharField(max_length=16,blank=True,null=False,verbose_name='房间号')
    roomname = models.CharField(max_length=40, blank=True, null=True, verbose_name='房间名称')
    roomtype = models.CharField(max_length=10, blank=True, null=True)
    # storecode = models.ForeignKey('baseinfo.Storeinfo',db_column='storecode',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='所属店铺')
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='所属店铺')

    class Meta:
        verbose_name='房间'
        verbose_name_plural='房间'
        managed = True
        db_table = 'room'


    def __str__(self):
        return self.roomname


#预约表
class Bookingevent(models.Model):
    bookingeventid = models.BigAutoField(primary_key=True,null=False)
    bookingeventname = models.CharField(max_length=40, blank=True, null=True)
    bookingstartdate = models.CharField(max_length=8,blank=False, null=True)
    bookingstarttime = models.CharField(max_length=8,blank=False, null=True)
    bookingendtime = models.CharField(max_length=8,blank=True, null=True)
    vcode = models.CharField(max_length=16,blank=True,null=True)
    vname = models.CharField(max_length=16,blank=True,null=True)
    ecode = models.CharField(max_length=40, blank=True, null=True)
    roomid = models.CharField(max_length=32, blank=True, null=True)
    instrumentid = models.CharField(max_length=32, blank=True, null=True)
    oldcustflag = models.CharField(max_length=8, blank=True, null=True)
    bookingoperdate = models.CharField(max_length=8, blank=True, null=True)
    comeintime = models.CharField( max_length=8,blank=True, null=True)
    leavetime = models.CharField( max_length=8,blank=True, null=True)
    operecode = models.CharField(max_length=16, blank=True, null=True)
    bookingstatus = models.CharField(max_length=8, blank=True, null=True)
    bookingflag = models.CharField(max_length=8, default='Y',blank=True, null=True)
    bookingtype = models.CharField(max_length=8, blank=True, null=True)
    areacode = models.CharField(max_length=16, blank=True, null=True)
    companyid = models.CharField(max_length=16, blank=True, null=True)
    storecode = models.CharField(max_length=16, blank=True, null=True)
    teamid = models.CharField(max_length=8, blank=True, null=True)
    bookingdetail = models.CharField(max_length=128, blank=True, null=True)
    mtcode = models.CharField(max_length=32, blank=True, null=True)
    viptype = models.CharField(max_length=8, blank=True, null=True)
    confirmtime = models.TimeField( blank=True, null=True)
    confirmempl = models.CharField(max_length=16, blank=True, null=True)
    roomstarttime = models.CharField( max_length=8,blank=True, null=True)
    roomendtime = models.CharField( max_length=8,blank=True, null=True)
    instrumentbookingstarttime = models.CharField( max_length=8,blank=True, null=True)
    instrumentstarttime = models.CharField(max_length=8,blank=True, null=True)
    instrumentendtime = models.CharField(max_length=8, blank=True, null=True)
    emplstarttime = models.CharField( max_length=8,blank=True, null=True)
    emplendtime = models.CharField( max_length=8,blank=True, null=True)
    callcleantime = models.CharField( max_length=8,blank=True, null=True)
    cleanstarttime = models.CharField( max_length=8,blank=True, null=True)
    cleanendtime = models.CharField( max_length=8,blank=True, null=True)
    canceltime = models.CharField( max_length=8,blank=True, null=True)
    linkbookngeventid = models.BigIntegerField(blank=True, null=True)
    # qrcode = models.CharField(max_length=2800, blank=True, null=True)
    instrumentbookingendtime = models.CharField(max_length=8, blank=True, null=True)
    vipcode = models.CharField(max_length=24, blank=True, null=True)
    billingendtime = models.CharField( max_length=8,blank=True, null=True)
    kaidanlasttime = models.CharField( max_length=8,blank=True, null=True)
    peiliaolasttime = models.CharField( max_length=8,blank=True, null=True)
    peiliaoconfirmtime = models.CharField(max_length=8,blank=True, null=True)
    pregoodsendtime = models.CharField(max_length=8,blank=True, null=True)
    vipconfirmtime = models.CharField(max_length=8,blank=True, null=True)
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',related_name='vip', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    uuid = models.UUIDField(auto_created=True,editable=False,default=uuid.uuid4,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'bookingevent'
        verbose_name='预约'
        verbose_name_plural='预约'

    def __str__(self):
        return self.vcode;

INFOTYPE = (
    ('10','新客咨询'),
    ('20','服务记录'),
    ('30','投诉建议')
)

class Vipinfogroup1(GenesisModel):
    # uuid = models.UUIDField(primary_key=True,auto_created=True,default=uuid.uuid4,null=False,blank=True)
    # storecode = models.ForeignKey('baseinfo.Storeinfo',db_column='storecode', max_length=10, blank=True,null=True,on_delete=models.SET_NULL,verbose_name='门店')
    storecode = models.CharField(db_column='StoreCode', default='0',max_length=16,blank=True,null=False,verbose_name='店铺编号')  # Field name made lowercase.
 #   vcode = models.ForeignKey('hdms.Vip',db_column='vcode',max_length=32, blank=True, null=True,verbose_name='顾客编号')
    mtcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='联系方法')
    vsdate = models.DateField(auto_now=True,verbose_name='咨询日期')
    # ecode = models.ForeignKey('baseinfo.Empl',db_column='ecode',to_field='ecode',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='咨询员工')
    infotype = models.CharField(max_length=16,blank=True,null=True,verbose_name='信息类型')
    vg1item1 = models.TextField( blank=True, null=True,verbose_name='跟踪信息')
    vg1item2 = models.CharField(max_length=256, blank=True, null=True)
    vg1item3 = models.CharField(max_length=2560, blank=True, null=True)
    vg1item4 = models.CharField(max_length=256, blank=True, null=True)
    vg1item5 = models.CharField(max_length=256, blank=True, null=True)
    vg1item6 = models.CharField(max_length=256, blank=True, null=True)
    vg1item7 = models.CharField(max_length=256, blank=True, null=True)
    vg1item8 = models.CharField(max_length=256, blank=True, null=True)
    vg1item9 = models.CharField(max_length=256, blank=True, null=True)
    vg1item10 = models.CharField(max_length=256, blank=True, null=True)
    vg1item11 = models.CharField(max_length=256, blank=True, null=True)
    vg1item12 = models.CharField(max_length=256, blank=True, null=True)
    vg1item13 = models.CharField(max_length=256, blank=True, null=True)
    vg1item14 = models.CharField(max_length=256, blank=True, null=True)
    vg1item15 = models.CharField(max_length=256, blank=True, null=True)
    vg1item16 = models.CharField(max_length=256, blank=True, null=True)
    # flag = models.CharField(max_length=8, choices=FLAG, blank=True, null=True,verbose_name='记录是否有效')

    class Meta:
        verbose_name='客户咨询记录'
        verbose_name_plural='客户咨询记录'
        managed = True
        db_table = 'vipinfogroup1'

    # def __str__(self):
    #     return self.vcode.vname

#   10: 加入购物车
#   20: 已经从购物车确认挂账开单
#   30: 备用
SHOPPINGCART_STATUS=['10','20','30']
class ShoppingCart(GenesisModel):
    vipuuid = models.ForeignKey('baseinfo.Vip',db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    vcode=models.CharField(max_length=32,db_column='vcode',blank=True,null=True,verbose_name='会员号')
    payccode=models.CharField(max_length=32,db_column='ccode',blank=True,null=True,verbose_name='付款卡卡号')
    vsdate=models.CharField(max_length=8,db_column='vsdate',blank=True,null=True,verbose_name='日期')
    ttype=models.CharField(max_length=8,db_column='ttype',blank=False,null=False,verbose_name='交易类别')
    stype=models.CharField(max_length=8,db_column='stype',default='N',blank=True,null=True,verbose_name='是否赠送')
    itemcode=models.CharField(max_length=32,db_column='itemcode',blank=True,null=True,verbose_name='项目编号')
    itemname = models.CharField(max_length=128,db_column='itemname',blank=True,null=True,verbose_name='名称')
    qty=models.DecimalField(max_digits=8,decimal_places=2,default=1,blank=True,null=True,verbose_name='数量')
    price=models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='原价')
    secdisc = models.DecimalField(max_digits=8,decimal_places=4,default=1,blank=True,null=True,verbose_name='折扣')
    mondisc = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='免单金额')
    amount=models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='实收金额')
    pmcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='顾问')
    seccode = models.CharField(max_length=16,blank=True,null=True,verbose_name='美疗师')
    thrcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='美疗师')
    pmratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True,verbose_name='顾问拆分比例')
    secratio = models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True,verbose_name='美容师拆分比例')
    thrratio =  models.DecimalField(max_digits=8,decimal_places=4,blank=True,null=True,verbose_name='美容师拆分比例')
    promotionsid = models.CharField(max_length=32,default='0',blank=True,null=True,verbose_name='活动编号')
    valiflag=models.CharField(max_length=8,default='Y',blank=True,null=True,verbose_name='是否有效')
    status= models.CharField(max_length=8,default='10',blank=True,null=True,verbose_name='当期状态')
    planqty = models.DecimalField(max_digits=8,decimal_places=2,default=0, blank=True,null=True,verbose_name='预订数量')
    planamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='预订金额')
    payedamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='定金金额')
    oweamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠款金额')
    remark = models.CharField(max_length=128,blank=True,null=True,verbose_name='备注')
    depositeflag = models.CharField(max_length=8,default='N',blank=True,null=True,verbose_name='是否存院')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        managed = True
        db_table = 'shoppingcart'

    def __delete__(self, instance):
        self.flag='N'
        self.save()
        return self

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields='itemname'):
    #     if self.ttype=='S':
    #         item=Serviece.objects.filter(company=self.company,svrcdoe=self.itemcode,flag='Y').last()
    #         self.itemname=item.svrname
    #
    #     if self.ttype=='G':
    #         item=Goods.objects.filter(company=self.company,gcode=self.itemcode,flag='Y').last()
    #         self.itemname=item.gname
    #
    #     if self.ttype=='I':
    #         cardinfo=Cardinfo.objects.filter(company=self.company,ccode=self.itemcode,flag='Y').last()
    #         cardtype=Cardtype.objects.filter(company=self.company,cardtype=cardinfo.cardtype,flag='Y').last()
    #         self.itemname=cardtype.cardname


    # def get_itemname(self):
    #     if self.ttype=='S':
    #         item = Serviece.objects.filter(company=self.company,svrcdoe=self.itemcode,flag='Y').last()
    #         return item.svrname
    #
    #     if self.ttype=='G':
    #         item=Goods.objects.filter(company=self.company,gcode=self.itemcode,flag='Y').last()
    #         return item.gcode
    #
    #     if self.ttype=='I':
    #         cardinfo=Cardinfo.objects.filter(company=self.company,ccode=self.itemcode,flag='Y').last()
    #         cardtype=Cardtype.objects.filter(company=self.company,cardtype=cardinfo.cardtype,flag='Y').last()
    #         return cardtype.cardname


