from django.db import models
from multiselectfield import MultiSelectField

import common.constants
import baseinfo.models

from common.constants import GenesisModel,BaseModel

# Create your models here
# .
FINANCE_YEAR_1ST_MONTH = 1
FINANCE_MONTH_1ST_DAY = 1


class ReportBase(models.Model):
    company = models.CharField(max_length=16,blank=True,null=True,verbose_name='公司')
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')
    storeuuid = models.ForeignKey(baseinfo.models.Storeinfo,db_column='storeuuid',blank=True,null=True,verbose_name='店铺')

    class Meta:
        abstract = True


class YearReport(ReportBase):
    reportyear = models.CharField(max_length=8,blank=True,null=True,verbose_name='年')

    class Meta:
        abstract = True

class MonthReport(YearReport):
    reportmonth = models.CharField(max_length=8,blank=True,null=True,verbose_name='月')

    class Meta:
        abstract = True

class DailyReport(MonthReport):
    reportdate = models.CharField(max_length=8,blank=True,null=True,verbose_name='日期')

    class Meta:
        abstract = True

class DateRange(models.Model):
    fromdate = models.DateField(auto_now=False,auto_now_add=False,verbose_name='开始日期')
    todate = models.DateField(auto_now=False,auto_now_add=False,verbose_name='截止日期')

    class Meta:
        abstract=True



class DailyReportVip(GenesisModel):
    vipuuid = models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,verbose_name='会员')
    vsdate = models.CharField(max_length=8,blank=True,null=True,verbose_name='日期')
    vipqty =models.IntegerField(default=1,blank=True,null=True,verbose_name='客户数量')
    newvipflag = models.CharField(max_length=8,blank=True,null=True,verbose_name='是否新客')
    friendqty = models.IntegerField(default=0,blank=True,null=True,verbose_name='同行朋友数量')
    friendsuuid= models.CharField(max_length=32,blank=True,null=True,verbose_name='同行朋友')

    class Meta:
        verbose_name='会员到店数量报表'
        verbose_name_plural=verbose_name
        managed=True
        db_table='dailyreportvip'

    def __init__(self):
        return self.vipuuid.vname+ '-'+self.vsdate

    def addqty(self,qty):
        self.qty = self.qty +qty
        self.save()

class Report(GenesisModel):
    reportId = models.CharField(max_length=128, blank=True, null=True, verbose_name='报表编号')
    reportName = models.CharField(max_length=128, blank=True, null=True, verbose_name='报表名称')

    class Meta:
        verbose_name='Genesis报表'
        verbose_name_plural=verbose_name
        managed=True
        db_table='report'

class Report_Item_Ruler(GenesisModel):
    report_item_ruler_id = models.CharField(max_length=16,blank=True,null=True,verbose_name='报表项计算规则ID')
    report_item_ruler = models.TextField(blank=True,null=True,verbose_name='报表项计算规则')

    class Meta:
        verbose_name='Genesis报表项次计算'
        verbose_name_plural=verbose_name
        managed=True
        db_table='report_item_ruler'


class ReportItem(models.Model):
    REPORTITEM_TYPE = (
        ('交易', '交易数据'),
        ('公式', '公式'),
        ('其他', '其他')
    )

    report_uuid = models.ForeignKey('Report',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='报表')
    report_item_id = models.CharField(max_length=64,blank=True,null=True,verbose_name='报表项次')
    report_item_name = models.CharField(max_length=64,blank=True,null=True,verbose_name='项次名称')
    report_item_type = models.CharField(max_length=16,choices=REPORTITEM_TYPE,blank=True,null=True,verbose_name='项次类型')
    report_item_rulers=models.CharField(max_length=256,blank=True,null=True,verbose_name='取值规则')
    report_item_group=models.CharField(max_length=128,blank=True,null=True,verbose_name='项次分组')
    report_item_order=models.CharField(max_length=8,blank=True,null=True,verbose_name='排序')
    report_item_visible = models.CharField(max_length=8,blank=True,null=True,verbose_name='是否显示')
    report_item_decimal_place =models.IntegerField(default=2,verbose_name='小数点位数')

    class Meta:
        verbose_name='报表项次'
        verbose_name_plural=verbose_name
        managed=True
        db_table='report_item'

class ReportItemData(models.Model):
    report_item_uuid = models.ForeignKey('ReportItem',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='报表项次')
    report_item_qty = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='数量')
    report_item_amount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='金额')


class DailyReportNo1(DailyReport):
    vipcnt = models.DecimalField(max_digits=8,decimal_places=0,default=0,blank=True,null=True,verbose_name='到店客数')
    newvipcnt = models.DecimalField(max_digits=8, decimal_places=0, default=0, blank=True, null=True, verbose_name='新客数')
    newvipwithcardcnt = models.DecimalField(max_digits=8, decimal_places=0, default=0, blank=True, null=True, verbose_name='新客入会数')
    newvipamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='新客现金')
    vipcnt_s =  models.DecimalField(max_digits=8,decimal_places=0,default=0,blank=True,null=True,verbose_name='服务客数')
    vipcnt_g =  models.DecimalField(max_digits=8,decimal_places=0,default=0,blank=True,null=True,verbose_name='商品客数')
    vipcnt_c =  models.DecimalField(max_digits=8,decimal_places=0,default=0,blank=True,null=True,verbose_name='购卡客数')
    vipcnt_i =  models.DecimalField(max_digits=8,decimal_places=0,default=0,blank=True,null=True,verbose_name='充值客数')
    shouru_samount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='服务收入')
    shouru_gamount = models.DecimalField(max_digits=16, decimal_places=2, default=0,blank=True, null=True,verbose_name='商品收入')
    shouru_camount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='卡收入')
    shihao_samount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='服务实耗')
    shihao_gamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='商品实耗')
    cash_samount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='现金服务')
    cash_gamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='现金商品')
    cash_camount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='现金售卡/充值')
    card_samount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='卡付服务')
    card_gamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='卡付商品')
    card_camount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='卡付售卡/充值')
    send_samount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='赠送服务')
    send_gamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='赠送商品')
    send_camount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,verbose_name='赠送售卡/充值')
    # daxian_amount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='大项业绩')
    # shihao_baseitem

    class Meta:
        verbose_name='1号日报表'
        verbose_name_plural='1号日报表'
        managed=True
        db_table='dailyreportno1'

    def get_data(self):
        company=self.company
        storecode=self.storecode
        vsdate=self.financedate


class ReportClassData(DailyReport):
    REPORT_TYPE=(
        ('empl','员工'),
        ('store','门店'),
        ('vip','会员')
    )
    DATARANGE = (
        ('daily', '日'),
        ('month', '月'),
        ('year', '年'),
        ('period', '期间')
    )

    REPORT_CLASS_TYPE = baseinfo.models.DISPLAYCLASS1 | baseinfo.models.DISPLAYCLASS2 \
                        | baseinfo.models.MARKETCLASS1 | baseinfo.models.MARKETCLASS2 | baseinfo.models.MARKETCLASS3 | baseinfo.models.MARKETCLASS4 \
                        | baseinfo.models.FINANCECLASS1 | baseinfo.models.FINANCECLASS2
    report_type = models.CharField(max_length=16,choices=REPORT_TYPE,blank=True,null=True,verbose_name='报表类别')
    empl = models.ForeignKey(baseinfo.models.Empl,db_column='empluuid',blank=True,null=True,verbose_name='员工')
    ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='员工工号')
    vip = models.ForeignKey(baseinfo.models.Vip,db_column='vipuuid',blank=True,null=True,verbose_name='客户')
    vcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='会员号')
    datarang = models.CharField(max_length=16,choices=DATARANGE,blank=True,null=True,verbose_name='数据日期范围')
    report_class_type = models.CharField(max_length=32,choices=REPORT_CLASS_TYPE,blank=True,null=True,verbose_name='分类')
    report_class_code = models.CharField(max_length=32,blank=True,null=True,verbose_name='分类编码')
    ttype = models.CharField(max_length=16,blank=True,null=True,verbose_name='交易类型')
    qty = models.DecimalField(max_digits=16,decimal_places=0,default=0,blank=True,null=True,verbose_name='数量')
    amount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='金额')

    class Meta:
        verbose_name='每日数据'
        verbose_name_plural='每日数据'
        managed=True
        db_table='reportclassdata'

    def set_data(self):
        if self.datarang=='daily':
            class_type = self.report_class_type
            class_code = self.report_class_code
            vsdate= self.reportdate


# class DailyMarketClass1(DailyReport):
#     itemclass1 = models.CharField(max_length=16,choices=common.constants.MARKET_ITEM_CLASS1,blank=True,null=True,verbose_name='营销分类1')
#     vipcnt = models.DecimalField(max_digits=16,decimal_places=0,default=0,blank=True,null=True,verbose_name='人数')
#     itemqty = models.DecimalField(max_digits=16,decimal_places=0,default=0,blank=True,null=True,verbose_name='数量')
#     itemamount = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='金额')
#
#     class Meta:
#         verbose_name='项目管理1号报表'
#         verbose_name_plural='项目管理2号报表'
#         managed=True
#         db_table='dailymarketclass1'


# class DailyItemClass2Report(DailyReport):
#     itemclass2 = models.CharField(max_length=16, choices=common.constants.MARKET_ITEM_CLASS1, blank=True, null=True,
#                                   verbose_name='项目分类2')
#     vipcnt = models.DecimalField(max_digits=16,decimal_places=0,default=0,blank=True,null=True,verbose_name='人数')
#     itemqty = models.DecimalField(max_digits=16, decimal_places=0, default=0, blank=True, null=True, verbose_name='数量')
#     itemamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                      verbose_name='金额')


# class DailyItemClass3Report(DailyReport):
#     itemclass1 = models.CharField(max_length=16, choices=common.constants.MARKET_ITEM_CLASS1, blank=True, null=True,
#                                   verbose_name='项目分类3')
#     itemqty = models.DecimalField(max_digits=16, decimal_places=0, default=0, blank=True, null=True, verbose_name='数量')
#     itemamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                      verbose_name='金额')


# class DailyItemClass4Report(DailyReport):
#     itemclass1 = models.CharField(max_length=16, choices=common.constants.ITEMCLASS4, blank=True, null=True,
#                                   verbose_name='项目分类4')
#     itemqty = models.DecimalField(max_digits=16, decimal_places=0, default=0, blank=True, null=True, verbose_name='数量')
#     itemamount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                      verbose_name='金额')

# class MonthReportNo1(MonthReport):
#
#
# class EmplPaySheetPerc(common.constants.GenesisModel):
#     storelist = MultiSelectField(choices=common.constants.STOREINFO,blank=True,null=True,verbose_name='可用门店')
#     position = models.CharField(max_length=16,blank=True,null=True,verbose_name='职位')
#     s_cash_perc = models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='服务现金提点')
#     g_cash_perc = models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='产品现金提点')
#     c_cash_perc = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='售卡现金提点')
#     s_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='服务实耗提点')
#     g_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='产品实耗提点')
#     c_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='卡项实耗提点')
#     fromdate = models.DateField(verbose_name='开始有效日期')
#     todate = models.DateField(verbose_name='结束有效日期')
#
#     class Meta:
#         managed = True
#         db_table = 'emplpaysheetperc'
#         verbose_name = '提成比率'
#         verbose_name_plural = '提成比率'
#
#     def __str__(self):
#         return self.company + self.position
#
# class EmplPaySheet(DailyReport):
#     empl = models.ForeignKey(baseinfo.models.Empl,blank=True,null=True,verbose_name='员工')
#     ecode = models.CharField(max_length=32,blank=True,null=True,verbose_name='员工工号')
#     basicwage=models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='基本工资')
#     s_cash_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='服务现金业绩')
#     s_cash_perc = models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='服务现金提点')
#     g_cash_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='产品现金业绩')
#     g_cash_perc = models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='产品现金提点')
#     c_cash_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='卡项现金业绩')
#     c_cash_perc = models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='售卡现金提点')
#     s_consume_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='服务实耗业绩')
#     s_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='服务实耗提点')
#     g_consume_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='产品实耗业绩')
#     g_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='产品实耗提点')
#     c_consume_archivement = models.DecimalField(max_digits=16,decimal_places=2,default=0,verbose_name='卡项实耗业绩')
#     c_consume_perc =  models.DecimalField(max_digits=4,decimal_places=2,default=0,verbose_name='售卡实耗提点')
#
#     class Meta:
#         verbose_name='员工每日业绩表'
#         verbose_name_plural='员工每日业绩表'
#         managed = True
#         db_table='emplpaysheet'
#

class MonthlyReportNo1(MonthReport):
    initial_leftmoney = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='期初卡余额')
    cashpay_c = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='本期入卡先进')
    cashpay_s = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='本期现金服务')
    cashpay_g = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True, verbose_name='本期现金商品')
    cardpay_s = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='本期卡付服务')
    cardpay_g = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True, verbose_name='本期卡付商品')
    last_leftmoney = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='本期卡付服务')

    class Meta:
        verbose_name='月度报表一'
        verbose_name_plural=verbose_name
        managed=True
        db_table='monthlyreportno1'



