from django.db import models

# Create your models here.
import baseinfo.models
from common.constants import FLAG, SALESFLAG, COMPTYPE, TTYPE,SCHEDULELIST,VIPTYPE, CASETYPE, CASESTATUS,SOURCE,SALEATR,STOREINFO,PERIOD
from common.constants import GenesisModel
from baseinfo.models import Goods,Storeinfo

class ReportPeriod(models.Model):

    reportyear  = models.CharField(max_length=8,blank=True,null=True,verbose_name='报表年份')
    reportname  = models.CharField(max_length=16,blank=True,null=True,verbose_name='报表名称')
    period = models.CharField(max_length=16,choices=PERIOD,blank=True,null=True,verbose_name='分期')
    perioddesc = models.CharField(max_length=32,blank=True,null=True,verbose_name='分期名称')
    fromdate = models.DateField(blank=True,null=True,verbose_name='开始日期')
    todate = models.DateField(blank=True,null=True,verbose_name='结束日期')

    class Meta:
        verbose_name='报表分期设置'
        verbose_name_plural='报表分期设置'
        managed = True
        db_table = 'reportperiod'

    def __str__(self):
        return self.reportname +'-'

class PeriodData(models.Model):
    reportperiod = models.ForeignKey('ReportPeriod',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='报表分期')
    company = models.CharField(max_length=16,blank=True,null=True,verbose_name='公司')
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='所属店铺')
    # storecode = models.ForeignKey(Storeinfo,db_column='storecode',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='门店')
    # goodsuuid = models.ForeignKey(Goods,db_column='goodsuuid',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='商品唯一码')
    rptcode2 = models.CharField(max_length=8,blank=True,null=True,verbose_name='分类2')
    rptcode3 = models.CharField(max_length=8,blank=True,null=True,verbose_name='功能')
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='商品')
    listflag = models.CharField(max_length=8, default='Y',blank=True,null=True,verbose_name='报表是否显示')
    costprice = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='进价')
    price = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='售价')
    iqty =models.DecimalField(max_digits=8,decimal_places=2,default=0,verbose_name='当期进货数')
    tiqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,verbose_name='转入数')
    toqty = models.DecimalField(max_digits=8,decimal_places=2,default=0,verbose_name='转出数')
    thisperiodsalesqty = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='当期销售数')
    thisperiodsalesamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='当期销售金额')
    totalsalesqty = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='当年累计销售数')
    totalsalesamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='当年累计销售金额')
    stockqty =  models.DecimalField(max_digits=8,decimal_places=4,default=0,blank=True,null=True,verbose_name='库存数')
    salespercent = models.DecimalField(max_digits=8,decimal_places=4,default=0,blank=True,null=True,verbose_name='销售进度')
    retiveiqtypercent =  models.DecimalField(max_digits=8,decimal_places=4,default=0,blank=True,null=True,verbose_name='相关进货占比')
    rativesalesqtypercent = models.DecimalField(max_digits=8,decimal_places=4,default=0,blank=True,null=True,verbose_name='相关销售数量占比')
    orderqty =  models.DecimalField(max_digits=8,decimal_places=4,default=0,blank=True,null=True,verbose_name='订货未到货数')

    class Meta:
        verbose_name='当期数据'
        verbose_name_plural='当期数据'
        managed = True
        db_table = 'perioddata'

    def __str__(self):
        return self.reportperiod.period+'-'+self.storecode.storecode +'-'+ self.gcode

    # def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
    #     self.gcode =Goods.objects.get(uuid=self.goodsuuid).gcode


class OldData(models.Model):
    storecode = models.CharField(max_length=8,choices=STOREINFO,blank=True,null=True,verbose_name='店铺')
    saleatr = models.CharField(max_length=8,choices=SALEATR,default='G',blank=True,null=True,verbose_name='类型')
    vsdate  = models.CharField(max_length=8,blank=True,null=True,verbose_name='日期')
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='商品')
    salesqty = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='数量')
    salesamount = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='金额')

    class Meta:
        verbose_name='往年销售数据'
        verbose_name_plural='往年销售数据'
        managed = True
        db_table = 'olddata'

    def __str__(self):
        if self == None:
            return ''

        return self.gcode

class GcodeMirror(models.Model):
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='系统商品编号')
    gname = models.CharField(max_length=32,blank=True,null=True,verbose_name='商品名称')
    gcode2018 = models.CharField(max_length=16,blank=True,null=True,verbose_name='2018年对应编号')
    gcode2017 = models.CharField(max_length=16,blank=True,null=True,verbose_name='2017年对应编号')
    gcode2016 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2016年对应编号')
    gcode2015 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2015年对应编号')
    gcode2014 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2014年对应编号')
    gcode2013 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2013年对应编号')
    gcode2012 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2012年对应编号')
    gcode2011 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2011年对应编号')
    gcode2010 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2010年对应编号')
    gcode2009 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2009年对应编号')
    gcode2008 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2008年对应编号')
    gcode2007 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2007年对应编号')
    gcode2006 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2006年对应编号')
    gcode2005 = models.CharField(max_length=16, blank=True, null=True, verbose_name='2005年对应编号')

    class Meta:
        verbose_name='商品编码对照表'
        verbose_name_plural='商品编码对照表'
        managed = True
        db_table = 'GcodeMirror'

    def __str__(self):
        return self.gcode + '/' + self.gname


class OldData2(models.Model):
    storecode = models.CharField(max_length=8,choices=STOREINFO,blank=True,null=True,verbose_name='店铺')
    saleatr = models.CharField(max_length=8,choices=SALEATR,default='G',blank=True,null=True,verbose_name='类型')
    vsdate  = models.CharField(max_length=8,blank=True,null=True,verbose_name='日期')
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='商品')
    salesqty = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='数量')
    salesamount = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='金额')

    class Meta:
        verbose_name='往年进货数据'
        verbose_name_plural='往年进货数据'
        managed = True
        db_table = 'olddata4'

    def __str__(self):
        if self == None:
            return ''

        return self.gcode

class OldData4(models.Model):
    storecode = models.CharField(max_length=8,choices=STOREINFO,blank=True,null=True,verbose_name='店铺')
    saleatr = models.CharField(max_length=8,choices=SALEATR,default='G',blank=True,null=True,verbose_name='类型')
    vsdate  = models.CharField(max_length=8,blank=True,null=True,verbose_name='日期')
    gcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='商品')
    salesqty = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='数量')
    salesamount = models.DecimalField(max_digits=16,decimal_places=2,blank=True,null=True,verbose_name='金额')

    class Meta:
        verbose_name='往年进货数据'
        verbose_name_plural='往年进货数据'
        managed = True
        db_table = 'olddata4'

    def __str__(self):
        if self == None:
            return ''

        return self.gcode


