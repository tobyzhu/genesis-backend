#coding = utf-8

from django.db import models
import sys
import uuid
import django.utils.timezone as timezone
from datetime import datetime

# from baseinfo.models import Storeinfo


__author__ = 'Toby Zhu'

# toby 2017-03-04: define global constants.  The domain name we use is HDMS

# toby:
# COMPANYID='youlan'
# COMPANYID='yiren'
# COMPANYID='yfy'
COMPANYID='dsdemo'

# DEMO_COMPANY='demo'
DEMO_COMPANYNAME='醉小主'
DEMO_STORECODE='88'
DEMO_STORENAME='演示门店'
DEMO_ECODE='888'
DEFAULT_VIP_PINNO='000000'
DEFAULT_VCODE_LENGTH=5
DEFAULT_CCODE_LENGTH=4

DEFAULT_NORMAL_PCODE='A'
DEFAULT_SEND_PCODE='Z'


TTYPE=(
    ('G','商品'),
    ('S','服务'),
    ('C','售卡'),
    ('I','充值'),
)


STYPE=(
    ('正常','正常'),
    ('赠送','赠送'),
)

FLAG=(
    ('Y','有效'),
    ('N','无效'),
)

COMPTYPE = (
    ('amount', '计费'),
    ('times', '计次'),
)
SALESFLAG = (
    ('Y', '可以销售'),
    ('N', '不可销售'),
)

CARDSUPTYPE=(
    ('10','储值卡'),
    ('15', '产品卡'),
    ('20','疗程卡'),
    ('30','赠送储值卡'),
    ('40','赠送疗程卡')
)

POSITION =(
    ('10','发型师'),
    ('20','技师'),
    ('30','助工'),
    ('40','其他')
)

SCHEDULELIST = (
    ('早班', '早班'),
    ('中班', '中班'),
    ('晚班', '晚班'),
    ('正常班', '正常班')
)


GOODSRPT1=(
    ('其他','其他'),
    ('','')
)

GOODSRPT2=(
    ('其他','其他'),
    ('','')
)

GOODSRPT3=(
    ('其他','其他'),
    ('','')
)

CARDTYPERPT1=(
    ('其他','其他'),
    ('','')
)



CASETYPE_VIP_BASE_MAINTAINCE    =   10
CASETYPE_NEW_VIP    =   20
CASETYPE_VIP_COMPLAIN = 30
CASETYPE_VIP_SERVIECE_RETURN_VISIT  =   40
CASETYPE_VIP_GOODS_RETURN_VISIT  =   45
CASETYPE_VIP_CARD_RETURN_VISIT  =   48

CASETYPE=(
    ('10','基础维护'),
    ('20','拓客'),
    ('30','客户投诉'),
    ('40','到店服务回访'),
    ('45','购买商品回访'),
    ('50','预约客户到店')
)

# CASETYPE=(
#     ('T10','基础维护'),
#     ('T10S','服务售后回访'),
#     ('T10G','商品售后回访'),
#     ('T10C','售卡售后回访'),
#     ('T20', '拓客'),
#     ('T30', '客户投诉'),
#     ('T50','预约客户到店')
# )

CASESTATUS=(
    ('10','未开始'),
    ('20','进行中'),
    ('30','已完成'),
    ('40','暂停')
)

VIPTYPE=(
    ('10','会员'),
    ('20','散客')
)

SOURCE=(
    ('朋友介绍','朋友介绍'),
    ('网络媒体','网络媒体'),
    ('户外媒体','户外媒体'),
    ('合作伙伴','合作伙伴'),
    ('朋友圈','朋友圈'),
    ('路过','路过'),
    ('其他','其他')
)

SALEATR=(
    ('G','销售'),
    ('I','进货'),
    ('O','出货'),
    ('F','退货'),
    ('U','领用'),
    ('C','盘点'),
    ('TI','转入'),
    ('TO','转出'),
    ('SL','申领单'),
    ('CG','采购单')
)

COMPANYLIST=(
    ('01','新红妆'),
    ('02','居明居'),
    ('youlan','杭州幽兰'),
    ('yfy','雅芳亚'),
    ('yiren','伊人')
)

STOREINFO = (
    ('000','总部'),
    ('001','杭州大厦店'),
    ('002','万象城店'),
)

PERIOD = (
    ('01', '01期'),
    ('02', '02期'),
    ('03', '03期'),
    ('04', '04期'),
    ('05', '05期'),
    ('06', '06期'),
    ('07', '07期'),
    ('08', '08期'),
    ('09', '09期'),
    ('10', '10期'),
    ('11', '11期'),
    ('12', '12期'),
    ('13', '13期'),
    ('14', '14期'),
    ('15', '15期'),
    ('16', '16期'),
    ('17', '17期'),
    ('18', '18期'),
    ('19', '19期'),
    ('20', '20期'),
    ('21', '21期'),
    ('22', '22期'),
    ('23', '23期'),
    ('24', '24期'),
    ('25', '25期'),
    ('26', '26期'),
    ('27', '27期'),
    ('28', '28期'),
    ('29', '29期'),
    ('30', '30期'),
)

ARCHIVEMENTTYPE=(
    ('100','正常服务'),
    ('130','正常销售'),
    ('110','正常储值卡'),
    ('120','正常疗程卡'),
    ('1DX','大项'),
    ('10PS','赠送服务'),
    ('10PG','赠送销售'),
    ('10PC','赠送卡'),
)

DISCOUNTCLASS=(
    ('10','按会员卡打折项目'),
    ('20','特殊折扣1'),
    ('30','特殊折扣2'),
    ('50','不打折项目'),
    ('90','其他')
)

MARKET_ITEM_CLASS1=[
    ('1001','拓客项目'),
    ('1002','留客项目'),
    ('1003','升客项目'),
    ('1004','挖客项目'),
    ('1090','其他')
]

MARKET_ITEM_CLASS2=(
    ('10','基础项目'),
    ('20','大项目'),
    ('30','合作项目'),
    ('80','医美'),
    ('90','其他'),
)

MARKET_ITEM_CLASS3=(
    ('10','无差别类项目'),
    ('20','必备类项目'),
    ('30','一维类项目'),
    ('40','魅力类项目'),
    ('90','其他')
)

ITEMCLASS4=(
    ('',''),
    ('','')
)

FINANCE_ITEM_CLASS1=(
    ('10','正常'),
    ('20','其他')
)

FINANCE_ITEM_CLASS2=(
    ('10','正常'),
    ('20','其他')
)



# TAGS=()
# VIPTAGS=()

VIPSTATUS=(
    ('010','有效会员'),
    ('020','警示会员'),
    ('030','流失会员'),
    ('120','潜在客户'),
    ('110','体验客户'),
    ('190','体验失败客户')
)


COMPANYLIST_WITHOUT_MTCODE = ['yiren']

CAN_CHECKOUT_FLAG='70'



class GenesisModel(models.Model):
    # STORECODE = Storeinfo.objects.filter(company=COMPANYID).values_list('storecode','storename')
    uuid = models.UUIDField(primary_key=True,auto_created=True,editable=False,default=uuid.uuid4,null=False,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name='建立时间')
    last_modified = models.DateTimeField(auto_created=True,default=timezone.now,editable=False,verbose_name='最后修改时间')
    creater = models.CharField(max_length=16,default='anonymous',editable=False,blank=True,null=True,verbose_name='创建者')
    flag = models.CharField(max_length=8,choices=FLAG,default='Y',editable=False,blank=True,null=True,verbose_name='是否删除')
    company = models.CharField(max_length=8,default=COMPANYID,null=True,editable=False,blank=True,verbose_name='公司')
    storecode = models.CharField(max_length=16,blank=True,null=True,editable=False,verbose_name='门店')

    class Meta:
        abstract=True

    def delete(self, using=None, keep_parents=False):
        self.flag='N'
        self.save()

    def create_date(self):
        return datetime.strftime(self.create_time,'%Y%m%d')
    # def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
    #     self.last_modified=datetime.now()
    #     self.save()

class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True,auto_created=True,editable=False,default=uuid.uuid4,null=False,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name='建立时间')
    last_modified = models.DateTimeField(auto_created=True,default=timezone.now,editable=False,verbose_name='最后修改时间')
    creater = models.CharField(max_length=16,default='anonymous',blank=True,null=True,verbose_name='创建者')
    flag = models.CharField(max_length=8,choices=FLAG,default='Y',editable=False,blank=True,null=True,verbose_name='是否删除')
    company = models.CharField(max_length=8,default=COMPANYID,null=True,blank=True,verbose_name='公司')
    # storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')

    class Meta:
        abstract=True

    def delete(self, using=None, keep_parents=False):
        self.flag='N'
        self.save()

class CommonBaseModel(models.Model):
    # uuid = models.UUIDField(primary_key=True,auto_created=True,editable=False,default=uuid.uuid4,null=False,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name='建立时间')
    last_modified = models.DateTimeField(auto_created=True,default=timezone.now,editable=False,verbose_name='最后修改时间')
    creater = models.CharField(max_length=16,default='anonymous',blank=True,null=True,verbose_name='创建者')
    flag = models.CharField(max_length=8,choices=FLAG,default='Y',editable=False,blank=True,null=True,verbose_name='是否删除')
    # company = models.CharField(max_length=8,default=COMPANYID,null=True,blank=True,verbose_name='公司')
    # storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')

    class Meta:
        abstract=True

    def delete(self, using=None, keep_parents=False):
        self.flag='N'
        self.save()

class CompanyCommonBaseModel(models.Model):
    # uuid = models.UUIDField(primary_key=True,auto_created=True,editable=False,default=uuid.uuid4,null=False,blank=True)
    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='建立时间')
    last_modified = models.DateTimeField(auto_created=True, default=timezone.now, editable=False,
                                         verbose_name='最后修改时间')
    creater = models.CharField(max_length=16, default='anonymous', blank=True, null=True, verbose_name='创建者')
    flag = models.CharField(max_length=8, choices=FLAG, default='Y', editable=False, blank=True, null=True,
                            verbose_name='是否删除')
    company = models.CharField(max_length=8,default=COMPANYID,null=True,blank=True,verbose_name='公司')
    # storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.flag = 'N'
        self.save()

class StoreCommonBaseModel(CompanyCommonBaseModel):
    storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.flag = 'N'
        self.save()
