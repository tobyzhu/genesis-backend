from django.db import models
import time,datetime
import django.utils.timezone as timezone
from django.db.models import Avg,Sum,Count
import uuid
# Create your models here.

import baseinfo.models

from common.constants import FLAG, SALESFLAG, COMPTYPE,STYPE, TTYPE,SCHEDULELIST,VIPTYPE, CASETYPE, CASESTATUS,SOURCE,SALEATR,COMPANYID
from common.constants import GenesisModel,BaseModel,CompanyCommonBaseModel,StoreCommonBaseModel

class Goodstranslog(models.Model):
    gtranukid = models.BigAutoField(primary_key=True)
    sukid = models.CharField(max_length=40)
    saleatr = models.CharField(max_length=8)
    vdate = models.CharField(max_length=8)
    sumdisc = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    tmount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    gnote = models.CharField(max_length=100, blank=True, null=True)
    ecode = models.CharField(max_length=10, blank=True, null=True)
    emp_ecode = models.CharField(max_length=10, blank=True, null=True)
    doccode = models.CharField(max_length=40, blank=True, null=True)
    areacode = models.CharField(max_length=8, blank=True, null=True)
    companyid = models.CharField(max_length=16, blank=True, null=True)
    storecode = models.CharField(max_length=10, blank=True, null=True)
    whcode = models.CharField(max_length=20, blank=True, null=True)
    goodsvaldate = models.CharField(db_column='goodsvalDate', default='',max_length=8, blank=True, null=True,verbose_name='商品有效期')  # Field name made lowercase.
    checkdate = models.CharField(max_length=8, blank=True, null=True)
    ioflag = models.CharField(db_column='IOFlag', max_length=1, blank=True, null=True)  # Field name made lowercase.
    seqbar = models.CharField(max_length=4, blank=True, null=True)
    docdate = models.CharField(max_length=8, blank=True, null=True)
    checkindate = models.CharField(max_length=8, blank=True, null=True)
    gcode = models.CharField(max_length=40, blank=True, null=True)
    disc = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    qty1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    qty2 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    qty3 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price2 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price3 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    costprice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    amount1 = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    amount2 = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    amount3 = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    costamount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    goodsnote = models.CharField(max_length=32, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True,verbose_name='进货批次')
    creater = models.CharField(max_length=18,blank=True,null=True)
    create_time = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    company = models.CharField(max_length=16,blank=True,null=True)
    uuid = models.CharField(max_length=32,blank=True,null=True)
    transdesc = models.CharField(max_length=128,blank=True,null=True,verbose_name='交易相关描述')
    transuuid = models.UUIDField(blank=True,null=True,verbose_name='对应原始记录uuid')

    class Meta:
        verbose_name='商品进出明细'
        verbose_name_plural='商品进出明细'
        managed = True
        db_table = 'goodstranslog'
        get_latest_by='gtranukid'

    def set_qty2(self):
        try:
            lastqty2 = Goodstranslog.objects.filter(company=self.company,storecode=self.storecode,whcode=self.whcode,gcode=self.gcode,gtranukid__lt=self.gtranukid).latest().qty2
        except:
            lastqty2 = 0

        print(self.saleatr,self.gcode,self.qty1,self.qty2,lastqty2)
        if self.saleatr == 'C':
            self.qty2 = lastqty2 + self.qty1

        if self.saleatr in  ('I','IS','TI','AD'):
            self.qty2 = lastqty2 + self.qty1

        if self.saleatr in ('F','G','U','TO'):
            self.qty2 = lastqty2 - self.qty1

        print(self.saleatr,self.gcode,self.qty1,self.qty2,lastqty2)
        self.save()
        return self.qty2

    def set_qty3(self):
        if self.goodsvaldate==None:
            self.goodsvaldate=''
        try:
            lastqty3 = Goodstranslog.objects.filter(company=self.company,storecode=self.storecode,whcode=self.whcode,gcode=self.gcode,goodsvaldate=self.goodsvaldate,gtranukid__lt=self.gtranukid).latest().qty3
        except:
            lastqty3 =0
        if self.saleatr == 'C':
            self.qty3 = lastqty3 + self.qty1

        if self.saleatr in  ('I','IS','TI','AD'):
            self.qty3 = lastqty3 + self.qty1

        if self.saleatr in ('F','G','U','TO'):
            self.qty3 = lastqty3 - self.qty1

        self.save()
        return self.qty3


class Vgtranslog(GenesisModel):
    # id = models.BigAutoField(primary_key=True)
    sukid = models.CharField(max_length=40, blank=True, null=True)
    itemid = models.CharField(max_length=40, blank=True, null=True)
    doccode = models.CharField(max_length=40, blank=True, null=True)
    vsdate = models.CharField(max_length=11, blank=True, null=True)
    vstime = models.CharField(max_length=8, blank=True, null=True)
    vcode = models.CharField(max_length=40, blank=True, null=True)
    gcode = models.CharField(max_length=40, blank=True, null=True)
    transtype = models.CharField(max_length=8, blank=True, null=True)
    s_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=10, blank=True, null=True)
    remark = models.CharField(max_length=64, blank=True, null=True)
    valiflag = models.CharField(max_length=8, blank=True, null=True)
    qty1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qty2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qty3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vipuuid = models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客人')

    class Meta:
        verbose_name='会员寄存商品变动记录明细'
        verbose_name_plural='会员寄存商品变动记录明细'
        managed = True
        db_table = 'vgtranslog'

class Owelist(GenesisModel):
    # oweukid = models.BigAutoField(primary_key=True)
    sernotype = models.CharField(max_length=8, blank=True, null=True)
    owetranserno = models.CharField(max_length=32, blank=True, null=True)
    ttype = models.CharField(max_length=8, blank=True, null=True)
    stype = models.CharField(max_length=8, blank=True, null=True)
    sgccode = models.CharField(max_length=16, blank=True, null=True)
    s_qty = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    s_amount = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    vcode = models.CharField(max_length=16, blank=True, null=True)
    owetype = models.CharField(max_length=8, blank=True, null=True)
    returnway = models.CharField(max_length=8, blank=True, null=True)
    expresscompany = models.CharField(max_length=16, blank=True, null=True)
    expressdoccode = models.CharField(max_length=24, blank=True, null=True)
    returndate = models.CharField(max_length=8, blank=True, null=True)
    returnecode = models.CharField(max_length=16, blank=True, null=True)
    vsdate = models.CharField(max_length=8, blank=True, null=True)
    expressaddress = models.CharField(max_length=128, blank=True, null=True)
    owestatus = models.CharField(max_length=8, blank=True, null=True)
    ecode1 = models.CharField(max_length=8, blank=True, null=True)
    ecode2 = models.CharField(max_length=8, blank=True, null=True)
    ecode3 = models.CharField(max_length=8, blank=True, null=True)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True)
    vipuuid = models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客人')
    returnedqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='已还数量')
    oweqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠货数量')
    description = models.CharField(max_length=128,blank=True,null=True,verbose_name='描述')

    class Meta:
        verbose_name_plural='欠客人货清单'
        verbose_name='欠客人货清单'
        managed = True
        db_table = 'owelist'

class OweReturnDetail(GenesisModel):
    owelist = models.ForeignKey(Owelist,blank=True,null=True,verbose_name='欠货单')
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)
    returnedqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='已还数量')
    oweqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='欠货数量')
    description = models.CharField(max_length=128,blank=True,null=True,verbose_name='描述')
    returnway = models.CharField(max_length=8, blank=True, null=True)
    expresscompany = models.CharField(max_length=16, blank=True, null=True)
    expressdoccode = models.CharField(max_length=24, blank=True, null=True)
    returndate = models.CharField(max_length=8, blank=True, null=True)
    returnecode = models.CharField(max_length=16, blank=True, null=True)
    vsdate = models.CharField(max_length=8, blank=True, null=True)


class Goodstock(GenesisModel):
    # id = models.BigAutoField(primary_key=True)
    storecode = models.CharField(max_length=16, blank=True, null=True)
    whcode = models.CharField(max_length=16, blank=True, null=True)
    gcode = models.CharField(max_length=16)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flag = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        verbose_name='最新库存数'
        verbose_name_plural='最新库存输'
        managed = True
        db_table = 'goodstock'

class Saledtl(GenesisModel):
    saleheadid = models.ForeignKey('Salehead',blank=True,null=True,on_delete=models.SET_NULL)
    sukid = models.CharField(db_column='SUKID', max_length=40)  # Field name made lowercase.
    seqbar = models.CharField(db_column='SEQBAR', max_length=4)  # Field name made lowercase.
    docdate = models.CharField(db_column='DOCDATE', max_length=8)  # Field name made lowercase.
    gcode = models.CharField(db_column='GCODE', max_length=40)  # Field name made lowercase.
    price = models.DecimalField(db_column='PRICE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(db_column='QTY', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    disc = models.DecimalField(db_column='DISC', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mount = models.DecimalField(db_column='MOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gdnote = models.CharField(db_column='GDNOTE', max_length=40, blank=True, null=True)  # Field name made lowercase.
    stbuyamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'saledtl'
        unique_together = (('sukid', 'seqbar'),)

class Salehead(GenesisModel):
    sukid = models.CharField(db_column='SUKID',blank=True,  max_length=40)  # Field name made lowercase.
    saleatr = models.CharField(db_column='SALEATR', max_length=10, blank=True, null=True)  # Field name made lowercase.
    vdate = models.CharField(db_column='VDATE', max_length=8, blank=True, null=True,verbose_name='日期')  # Field name made lowercase.
    smndisc = models.DecimalField(db_column='SMNDISC', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tmount = models.DecimalField(db_column='TMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gnote = models.CharField(db_column='GNOTE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ecode = models.CharField(db_column='ECODE', max_length=10, blank=True, null=True)  # Field name made lowercase.
    emp_ecode = models.CharField(db_column='EMP_ECODE', max_length=10, blank=True, null=True)  # Field name made lowercase.
    doccode = models.CharField(max_length=40, blank=True, null=True)
    inwhcode = models.CharField(max_length=20, blank=True, null=True)
    outwhcode = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)
    instorecode = models.CharField(max_length=8, blank=True, null=True)
    supplierid = models.CharField(max_length=16,blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'salehead'

    def get_qty(self):
        gcodeqty = Saledtl.objects.filter(saleheadid=self.uuid).annotate(orderqty=Sum('qty')).values('gcode','qty')
        return gcodeqty

class Transdtl(GenesisModel):
    transheadid = models.ForeignKey('Transhead',blank=True,null=True,on_delete=models.SET_NULL)
    sukid = models.CharField(max_length=40, db_column='sukid',blank=True)
    seqbar = models.CharField(max_length=4)
    docdate = models.CharField(max_length=8)
    gcode = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    disc = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    trsqty = models.DecimalField(db_column='TrsQty', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mount = models.DecimalField(db_column='Mount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    trsamount = models.DecimalField(db_column='TrsAmount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gdnote = models.CharField(max_length=40, blank=True, null=True)
    stbuyamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    batch = models.CharField(max_length=16, blank=True, null=True)
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'transdtl'
        unique_together = (('sukid', 'seqbar'),)

class Transhead(GenesisModel):
    sukid = models.CharField( db_column='sukid',blank=True,max_length=40)
    saleatr = models.CharField(db_column='saleatr',max_length=10, blank=True, null=True)
    vdate = models.CharField(max_length=8, blank=True, null=True)
    smndisc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tmount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gnote = models.CharField(max_length=100, blank=True, null=True)
    ecode = models.CharField(max_length=10, blank=True, null=True)
    emp_ecode = models.CharField(max_length=10, blank=True, null=True)
    doccode = models.CharField(max_length=40, blank=True, null=True)
    instore = models.CharField(max_length=20, blank=True, null=True)
    towhcode = models.CharField(max_length=20, blank=True, null=True)
    outstore = models.CharField(max_length=20, blank=True, null=True)
    outwhcode = models.CharField(max_length=20, blank=True, null=True)
    # arrivaldate = models.CharField(db_column='ArrivalDate', max_length=8, blank=True, null=True)  # Field name made lowercase.
    # checkdate = models.CharField(max_length=8, blank=True, null=True)
    # ioflag = models.CharField(db_column='IOFlag', max_length=1, blank=True, null=True)  # Field name made lowercase.
    # checkindate = models.CharField(max_length=8, blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'transhead'

    def set_goodstranslog(self):
        if self.saleatr == '15':
            items = Transdtl.objects.filter(company=self.company,transheadid=self.uuid)
            for item in items:
                goodstranslog = Goodstranslog.objects.get_or_create(company=self.company, storecode=self.outstore,whcode=self.outwhcode, saleatr='TO',sukid=self.sukid,seqbar=self.seqbar )[0]
                goodstranslog.companyid=self.company
                goodstranslog.doccode=self.doccode
                goodstranslog.vdate=self.vdate
                goodstranslog.gnote = self.gnote
                goodstranslog.ecode = self.ecode
                goodstranslog.gcode = item.gcode
                goodstranslog.goodsvaldate = item.goodsvaldate
                goodstranslog.qty1=item.qty
                goodstranslog.price1=item.price
                goodstranslog.amount1 = item.mount
                goodstranslog.transdesc = self.outwhcode
                goodstranslog.save()
                goodstranslog.set_qty2()
                goodstranslog.set_qty3()

        if self.saleatr == '20':
            items = Transdtl.objects.filter(company=self.company,transheadid=self.uuid)
            for item in items:
                goodstranslog = Goodstranslog.objects.get_or_create(company=self.company, storecode=self.outstore,whcode=self.outwhcode, saleatr='TO',sukid=self.sukid,seqbar=self.seqbar )[0]
                goodstranslog.companyid=self.company
                goodstranslog.doccode=self.doccode
                goodstranslog.vdate=self.vdate
                goodstranslog.gnote = self.gnote
                goodstranslog.ecode = self.ecode
                goodstranslog.gcode = item.gcode
                goodstranslog.goodsvaldate = item.goodsvaldate
                goodstranslog.qty1=item.qty
                goodstranslog.price1=item.price
                goodstranslog.amount1 = item.mount
                goodstranslog.transuuid = self.uuid
                goodstranslog.transdesc= self.outwhcode
                goodstranslog.save()
                goodstranslog.set_qty2()
                goodstranslog.set_qty3()


                goodstranslog = Goodstranslog.objects.get_or_create(company=self.company, storecode=self.instore,whcode=self.towhcode, saleatr='TI',sukid=self.sukid,seqbar=self.seqbar )[0]
                goodstranslog.companyid=self.company
                goodstranslog.doccode=self.doccode
                goodstranslog.vdate=self.vdate
                goodstranslog.gnote = self.gnote
                goodstranslog.ecode = self.ecode
                goodstranslog.gcode = item.gcode
                goodstranslog.goodsvaldate = item.goodsvaldate
                goodstranslog.qty1=item.qty
                goodstranslog.price1=item.price
                goodstranslog.amount1 = item.mount
                goodstranslog.transuuid = self.uuid
                goodstranslog.transdesc=self.towhcode
                goodstranslog.save()
                goodstranslog.set_qty2()
                goodstranslog.set_qty3()

class Stockmst(GenesisModel):
    sukid = models.CharField( db_column='sukid',blank=True,max_length=40)
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='所属店铺')
    # storecode = models.ForeignKey('baseinfo.Storeinfo',blank=True,null=True,db_column='storecode',on_delete=models.SET_NULL,verbose_name='店铺')
    # wharehousecode = models.ForeignKey('baseinfo.Wharehouse',blank=True,null=True,db_column='wharehousecode',on_delete=models.SET_NULL,verbose_name='盘点仓库')
    wharehousecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='盘点仓库')
    stockdate = models.CharField(max_length=8,db_column='stockdate', blank=True, null=True,verbose_name='盘点日期')  # Field name made lowercase.
    # ecode = models.ForeignKey('baseinfo.Empl',db_column='ecode', blank=True,null=True,on_delete=models.SET_NULL,verbose_name='盘点员工')  # Field name made lowercase.
    ecode= models.CharField(max_length=16,blank=True,null=True,verbose_name='盘点员工')
    doccode = models.CharField(db_column='doccode',max_length=40,verbose_name='盘点单单号')  # Field name made lowercase.
    note = models.CharField(db_column='note', max_length=100, blank=True, null=True)  # Field name made lowercase.
    checkflag = models.CharField(db_column='checkflag', default='N',max_length=8, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        verbose_name='盘点表'
        verbose_name_plural='盘点表'
        managed = True
        db_table = 'stockmst'

class Stockdetail(GenesisModel):
    stockmst = models.ForeignKey(Stockmst,blank=True,null=True,on_delete=models.SET_NULL)
    sukid = models.CharField(max_length=40, db_column='sukid',blank=True,null=True)
    seqbar = models.CharField(max_length=4,blank=True,null=True)
    # doccode = models.ForeignKey('Stockmst',db_column='doccode',on_delete=None,null=True,verbose_name='盘点单单号')
    # gcode = models.ForeignKey('baseinfo.Goods', db_column='gcode', null=True,on_delete=models.SET_NULL , verbose_name='商品')
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='商品')
    goodsvaldate = models.CharField(max_length=8, blank=True, null=True,verbose_name='有效期')
    # batch = models.CharField(max_length=16, blank=True, null=True,verbose_name='批次')
    mqty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='电脑库存数量')
    qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='盘点数量')
    note = models.CharField(max_length=100, blank=True, null=True,verbose_name='备注')


    class Meta:
        verbose_name='盘点明细'
        verbose_name_plural='盘点明细'
        managed = True
        db_table = 'stockdetail'
    #    unique_together = (( 'doccode','item'),)


class Serviecegoods(GenesisModel):
    srvuuid = models.ForeignKey('baseinfo.Serviece',db_column='srvuuid',max_length=16,blank=True,null=True,on_delete=models.SET_NULL, verbose_name='服务项目')
    srvcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='服务项目编号')
    goodsuuid = models.ForeignKey('baseinfo.Goods',db_column='goodsuuid',max_length=16,blank=True,null=True,on_delete=models.SET_NULL, verbose_name='使用产品')
    gcode = models.CharField(max_length=32,blank=True,null=True,verbose_name='商品编号')
    qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='使用量')

    class Meta:
        managed = True
        db_table = 'serviecegoods'
        # unique_together = (('company','svrcode', 'gcode'),)

STEPFLAG=(
    ('AGREE','同意'),
    ('DISAGREE','不同意')
)
class GoodsTransHead(GenesisModel):
    sukid = models.CharField(max_length=16,blank=True,null=True,verbose_name='流水单号')
    saleatr = models.CharField(db_column='saleatr', choices=SALEATR,max_length=8,verbose_name='单号类型')  # Field name made lowercase.
    vsdate = models.DateField(db_column='vsdate',verbose_name='日期')  # Field name made lowercase.
    totamount = models.DecimalField(db_column='TMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='note', max_length=100, blank=True, null=True,verbose_name='备注')  # Field name made lowercase.
    ecode = models.CharField(max_length=16,db_column='ECODE', blank=True,null=True, verbose_name='第一流程人')  # Field name made lowercase.
    doccode = models.CharField(max_length=40, blank=True, null=True,verbose_name='手工单号')
    whcode = models.CharField(max_length=16,blank=True, null=True,verbose_name='仓库')
    otherwhcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='对应仓库')
    otherstorecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='对应门店')
    status = models.CharField(max_length=8, blank=True, null=True,verbose_name='状态')
    supplierid = models.CharField(max_length=16,blank=True,null=True)
    step1flag = models.CharField(max_length=16,choices=STEPFLAG,blank=True,null=True,verbose_name='第一步处理结果')
    step1ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第一步批准人')
    step1note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第一步意见')
    step2flag = models.CharField(max_length=16,choices=STEPFLAG,blank=True,null=True,verbose_name='第二步处理结果')
    step2ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第二步批准人')
    step2note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第二步意见')
    step3flag = models.CharField(max_length=16,choices=STEPFLAG,blank=True,null=True,verbose_name='第三步处理结果')
    step3ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第三步批准人')
    step3note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第三步意见')
    step4flag = models.CharField(max_length=16,choices=STEPFLAG,blank=True,null=True,verbose_name='第四步处理结果')
    step4ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第四步批准人')
    step4note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第四步意见')

    class Meta:
        verbose_name ='商品流通单'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'GoodsTransHead'

GOODSLIST= baseinfo.models.Goods.objects.filter(company=COMPANYID,flag='Y',valiflag='Y').values_list('gcode','gname')
class GoodsTransDetail(GenesisModel):
    transuuid = models.ForeignKey(GoodsTransHead,db_column='transid',on_delete=models.CASCADE,null=True,blank=True)  # Field name made lowercase.
    sukid = models.CharField(max_length=16,blank=True,null=True,verbose_name='流水单号')
    ditem = models.IntegerField(db_column='ditem',verbose_name='序号')  # Field name made lowercase.
    gcode = models.CharField(max_length=16,db_column='gcode',choices=GOODSLIST,blank=True,null=True, verbose_name='商品') # Field name made lowercase.
    goodsvaldate = models.DateField(db_column='goodsvaldate',blank=True, null=True,verbose_name='有效期')
    price = models.DecimalField(db_column='price', max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='单价')  # Field name made lowercase.
    qty = models.DecimalField(db_column='qty', max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='数量')  # Field name made lowercase.
    amount = models.DecimalField(db_column='amount', max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='金额')  # Field name made lowercase.

    class Meta:
        verbose_name='商品进出单明细'
        managed = True
        db_table = 'GoodsTransDetail'
        # unique_together = (('sukid', 'seqbar'),)

STEPS=(
    ('10','发起'),
    ('12','一级审批'),
    ('13','二级审批'),
    ('14','采购'),
    ('20','完成')
)
STEPFLAG=(
    ('AGREE','同意'),
    ('DISAGREE','不同意')
)

class GoodsTransProcess(GenesisModel):
    transuuid = models.ForeignKey(GoodsTransHead,db_column='transid',on_delete=models.CASCADE,null=True,blank=True)
    step1flag = models.CharField(max_length=16,blank=True,null=True,verbose_name='第一步处理结果')
    step1ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第一步批准人')
    step1note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第一步意见')
    step2flag = models.CharField(max_length=16,blank=True,null=True,verbose_name='第二步处理结果')
    step2ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第二步批准人')
    step2note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第二步意见')
    step3flag = models.CharField(max_length=16,blank=True,null=True,verbose_name='第三步处理结果')
    step3ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第三步批准人')
    step3note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第三步意见')
    step4flag = models.CharField(max_length=16,blank=True,null=True,verbose_name='第四步处理结果')
    step4ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='第四步批准人')
    step4note = models.CharField(max_length=128,blank=True,null=True,verbose_name='第四步意见')