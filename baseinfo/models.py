#coding = utf-8

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
import uuid
from pypinyin import pinyin,lazy_pinyin,Style

from common.constants import FLAG,SALESFLAG,COMPTYPE,TTYPE,STYPE,CASETYPE,CASESTATUS,VIPTYPE,DEFAULT_VCODE_LENGTH,DEFAULT_CCODE_LENGTH
from common.constants import GenesisModel,BaseModel,CommonBaseModel
import common.constants
from multiselectfield import MultiSelectField
from .tools import set_mnemoniccode,main
# from cashier.models import Expvstoll,Expense
# from adviser.models import  *
from adviser.models import Cardinfo
# from wechat.models import WechatUser
# from baseinfo.admin import AdminModel


SEGS=[
    ('viplevel','会员级别'),
    ('brand','品牌'),
    ('tags','标签'),
    ('financeclass1','财务分类（一）'),
    ('financeclass2', '财务分类（二）'),
    # ('marketclass1','营销分类1'),
    ('displayclass1','显示分类(方法一)'),
    ('displayclass2', '显示分类(方法二)'),
    ('bodyparts1','身体部位'),
    ('marketclass1','营销分类(一)'),
    ('marketclass2', '营销分类(二)'),
    ('marketclass3', '营销分类(三）'),
    ('marketclass4','项目分类4'),
    ('source','来店渠道'),
    ('archivementclass1','业绩分类（一）'),
    ('casetype','回访类型'),
    ('unit','单位')
]

class Appoption(GenesisModel):
    seg = models.CharField(max_length=40,choices=SEGS,verbose_name='类别')
    itemname = models.CharField(max_length=40,verbose_name='编码')
    itemvalues = models.CharField(max_length=200, blank=True, null=True,verbose_name='名称')
    itemvalues2 = models.CharField(max_length=200, blank=True, null=True)
    itemvalues3 = models.CharField(max_length=200, blank=True, null=True)
    itemvalues4 = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name='系统配置'
        verbose_name_plural='系统配置'
        managed = True
        db_table = 'appoption'
        unique_together = (('company','seg', 'itemname'),)

COMPANY=common.constants.COMPANYID
BRAND = Appoption.objects.filter(company=COMPANY,flag='Y',seg='brand').values_list('itemname','itemvalues')
VIPLEVEL =  Appoption.objects.filter(company=COMPANY,flag='Y',seg='viplevel').values_list('itemname','itemvalues')
DISCOUNTCLASS= Appoption.objects.filter(company=COMPANY,flag='Y',seg='discountclass').values_list('itemname','itemvalues')

DISPLAYCLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='displayclass1').values_list('itemname','itemvalues')
DISPLAYCLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='displayclass2').values_list('itemname','itemvalues')

SRVDISPLAYCLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='srvdisplayclass1').values_list('itemname','itemvalues')
SRVDISPLAYCLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='srvdisplayclass2').values_list('itemname','itemvalues')

GOODSDISPLAYCLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='goodsdisplayclass1').values_list('itemname','itemvalues')
GOODSDISPLAYCLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='goodsdisplayclass2').values_list('itemname','itemvalues')

CARDTYPEDISPLAYCLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='cardtypedisplayclass1').values_list('itemname','itemvalues')
CARDTYPEDISPLAYCLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='cardtypedisplayclass2').values_list('itemname','itemvalues')

MARKETCLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='marketclass1').values_list('itemname','itemvalues')
MARKETCLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='marketclass2').values_list('itemname','itemvalues')
MARKETCLASS3= Appoption.objects.filter(company=COMPANY,flag='Y',seg='marketclass3').values_list('itemname','itemvalues')
MARKETCLASS4= Appoption.objects.filter(company=COMPANY,flag='Y',seg='marketclass4').values_list('itemname','itemvalues')
FINANCECLASS1= Appoption.objects.filter(company=COMPANY,flag='Y',seg='financeclass1').values_list('itemname','itemvalues')
FINANCECLASS2= Appoption.objects.filter(company=COMPANY,flag='Y',seg='financeclass2').values_list('itemname','itemvalues')
ARCHIVEMENTCLASS1 = Appoption.objects.filter(company=COMPANY,flag='Y',seg='archivementclass1').values_list('itemname','itemvalues')
ARCHIVEMENTCLASS2 = Appoption.objects.filter(company=COMPANY,flag='Y',seg='archivementclass2').values_list('itemname','itemvalues')
BODYPARTS1 = Appoption.objects.filter(company=COMPANY,flag='Y',seg='bodyparts1').values_list('itemname','itemvalues')
BODYPARTS2 = Appoption.objects.filter(company=COMPANY,flag='Y',seg='bodyparts2').values_list('itemname','itemvalues')
TAGS = Appoption.objects.filter(company=COMPANY,flag='Y',seg='tags').values_list('itemname','itemvalues')
VIPTAGS = Appoption.objects.filter(company=COMPANY,flag='Y',seg='viptags').values_list('itemname','itemvalues')
SOURCE= Appoption.objects.filter(company=COMPANY,flag='Y',seg='source').values_list('itemname','itemvalues')

COMPANYLIST= Appoption.objects.filter(flag='Y',company='common',seg='company').values_list('itemname','itemvalues')
COMPANY_PAY_PERIOD = Appoption.objects.filter(flag='Y',company='common',seg='company_pay_period').values_list('itemname','itemvalues')
UNITS = Appoption.objects.filter(flag='Y',company='common',seg='unit').values_list('itemname','itemvalues')
SALEATR = Appoption.objects.filter(flag='Y',company='common',seg='saleatr').values_list('itemname','itemvalues')


class Storeinfo(BaseModel):
    # storecode = models.CharField(db_column='StoreCode', default='0',max_length=16,blank=True,null=False,verbose_name='店铺编号')  # Field name made lowercase.
    storecode = models.CharField(db_column='StoreCode', default='0',max_length=16,blank=True,null=False,verbose_name='店铺编号')  # Field name made lowercase.
    storename = models.CharField(db_column='StoreName', max_length=40, blank=True, null=True,verbose_name='店铺名称')  # Field name made lowercase.
    dsn = models.CharField(db_column='DSN', max_length=20, blank=True, null=True,verbose_name='DSN')  # Field name made lowercase.
    database = models.CharField(db_column='database',max_length=16,blank=True,null=True,verbose_name='数据库名称')
    precode = models.CharField(db_column='preCode', max_length=8, blank=True, null=True,verbose_name='卡号前缀')  # Field name made lowercase.
    areacode = models.CharField(max_length=16, blank=True, null=True,verbose_name='所属地区')
    company = models.CharField(max_length=16, blank=True, null=True,verbose_name='所属公司')
    invoicealter = models.CharField(db_column='invoicealter', max_length=8, default='N',blank=True, null=True,verbose_name='直接打印提示')  # Field name made lowercase.
    salewhcode = models.CharField(db_column='salewhcode', max_length=16, blank=True, null=True,verbose_name='销售品仓库')  # Field name made lowercase.
    invoicetitle1 = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票抬头')
    invoicetitle2 = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票抬头')
    invoicefoot1 = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票页脚')
    invoicefoot2 = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票页脚')
    usewhcode = models.CharField(max_length=16, blank=True, null=True,verbose_name='使用品仓库')
    hdflag = models.CharField(max_length=8,choices=FLAG,default='N',blank=True,null=True,verbose_name='是否总部')
    rooms = models.DecimalField(max_digits=16,decimal_places=2,default=1,blank=True,null=True,verbose_name='房间数')
    measureofarea = models.DecimalField(max_digits=16,decimal_places=2,default=1,blank=True,null=True,verbose_name='经营面积')
    pmcodes = models.DecimalField(max_digits=8,decimal_places=2,default=1,blank=True,null=True,verbose_name='顾问人数')
    seccodes = models.DecimalField(max_digits=8,decimal_places=2,default=1,blank=True,null=True,verbose_name='美疗师人数')
    validyvipcnt = models.DecimalField(max_digits=8,decimal_places=2,default=1,blank=True,null=True,verbose_name='有效会员')
    storetype = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店类型')
    service_due_date = models.DateField(auto_now=False,auto_created=False,auto_now_add=False,blank=True,null=True,verbose_name='服务最后日期')
    pay_buffer_days = models.IntegerField(default=0,blank=True,null=True,verbose_name='付费缓冲日')
    pay_period = models.CharField(max_length=16,choices=COMPANY_PAY_PERIOD,blank=True,null=True,verbose_name='付款周期')

    class Meta:
        verbose_name='门店设定'
        verbose_name_plural='门店设定'
        managed = True
        db_table = 'storeinfo'
        unique_together = ("company", "storecode")

    def __str__(self):
        return self.storename

STOREINFO = Storeinfo.objects.filter(company=common.constants.COMPANYID).values_list('storecode','storename')

class BankAccount(BaseModel):
    accountcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='编号')
    accountname = models.CharField(max_length=128,blank=True,null=True,verbose_name='账号名称')
    bankname = models.CharField(max_length=128,blank=True,null=True,verbose_name='开户银行')
    accountnumber = models.CharField(max_length=128,blank=True,null=True,verbose_name='银行账号')
    accountdesc = models.CharField(max_length=128,blank=True,null=True,verbose_name='描述')
    status = models.CharField(max_length=128,blank=True,null=True,verbose_name='状态')
    storelist = MultiSelectField(choices=STOREINFO,blank=True,null=True,verbose_name='可用门店')

    class Meta:
        verbose_name='账户设定'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'bankaccount'

    def __str__(self):
        return self.accountname

class Tags(models.Model):
    tag =models.CharField(max_length=16,primary_key=True,verbose_name='标签')

    class Meta:
        verbose_name_plural = '标签'
        verbose_name = '标签'
        managed = True
        db_table = 'tags'

    def __str__(self):
        return self.tag

class VipTags(models.Model):
    tag = models.CharField(max_length=16,primary_key=True,verbose_name='客户标签')

    class Meta:
        verbose_name_plural = '客户标签'
        verbose_name = '客户标签'
        managed = True
        db_table = 'viptags'

    def __str__(self):
        return self.tag

class ItemModel(models.Model):
    srvrptypecode = models.CharField(max_length=8,blank=True,null=True,verbose_name='报表分类')
    brand = models.CharField(max_length=16,choices=BRAND, blank=True,null=True,verbose_name='品牌')
    discountclass = models.CharField(max_length=16,default='',blank=True,null=True,verbose_name='折扣分类')
    displayclass1 = models.CharField(max_length=16,choices=DISPLAYCLASS1,default='',blank=True,null=True,verbose_name='显示分类（方法一）')
    displayclass2 = models.CharField(max_length=16,choices=DISPLAYCLASS2,default='',blank=True,null=True,verbose_name='显示分类（方法二）')
    marketclass1 = models.CharField(max_length=16,choices=MARKETCLASS1,default='',blank=True,null=True,verbose_name='项目营销分类（方法一）')
    marketclass2 = models.CharField(max_length=16,choices=MARKETCLASS2,default='',blank=True,null=True,verbose_name='项目营销分类（方法二）')
    marketclass3 = models.CharField(max_length=16,choices=MARKETCLASS3,default='',blank=True,null=True,verbose_name='项目营销分类（方法三）')
    marketclass4 = MultiSelectField(max_length=128,choices=MARKETCLASS4,default='',blank=True,null=True,verbose_name='项目营销分类（方法四）')
    financeclass1 = models.CharField(max_length=16,choices=FINANCECLASS1,default='',blank=True,null=True,verbose_name='项目财务分类1')
    financeclass2 = models.CharField(max_length=16,choices=FINANCECLASS2,default='',blank=True,null=True,verbose_name='项目财务分类2')
    archivementclass1 = models.CharField(max_length=16,choices=ARCHIVEMENTCLASS1,default='',blank=True,null=True,verbose_name='业绩分类1')
    archivementclass2 = models.CharField(max_length=16,choices=ARCHIVEMENTCLASS2,default='',blank=True,null=True,verbose_name='业绩分类2')
    bodyparts1 = MultiSelectField(max_length=128,choices=BODYPARTS1,default='',blank=True,null=True,verbose_name='身体部位')
    saleflag = models.CharField(max_length=8,choices=FLAG,default='Y',blank=True,null=True,verbose_name='可否销售')
    valiflag = models.CharField(max_length=8,choices=FLAG,default='Y',blank=True,null=True,verbose_name='是否有效')
    pricechangeable = models.CharField(max_length=8, default='Y',choices=FLAG,blank=True, null=True,verbose_name='可否修改价格')
    price = models.DecimalField(max_digits=16, decimal_places=2, default=0,blank=True, null=True,verbose_name='价格')
    price2 = models.DecimalField(max_digits=16, decimal_places=2, default=0,blank=True, null=True,verbose_name='第二价格')
    price3 = models.DecimalField(max_digits=16, decimal_places=2, default=0,blank=True, null=True,verbose_name='第三价格')
    price4 = models.DecimalField(max_digits=16, decimal_places=2, default=0,blank=True, null=True,verbose_name='第四价格')
    pricecurrency = models.CharField(max_length=8, default='RMB', blank=True, null=True,verbose_name='币别')
    intervalday = models.IntegerField(default=7, blank=True, null=True,verbose_name='建议间隔天数')
    rptcode1 = models.CharField(max_length=16, blank=True, null=True)
    rptcode2 = models.CharField(max_length=16, blank=True, null=True)
    rptcode3 = models.CharField(max_length=16, blank=True, null=True)
    rptcode4 = models.CharField(max_length=16, blank=True, null=True)
    rptcode5 = models.CharField(max_length=16, blank=True, null=True)
    rptcode6 = models.CharField(max_length=16, blank=True, null=True)
    ttype = models.CharField(max_length=16,choices=TTYPE,blank=True,null=True,verbose_name='商品/服务')
    after_sales_scheme = models.CharField(max_length=64,blank=True,null=True,verbose_name='售后服务方案')
    tags = MultiSelectField(choices=TAGS,max_length=128,blank=True,null=True,verbose_name='标签')
    mnemoniccode=models.CharField(max_length=16,blank=True,null=True,verbose_name='助记码')
    storelist = MultiSelectField(choices=STOREINFO,blank=True,null=True,verbose_name='可用门店')
    # itemtags= models.ManyToManyField(Tags,verbose_name='项目标签')

    class Meta:
        abstract=True

    def get_brand_list(self):
        brandlist = Appoption.objects.filter(company=self.company, flag='Y', seg='brand').values_list(
            'itemname', 'itemvalues')
        print('brand list:', brandlist)
        return brandlist

    def __init1__(self, *args, **kwargs):
        print("1",args)
        print("2",kwargs)
        super(ItemModel, self).__init__(*args, **kwargs)
        self._meta.get_field('brand').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='brand').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('displayclass1').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='displayclass1').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('displayclass2').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='displayclass2').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('marketclass1').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='marketclass1').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('marketclass2').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='marketclass2').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('marketclass3').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='marketclass3').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('marketclass4').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='marketclass4').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('financeclass1').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='financeclass1').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('financeclass2').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='financeclass2').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('archivementclass1').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='archivementclass1').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('archivementclass2').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='archivementclass2').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('bodyparts1').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='bodyparts1').values_list( 'itemname', 'itemvalues')
        self._meta.get_field('tags').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='tags').values_list( 'itemname', 'itemvalues')

        self._meta.get_field('storelist').choices = Storeinfo.objects.filter(company=self.company, flag='Y').values_list( 'storecode', 'storename')

    # def brandname(self):
    #     item = Appoption.objects.filter(company=common.constants.COMPANYID,flag='Y',seg='brand',itemname=self.brand).last()
    #     if len(item) == 0:
    #         return ''
    #     else:
    #         return item.itemvalues

    # def displayclass1name(self):
    #     item = Appoption.objects.filter(company=common.constants.COMPANYID,flag='Y',seg='displayclass1',itemname=self.brand).last()
    #     if len(item) == 0:
    #         return ''
    #     else:
    #         return item.itemvalues
    #     return ''

class ArchivementBaseModel(models.Model):
    achivementcost= models.DecimalField(max_digits=8,decimal_places=2,default=0,blank=True,null=True,verbose_name='业绩固定成本扣除')
    pmperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='顾问提成率')
    pmguideperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='顾问营业额拆分率')
    pmpoint = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True,default=0,verbose_name='顾问提成')
    secperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='美疗师1提成率')
    secguideperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='美疗师1营业额拆分率')
    secpoint = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True,default=0,verbose_name='赠送美疗师提成')
    thrperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='美疗师2提成率')
    thrguideperc = models.DecimalField(max_digits=5,decimal_places=4,blank=True,null=True,default=0,verbose_name='美疗师2营业额拆分率')
    thrpoint = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True,default=0,verbose_name='美疗师2提成')
    basenum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='顾问提成基数')
    secbasenum = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True,verbose_name='美容师提成基数')
    thrbasenum = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True,verbose_name='美容师2提成基数')
    presentpoint = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True,verbose_name='赠送1美疗师提成')

    class Meta:
        abstract=True

class Paymode(GenesisModel):
    ISCASH=(
        ('0','卡付类'),
        ('1','现金类'),
        ('2','赠送类'),
    )
    pcode = models.CharField(db_column='PCODE', max_length=16,verbose_name='编码')  # Field name made lowercase.
    pname = models.CharField(db_column='PNAME', max_length=20, blank=True, null=True,verbose_name='付款名称')  # Field name made lowercase.
    sysflag = models.CharField(db_column='SYSFLAG', max_length=1, blank=True, null=True)  # Field name made lowercase.
    changfalg = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    iscash = models.CharField(max_length=2, choices=ISCASH,blank=True, null=True,verbose_name='是否现金')
    currency = models.CharField(max_length=8, default='RMB',blank=True, null=True,verbose_name='币别')
    rate = models.DecimalField(max_digits=10, decimal_places=4, default=1,blank=True, null=True,verbose_name='汇率')
    guideperc = models.DecimalField(max_digits=10, decimal_places=4, default=1,blank=True, null=True,verbose_name='员工业绩折算率')

    class Meta:
        verbose_name='付款方式'
        verbose_name_plural='付款方式'
        managed = True
        db_table = 'paymode'
        ordering=['pcode',]
        unique_together = ("company", "pcode")

    # def __unicode__(self):
    #     return u'%s' %self.pname

    def __str__(self):
        return self.pname

class Brand(GenesisModel):
    brand = models.CharField(max_length=16,blank=False,verbose_name='品牌')

    class Meta:
        verbose_name_plural = '品牌'
        verbose_name = '品牌'
        managed = True
        db_table = 'brand'

class ItemType(GenesisModel):
    ttype = models.CharField(max_length=16,choices=TTYPE,blank=True,null=True,verbose_name='类别')
    itemtypecode = models.CharField(max_length=16,null=True,blank=True,verbose_name='项目类别编号')
    itemtypename = models.CharField(max_length=128,null=True,blank=True,verbose_name='项目类别名称')
    parentitemtype = models.CharField(max_length=16,null=True,blank=True,verbose_name='父类')

    class Meta:
        verbose_name='项目类别'
        verbose_name_plural=verbose_name
        managed=True
        db_table ='itemtype'

class Item(GenesisModel,ItemModel,ArchivementBaseModel):
    itemcode = models.CharField(max_length=16,blank=True,null=True)
    itemname = models.CharField(max_length=64,blank=True,null=True)

    class Meta:
        verbose_name='项目'
        verbose_name_plural='项目'
        # managed=True
        db_table ='item'

class Objectvalue2(GenesisModel):
    objectname1 = models.CharField(max_length=40)
    objectname2 = models.CharField(max_length=40)
    langtype = models.CharField(max_length=1)
    objectvalue = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        verbose_name_plural='系统参数表'
        verbose_name='系统参数表'
        managed = True
        db_table = 'objectvalue2'
        unique_together = (('objectname1', 'objectname2', 'langtype'),)



HDSYSUSER_IDTYPE=(
    ('10','员工登陆号'),
    ('80','员工岗位')
)
class Hdsysuser(GenesisModel):
    sys_idtype = models.CharField(max_length=32,choices=HDSYSUSER_IDTYPE,default='10',blank=True,null=True,verbose_name='类型')
    sys_userid = models.CharField(db_column='SYS_USERID', max_length=16,null=False,blank=True,verbose_name='用户名')  # Field name made lowercase.
    sys_passwd = models.CharField(db_column='SYS_PASSWD', max_length=32,verbose_name='密码')  # Field name made lowercase.
    sys_userstatus = models.SmallIntegerField(db_column='SYS_USERSTATUS',verbose_name='当前状态')  #
    sys_fullname = models.CharField(db_column='SYS_FULLNAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sys_lock = models.CharField(db_column='SYS_LOCK', max_length=1, blank=True, null=True)  # Field name made lowercase.
    sys_retry = models.SmallIntegerField(db_column='SYS_RETRY', blank=True, null=True)  # Field name made lowercase.
    sys_adm = models.CharField(db_column='SYS_ADM', max_length=1, blank=True, null=True,verbose_name='是否管理员')  # Field name made lowercase.
    storelist = MultiSelectField(max_length=128,choices=STOREINFO,blank=True,null=True,verbose_name='可用门店')
    costpriceflag = models.CharField(max_length=8,choices=FLAG,default='N', blank=True,null=True,verbose_name='是否有查看成本价权限')

    class Meta:
        managed = True
        db_table = 'hdsysuser'

    def __str__(self):
        return self.sys_userid

class Useright(GenesisModel):
    sys_userid = models.CharField(db_column='SYS_USERID', max_length=32,blank=True,null=True,verbose_name='编号')  # Field name made lowercase.
    sys_module = models.CharField(db_column='SYS_MODULE', max_length=50,verbose_name='功能模块')  # Field name made lowercase.
    sys_readrights = models.CharField(db_column='SYS_READRIGHTS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    sys_writerights = models.CharField(db_column='SYS_WRITERIGHTS', max_length=1, blank=True, null=True)  # Field name made lowercase.
    sys_modulegrp = models.CharField(db_column='SYS_MODULEGRP', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'useright'
        unique_together = (('company','storecode','sys_userid', 'sys_module'),)

    def __str__(self):
        return self.sys_userid +':'+self.sys_module

class Enactmen(GenesisModel):
    corpname = models.CharField(db_column='CORPNAME', max_length=100, blank=True, null=True,verbose_name='公司')  # Field name made lowercase.
    storecode = models.CharField(db_column='STORECODE', max_length=10,verbose_name='店铺编号')  # Field name made lowercase.
    storename = models.CharField(db_column='STORENAME', max_length=100, blank=True, null=True,verbose_name='店铺名称')  # Field name made lowercase.
    firstday = models.CharField(db_column='FIRSTDAY', max_length=8, blank=True, null=True,verbose_name='开业日期')  # Field name made lowercase.
    multidiscable = models.CharField(db_column='MULTIDISCABLE', max_length=1, blank=True, null=True,verbose_name='直接打印提示')  # Field name made lowercase.
    saledept = models.CharField(db_column='SALEDEPT', max_length=40, blank=True, null=True,verbose_name='销售品仓库')  # Field name made lowercase.
    invoicetitle = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票抬头')
    invoicefoot = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票页脚')
    usewhcode = models.CharField(max_length=32, blank=True, null=True,verbose_name='使用品仓库')

    class Meta:
        managed = True
        db_table = 'enactmen'
        verbose_name='门店信息'
        verbose_name_plural='门店信息'

PCODELIST= Paymode.objects.filter(company=common.constants.COMPANYID,flag='Y').values_list('pcode','pname')
class Cardsupertype(GenesisModel):
    code = models.CharField( max_length=16,blank=True,null=True,verbose_name='编号')
    name = models.CharField(max_length=500, blank=True, null=True,verbose_name='名称')
    parentid = models.CharField(max_length=16, blank=True, null=True)
    note = models.CharField(max_length=200, blank=True, null=True)
    res = models.CharField(max_length=200, blank=True, null=True)
    pcode = models.CharField(max_length=16,choices=PCODELIST,blank=True,null=True,verbose_name='默认付款方式')
    normal_pcode = models.CharField(max_length=16,choices=PCODELIST,blank=True,null=True,verbose_name='正常对应付款方式')
    present_pcode = models.CharField(max_length=16,choices=PCODELIST,blank=True,null=True,verbose_name='赠送对应付款方式')

    class Meta:
        verbose_name = '卡大类'
        verbose_name_plural = verbose_name
        managed = True
        db_table = 'cardsupertype'

    def __init__(self,*args,**kwargs):
        super(Cardsupertype, self).__init__(*args, **kwargs)
        self._meta.get_field('pcode').choices =  Paymode.objects.filter(company=self.company,flag='Y').values_list('pcode','pname')

class CardtypeManager(models.Manager):
    def cardcount(self,cardtype):
        return Cardinfo.objects.filter(cardtype=self.cardtype).count()

CARDSUPTYPE = Cardsupertype.objects.filter(company=common.constants.COMPANYID,flag='Y').values_list('code','name')
class Cardtype(GenesisModel,ItemModel,ArchivementBaseModel):
    COMPTYPE = (
        ('amount','计费'),
        ('times', '计次'),
    )
    FLAG =(
        ('Y','可以销售'),
        ('N','不可销售'),
    )
    VALDATETYPE=(
        ('10','第一次使用日期'),
        ('20','销售日期'),
        ('90','手动输入')
    )
    cardtype = models.CharField(max_length=16,null=False,blank=True,verbose_name='编号')
    cardname = models.CharField(max_length=100, blank=True, null=True,verbose_name='名称')
    cardnote = models.CharField(max_length=100, blank=True, null=True,verbose_name='备注')
    # oriprice = models.DecimalField(max_digits=12, default=0,decimal_places=4, blank=True, null=True,verbose_name='标准售价')
    # oripricecurrency = models.CharField(max_length=8, blank=True, null=True,verbose_name='币别')
    leftmoney = models.DecimalField(max_digits=16, default=0.00,decimal_places=2, blank=True, null=True,verbose_name='可用金额')
    custperc = models.DecimalField(max_digits=10, default=1.00,decimal_places=4, blank=True, null=True,verbose_name='会员消费额折算率')
    # srvrptypecode = models.CharField(max_length=8, blank=True, null=True,verbose_name='所属报表大类')
    comptype = models.CharField(max_length=8, blank=True,default='amount', choices=COMPTYPE,null=True,verbose_name='消费模式')
    prncomptype = models.CharField(max_length=8, blank=True, null=True,verbose_name='打印小票时显示的消费方式')
    suptype = models.CharField(max_length=8, choices=CARDSUPTYPE,blank=True, null=True,verbose_name='卡大类')
    # saleperc = models.DecimalField(max_digits=6, default=0,decimal_places=5, blank=True, null=True,verbose_name='顾问销售提成率')
    # salesrvprec = models.DecimalField(max_digits=6, default=0,decimal_places=5, blank=True, null=True, verbose_name='销售提成率')
    # checkdate = models.CharField(max_length=8, blank=True, null=True)
    # pmperc =  models.DecimalField(max_digits=8, default=0,decimal_places=4, blank=True, null=True,verbose_name='顾问销售提成率')
    # secperc =  models.DecimalField(max_digits=8, default=0,decimal_places=4, blank=True, null=True,verbose_name='美容师1销售提成率')
    # thrperc = models.DecimalField(max_digits=10, default=0.00,decimal_places=2, blank=True, null=True,verbose_name='美容师2销售提成率')
    # pmguideperc = models.DecimalField(max_digits=8, default=0,decimal_places=4, blank=True, null=True,verbose_name='顾问营业额拆分率')
    # secguideperc = models.DecimalField(max_digits=8, default=0,decimal_places=4, blank=True, null=True,verbose_name='美容师2营业额拆分率')
    # thrguideperc = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True,verbose_name='美容师2营业额拆分率')
    # pmpoint = models.DecimalField(max_digits=6, default=0.00,decimal_places=2, blank=True, null=True,verbose_name='顾问销售提出金额')
    # secpoint = models.DecimalField(max_digits=6, default=0.00,decimal_places=2, blank=True, null=True,verbose_name='美容师1销售提成金额')
    # thrpoint = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,verbose_name='美容师2销售提成金额')
    # basenum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # salethrperc = models.DecimalField(max_digits=6, decimal_places=5, blank=True, null=True)
    # salesflag = models.CharField(max_length=8, default='Y',choices=SALESFLAG,blank=True, null=True,verbose_name='可否销售')
    valdatetype = models.CharField(max_length=16,default='10',choices=VALDATETYPE, blank=True,null=True,verbose_name='有效期天数计算方法')
    validays = models.DecimalField(max_digits=10, default=9999,decimal_places=2, blank=True, null=True,verbose_name='有效期天数')
    # isic = models.CharField(db_column='ISIC', max_length=1, blank=True, null=True)  # Field name made lowercase.
    # rptcode1 = models.CharField(max_length=16, blank=True, null=True,verbose_name='分类1')
    # rptcode2 = models.CharField(max_length=16, blank=True, null=True,verbose_name='分类2')
    # rptcode3 = models.CharField(max_length=16, blank=True, null=True,verbose_name='分类3')
    # photofile = models.CharField(max_length=64, blank=True, null=True)
    minfillmoney = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True,verbose_name='最低充值金额')
    maxratio = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    # rptcode4 = models.CharField(max_length=16, blank=True, null=True)
    # rptcode5 = models.CharField(max_length=16, blank=True, null=True)
    # rptcode6 = models.CharField(max_length=16, blank=True, null=True)
    # brand = models.ForeignKey('Brand',db_column='brand',choices=BRAND, max_length=16, blank=True, null=True,on_delete=models.SET_NULL,verbose_name='品牌')
    # cardprice2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # cardprice3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # cardprice4 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # ttype = models.CharField(max_length=8,blank=True,null=True,verbose_name='计次卡对应的项目类型')
    ruler = models.ForeignKey('baseinfo.Ruler',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='规则')
    sguuid = models.UUIDField(blank=True,null=True,verbose_name='服务商品UUID')
    # brand = models.CharField(max_length=16,db_column='brand',choices=BRAND,blank=True, null=True,verbose_name='品牌')
    objects = CardtypeManager()

    class Meta:
        managed = True
        db_table = 'cardtype'
        verbose_name ='会员卡卡类'
        verbose_name_plural = '会员卡卡类'
        ordering = ['cardtype']
        unique_together = ("company", "cardtype")

    def __str__(self):
        return self.cardname

    @property
    def defaultpaycode(self):
        try:
            cardsuptype = Cardsupertype.objects.get(company=self.company,code=self.suptype)
            return  cardsuptype.pcode
        except:
            return  'B'

class Cardvsdi(GenesisModel):
    FLAG = (
        ('Y', '可以销售'),
        ('N', '不可销售'),
    )

    TTYPE = (
        ('S','服务'),
        ('G','商品'),
        ('C','卡')
    )
    PRICETYPE = (
        ('DISCOUNT','按照折扣'),
        ('PRICE', '按照价格'),
    )

    # vsid = models.AutoField(db_column='VSID', max_length=32)  # Field name made lowercase.
    cardtypeuuid = models.ForeignKey('Cardtype',db_column='cardtypeuuid', null=True, on_delete=models.SET_NULL,max_length=16)  # Field name made lowercase.
    cardtype = models.CharField(db_column='cardtype',max_length=16,null=True,blank=True,verbose_name='编号')
    topcode = models.CharField(db_column='TOPCODE', max_length=32,null=True,blank=True,verbose_name='服务大类')  # Field name made lowercase.
    # topcode = models.ForeignKey('Srvtopty',db_column='topcode',default=None,blank=True,null=True,on_delete=models.SET_NULL,verbose_name='服务大类')
    cardvsdisc = models.DecimalField(db_column='CARDVSDISC',default=1, max_digits=6, decimal_places=5, blank=True, null=True,verbose_name='折扣')  # Field name made lowercase.
    cddsec = models.CharField(db_column='CDDSEC', max_length=100, default='',blank=True, null=True)  # Field name made lowercase.
#    ccode = models.CharField(db_column='CCODE', max_length=40, blank=True, null=True)  # Field name made lowercase.
    ttype = models.CharField(max_length=8,default='S',choices=TTYPE,verbose_name='项目类别')
    flag = models.CharField(max_length=1, default='Y',choices=FLAG,blank=True, null=True,verbose_name='可否消费')
    guideperc = models.DecimalField(max_digits=10, default=1,decimal_places=4, blank=True, null=True,verbose_name='员工业绩折算率')
    cardvsprice = models.DecimalField(max_digits=16, default=0,decimal_places=4, blank=True, null=True,verbose_name='单次价格')
    pricetype = models.CharField(max_length=16, default='DISCOUNT', choices=PRICETYPE,blank=True,null=True,verbose_name='计费方法')

    class Meta:
        managed = True
        db_table = 'cardvsdi'
        verbose_name='计费卡类折扣'
        verbose_name_plural='计费卡类折扣'

    def __str__(self):
        return ''

class CardtypeVsDiscountClass(GenesisModel):
    cardtypeuuid = models.ForeignKey(Cardtype,db_column='cardtypeuuid',blank=True,null=True,verbose_name='卡类')
    cardtype = models.CharField(max_length=32,blank=True,null=True,verbose_name='卡类编号')
    ttype = models.CharField(max_length=8,default='S',choices=TTYPE,verbose_name='项目类别')
    discountclass = models.CharField(max_length=16,default='',blank=True,null=True,verbose_name='折扣分类')
    discounttype = models.CharField(max_length=8,blank=True,null=True,verbose_name='折扣方式')
    price = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='折扣价')
    disc = models.DecimalField(max_digits=8,decimal_places=5,default=1,blank=True,null=True,verbose_name='折扣率')
    valiflag = models.CharField(max_length=8,blank=True,null=True,verbose_name='可否消费')
    emplguideperc = models.DecimalField(max_digits=10, default=1,decimal_places=4, blank=True, null=True,verbose_name='员工业绩折算率')

    # class Meta:
    #     managed = True
    #     db_table = 'cardtypevsdiscountclass'
    #     verbose_name='计费卡类折扣'
    #     verbose_name_plural=verbose_name
    #
    # def __str__(self):
    #     return ''

class Ruler(models.Model):
    rulername = models.CharField(max_length=32,db_column='rulername',blank=True,null=True,verbose_name='规则名称' )
    ruler = models.CharField(max_length=512,db_column='ruler',blank=True,null=True,verbose_name='规则')
    flag = models.CharField(max_length=8,choices=FLAG,default='Y',blank=True,null=True,verbose_name='是否有效')

    class Meta:
        managed = True
        db_table = 'ruler'
        verbose_name='规则'
        verbose_name_plural='规则'

    def __str__(self):
        return self.rulername

class Vip(GenesisModel):
    vcode = models.CharField(max_length=24, blank=True,null=True,verbose_name='会员号')
    vname = models.CharField(max_length=32, blank=True, null=True,verbose_name='姓名')
    othercha = models.CharField(max_length=100, blank=True, null=True)
    telph = models.CharField(max_length=64, blank=True, null=True,verbose_name='电话')
    addr = models.CharField(max_length=200, blank=True, null=True,verbose_name='收货地址')
    zip = models.CharField(max_length=8, blank=True, null=True)
    birth = models.CharField(max_length=8, blank=True, null=True,verbose_name='生日')
    IDNO = models.CharField(max_length=16, blank=True, null=True,verbose_name='身份证号码')
    vdesc = models.CharField(max_length=1000, blank=True, null=True)
#    vipflag = models.CharField(max_length=1, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    mtcode = models.CharField(max_length=20, blank=True, null=True,verbose_name='手机')
    qq = models.CharField(max_length=16, blank=True, null=True,verbose_name='QQ')
    wechat = models.CharField(max_length=16, blank=True, null=True,verbose_name='微信号')
    weibo = models.CharField(max_length=32, blank=True, null=True,verbose_name='微博')
    documentpath = models.CharField(max_length=128, blank=True, null=True)
    license = models.CharField(max_length=8, blank=True, null=True,verbose_name='车牌')
    indate = models.DateField(max_length=8, blank=True, null=True,verbose_name='入会日期')
    photofile = models.ImageField(upload_to="images", blank=True, null=True,verbose_name='照片')
    status = models.CharField(max_length=8, choices=common.constants.VIPSTATUS,blank=True, null=True,verbose_name='当前状态')
    sex = models.CharField(max_length=1, blank=True, null=True,verbose_name='性别')
    vipcode = models.CharField(max_length=32, blank=True, null=True)
    vippinno = models.CharField(max_length=32, blank=True, null=True,verbose_name='密码')
    viptype = models.CharField(max_length=8, choices=VIPTYPE,blank=True, null=True,verbose_name='散客/会员')
    ecode = models.CharField(max_length=40, blank=True, null=True,verbose_name='负责顾问')
    ecode2 = models.CharField(max_length=16, blank=True, null=True,verbose_name='指定美疗师')
    valiflag = models.CharField(max_length=8,default='Y', blank=True, null=True)
    firstname = models.CharField(max_length=32, blank=True, null=True)
    lastname = models.CharField(max_length=32, blank=True, null=True)
    nametype = models.CharField(max_length=8, blank=True, null=True)
    areacode = models.CharField(max_length=16, blank=True, null=True,verbose_name='地区')
    companyid = models.CharField(max_length=16, blank=True, null=True,verbose_name='所属公司')
    viplevel = models.CharField(max_length=8,default='',blank=True,null=True,verbose_name='当前级别')
    source = models.CharField(max_length=32,blank=True,null=True,verbose_name='来店渠道')
    pinyin = models.CharField(max_length=32,blank=True,null=True,verbose_name='拼音')
    occupation = models.CharField(max_length=16,blank=True,null=True,verbose_name='职业')
    tags = MultiSelectField(choices=VIPTAGS,max_length=64,blank=True,null=True,verbose_name='标签')
    referreruuid = models.UUIDField(blank=True,null=True,verbose_name='推荐人UUID')
    referrervcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='推荐人姓名')
    openid = models.CharField(max_length=32,blank=True,null=True,verbose_name='微信openid')
    unionid = models.CharField(max_length=32,blank=True,null=True,verbose_name='微信unionid')

    class Meta:
        verbose_name='会员'
        verbose_name_plural='会员'
        managed = True
        db_table = 'vip'

    def __str__(self):
        if self.vcode == None:
            self.vcode = ''
            # return self.viptype + '：' + self.vname + '-' + self.vcode

        if self.vname == None:
            self.vname = '未留'
            return self.viptype + '：' + self.vname + '-' + self.vcode

        if self.viptype=='10':
            self.viptype='会员'
            return self.viptype + '：' + self.vname +'-'+ self.vcode
        if self.viptype=='20':
            self.viptype='散客'
            return self.viptype + '：' + self.vname +'-'+ self.vcode

        if self.viptype ==None:
            self.viptype ='未知'
            return self.viptype + '：' + self.vname + '-' + self.vcode

        if self.uuid == None:
            self.uuid =uuid.uuid4()
            return str(self.uuid)

        return self.viptype + '：' + self.vname +'-'+ self.vcode

    def get_cardsuptype(self):
        cardtypes = adviser.models.Cardinfo.objects.filter(company=common.constants.COMPANYID,vipuuid=self.uuid).values('cardtype')
        return 0

    def set_pinyin(self):
        self.pinyin = main(self.vname)
        print(self.pinyin)
        self.save()
        return 0
#    def preview(self):
#        return '<img src="%s" height="256",width="256" />' %(self.photofile.url)

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    def save(self,*args, **kwargs):
        print(self.vname,main(self.vname),self.mtcode)

        self.pinyin = main(self.vname)
        if self.vcode == None :
            self.vcode=''
            self.save()

        if (self.viptype=='10' and len(self.vcode)==0 ):
            vip = Vip.objects.filter(company=self.company, vcode__startswith=self.storecode,viptype='10').order_by('-vcode').first()
            print(vip)
            if len(vip.vcode) > 0:
                print(vip.vcode, 'len(storecode)=', len(self.storecode), 'len(vip.vcode) - len(storecode)=',
                      len(vip.vcode) - len(self.storecode))
                nextcode = vip.vcode[len(vip.storecode):len(vip.vcode)]
            else:
                nextcode = '00000000'
            print(nextcode)
            self.vvcode = self.storecode + ('00000000' + str(int(nextcode) + 1))[-common.constants.DEFAULT_VCODE_LENGTH:]
            print(self.vcode)

        super(Vip, self).save(*args, **kwargs)
        return 0

    def nextccode(self):
        prefix = self.storecode
        codelength = DEFAULT_CCODE_LENGTH
        vcode=self.vcode
        cardinfo = Cardinfo.objects.filter(company=self.company, storecode=self.storecode, vcode=self.vcode).order_by('-ccode')[:1]

        print('cardinfo',cardinfo)
        # if len(cardinfo) == 0:
        if cardinfo==None or len(cardinfo)==0:
            lastcode = '00000001'[-codelength]
        else:
            lastccode = cardinfo[0].ccode
            lastcode = lastccode[len(vcode)+1:len(lastccode)]
        print('lastcode:',lastcode)
        nextccode = vcode + '-' + ('000000' + str(int(lastcode) + 1))[-codelength:]
        print('nextccode:',nextccode)
        return nextccode

    def pmname(self):
        return Empl.objects.filter(company=self.company,ecode=self.ecode)[0].ename

    def secname(self):
        return Empl.objects.filter(company=self.company, ecode2=self.ecode)[0].ename

    @property
    def ecode_list(self):
        if self.ecode is None:
            self.ecode=''

        if self.ecode2 is None:
            self.ecode2=''

        return (self.ecode +' ' +self.ecode2).split()

    @property
    def birth_month(self):
        if len(self.birth)== 8:
            return self.birth[4:6]
        else:
            return '00'

    @property
    def birth_day(self):
        if len(self.birth)== 8:
            return self.birth[6:8]
        else:
            return '00'

    @property
    def indate_month(self):
        if self.indate is None:
            return '200000'
        else:
            return ('0'+str(self.indate.month))[:2]

    @property
    def indate_day(self):
        if self.indate is None:
            return '00'
        else:
            return ('0'+str(self.indate.day))[:2]

class VipAddress(GenesisModel):
    vipuuid=models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,verbose_name='会员')
    vcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='会员号')
    receiver = models.CharField(max_length=16,blank=True,null=True,verbose_name='收件人')
    mtcode =  models.CharField(max_length=16,blank=True,null=True,verbose_name='手机')
    province = models.CharField(max_length=32,blank=True,null=True,verbose_name='省份')
    city = models.CharField(max_length=32,blank=True,null=True,verbose_name='城市')
    address = models.CharField(max_length=128,blank=True,null=True,verbose_name='地址')
    showsequence = models.CharField(max_length=8,blank=True,null=True,verbose_name='显示顺序')
    defaultflag = models.CharField(max_length=8,default='N',blank=True,null=True,verbose_name='默认值标志')

    class Meta:
        verbose_name='会员地址'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'vipaddress'

    def __str__(self):
        return self.vipuuid.vname

class Vip20(Vip):
    class Meta:
        verbose_name = "散客信息"
        verbose_name_plural = verbose_name
        proxy = True

VIPSPECDATETYPELIST= Appoption.objects.filter(company=common.constants.COMPANYID,flag='Y',seg='vipspecdatetype').values_list('itemname','itemvalues')
class VipSpecialDate(GenesisModel):
    vipuuid=models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,verbose_name='会员')
    vcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='会员号')
    specdatetype = models.CharField(max_length=16,choices=VIPSPECDATETYPELIST,default='',blank=True,null=True,verbose_name='日期类型')
    lunarcalendarflag = models.CharField(max_length=16,default='N',blank=True,null=True,verbose_name='是否阴历')
    specdate = models.CharField(max_length=16,blank=True,null=True,verbose_name='特殊日期')
    remark = models.CharField(max_length=256,blank=True,null=True,verbose_name='备注')

    class Meta:
        verbose_name='客人特别日'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'vipspecicaldate'

    def __init__(self):
        super(VipSpecialDate, self).__init__(*args, **kwargs)
        self._meta.get_field('specdatetype').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='vipspecdatetype').values_list( 'itemname', 'itemvalues')

    def __str__(self):
        return self.specdatetype

class Position(GenesisModel):
    positioncode = models.CharField(max_length=8,blank=True,null=True,verbose_name='代号')
    positiondesc = models.CharField(max_length=40, blank=True, null=True,verbose_name='职位')
    valideflag = models.CharField(max_length=1, blank=True, null=True)
    sysflag = models.CharField(max_length=8, blank=True, null=True)
    bookingflag = models.CharField(max_length=1, blank=True, null=True,verbose_name='是否可以预约')

    class Meta:
        verbose_name='职位'
        verbose_name_plural='职位'
        managed = True
        db_table = 'position'

    def __str__(self):
        return self.positiondesc


class Team(GenesisModel):
    teamid = models.CharField(max_length=16,blank=True,null=True,verbose_name='业务组别')
    teamname = models.CharField(max_length=64, blank=True, null=True,verbose_name='名称')
    teamdesc = models.CharField(max_length=256, blank=True, null=True)
    flag = models.CharField(max_length=8, blank=True, null=True)
    parent = models.ForeignKey('self',default='0',blank=True,null=True,on_delete=models.SET_NULL )

    class Meta:
        verbose_name='业务组别'
        verbose_name_plural='业务组别'
        managed = True
        db_table = 'team'


EMPLSTATUS=(
        {'Y','在职'},
        ('N','离职')
)
POSITION = Position.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('positioncode', 'positiondesc')
STORECODE = Storeinfo.objects.filter(company=common.constants.COMPANYID).values_list('storecode', 'storename')
TEAMLIST = Team.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('teamid', 'teamname')

class Empl(BaseModel):
    ecode = models.CharField(db_column='ECODE', max_length=16,blank=True,null=True,verbose_name='员工工号')  # Field name made lowercase.
    ename = models.CharField(db_column='ENAME', max_length=32, blank=True, null=True,verbose_name='姓名')  # Field name made lowercase.
    cname = models.CharField(max_length=32, blank=True, null=True,verbose_name='中文名')
    indate = models.CharField(db_column='INDATE', max_length=8, blank=True, null=True,verbose_name='入职日期')  # Field name made lowercase.
    position = models.CharField(db_column='POSITION', choices=POSITION,max_length=20, blank=True, null=True,verbose_name='职位')  # Field name made lowercase.
    outdate = models.CharField(db_column='OUTDATE', max_length=8, blank=True, null=True,verbose_name='')  # Field name made lowercase.
    telcode = models.CharField(db_column='TELCODE', max_length=15, blank=True, null=True,verbose_name='身份证')  # Field name made lowercase.
    cmtcode = models.CharField(db_column='CMTCODE', max_length=15, blank=True, null=True,verbose_name='手机号')  # Field name made lo号码wercase.
    cardno = models.CharField(db_column='CARDNO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    empnote = models.CharField(db_column='EMPNOTE', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    # positioncode = models.ForeignKey(Position,db_column='positioncode',related_name='empls', blank=True, null=True,on_delete=models.SET_NULL,verbose_name='职位')
    status = models.CharField(max_length=8,choices=SALESFLAG, blank=True, null=True,verbose_name='是否在职')
 #   empldesc1 = models.CharField(max_length=256, blank=True, null=True)
 #   empldesc2 = models.CharField(max_length=256, blank=True, null=True)
 #   empldesc3 = models.CharField(max_length=256, blank=True, null=True)
 #    teamid = models.ForeignKey(Team,db_column='teamid',max_length=16, blank=True, null=True,on_delete=models.SET_NULL,verbose_name='业务组别')
    team = models.CharField(max_length=16,choices=TEAMLIST,blank=True,null=True,verbose_name='业务组别')
    emplpwd = models.CharField(max_length=32, blank=True, null=True,verbose_name='员工密码')
    # photofile = models.CharField(max_length=256, blank=True, null=True,verbose_name='照片')
    storecode = models.CharField(max_length=16,choices=STORECODE,blank=True,null=True,verbose_name='所属门店')
    # storecode = models.ForeignKey('baseinfo.Storeinfo',db_column='storecode', blank=True, null=True,on_delete=models.SET_NULL,verbose_name='所在店铺')
    openid = models.CharField(max_length=32,blank=True,null=True,verbose_name='微信openid')
    unionid = models.CharField(max_length=32,blank=True,null=True,verbose_name='微信unionid')
    storelist = MultiSelectField(choices=STOREINFO,blank=True,null=True,verbose_name='可用门店')

    class Meta:
        verbose_name='员工'
        verbose_name_plural='员工'
        managed = True
        db_table = 'empl'

    def __init__(self, *args, **kwargs):
        super(Empl, self).__init__(*args, **kwargs)
        self._meta.get_field('storelist').choices = Storeinfo.objects.filter(company=self.company, flag='Y').values_list('storecode','storename')
        self._meta.get_field('storecode').choices = Storeinfo.objects.filter(company=self.company, flag='Y').values_list('storecode','storename')
        self._meta.get_field('position').choices =Position.objects.filter(company=self.company, flag='Y').values_list('positioncode', 'positiondesc')
        self._meta.get_field('team').choices =Team.objects.filter(company=self.company, flag='Y').values_list('teamid', 'teamname')
        # self._meta.get_field('goodsct').choices =Goodsct.objects.filter(company=self.company,flag='Y').values_list('goodsct','goodsctname')

    def __str__(self):
        if self.ename == None:
            self.ename=''
        return self.ename

    def get_empl_byecode(ecode):
        return Empl.objects.get(company=common.constants.COMPANYID,ecode=ecode)

class Goodsct(GenesisModel):
    goodsct = models.CharField(max_length=16,blank=True,null=True,verbose_name='分类编号')
    goodsctname = models.CharField(max_length=40,verbose_name='分类名称')
    parent = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name='商品折扣分类'
        verbose_name_plural='商品折扣分类'
        managed = True
        db_table = 'goodsct'

    def __str__(self):
        return self.goodsctname

class Goods(GenesisModel,ItemModel,ArchivementBaseModel):
    # UNITS=(
    #     ('10','ml'),
    #     ('20','g'),
    #     ('30','瓶'),
    #     ('40','支'),
    #     ('50','套'),
    #     ('51','个'),
    #     ('52','台'),
    #     ('53','盒'),
    #     ('54','袋'),
    #     ('55','张'),
    #     ('60','斤'),
    #     ('61','包'),
    #     ('62','件'),
    #     ('63','双'),
    #     ('64','对'),
    #     ('65','本'),
    #     ('66','副'),
    #     ('67','片'),
    #     ('68','条'),
    #     ('69','桶'),
    #     ('70','份')
    # )
    FLAG =(
        ('Y','有效'),
        ('N','无效'),
    )
    SALESCHANNELS =(
        ('10','线下门店销售'),
        ('20','线上销售'),
    )
    GOODSCTS = Goodsct.objects.filter(company=common.constants.COMPANYID,flag='Y').values_list('goodsct','goodsctname')
    gcode = models.CharField(db_column='GCODE', max_length=40,blank=True,verbose_name='商品编码')  # Field name made lowercase.
    gname = models.CharField(db_column='GNAME', max_length=100, blank=True, null=True,verbose_name='商品名称')  # Field name made lowercase.
    spec = models.CharField(db_column='SPEC', max_length=40, blank=True, null=True,verbose_name='规格')  # Field name made lowercase.'
    buyprc = models.DecimalField(db_column='BUYPRC', default=0,max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='进价')
    # saleprc = models.DecimalField(db_column='SALEPRC', default=0,max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='售价')  # Field name made lowercase.
    isreturn = models.CharField(db_column='ISRETURN', max_length=1, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=1,blank=True, null=True,verbose_name='数量')
    unit = models.CharField(db_column='UNIT', choices=UNITS, default='10',max_length=10, blank=True, null=True,verbose_name='单位')  # Field name made lowercase.
    intax = models.DecimalField(db_column='INTAX', max_digits=5, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    barcode = models.CharField(db_column='BARCODE', max_length=16, blank=True, null=True,verbose_name='条码')  # Field name made lowercase.
    saledept = models.CharField(max_length=20, blank=True, null=True,verbose_name='可销售仓库')
    charactertic = models.CharField(max_length=500, blank=True, null=True)
    minivalues = models.DecimalField(max_digits=10, default=1,decimal_places=0, blank=True, null=True,verbose_name='最低库存数')
    maxvalues = models.DecimalField(db_column='maxvalueS', default=10,max_digits=10, decimal_places=0, blank=True, null=True,verbose_name='最高库存数')  # Field name made lowercase.
    goodstype = models.CharField(max_length=40, blank=True, null=True,verbose_name='')
    intervalday = models.DecimalField(max_digits=10, decimal_places=2, default=30,blank=True, null=True,verbose_name='估计使用天数')
    packagetype = models.CharField(max_length=10, blank=True, null=True)
    costprc = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True,verbose_name='当前成本')
    areacode = models.CharField(max_length=16, blank=True, null=True)
    companyid = models.CharField(max_length=16, blank=True, null=True)
    location = models.CharField(max_length=16, blank=True, null=True,verbose_name='库房位置')
    salestargets = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchases = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    photofile = models.CharField(max_length=64, blank=True, null=True)
    desc1 = models.CharField(max_length=64, blank=True, null=True,verbose_name='商品描述1')
    desc2 = models.CharField(max_length=64, blank=True, null=True,verbose_name='商品描述2')
    desc3 = models.CharField(max_length=64, blank=True, null=True,verbose_name='商品描述3')
    purchaseflag = models.CharField(max_length=8, choices=FLAG,blank=True, null=True,verbose_name='是否可以采购')
    supplierid = models.CharField(max_length=16,db_column='supplierid',null=True,blank=True,verbose_name='供应商')
    goodsct = models.CharField(max_length=16,db_column='goodsct',choices=GOODSCTS,null=True,blank=True,verbose_name='商品折扣分类')
    saleschannels = MultiSelectField(max_length=128,choices=SALESCHANNELS,blank=True,null=True,verbose_name='销售渠道')
    small_image =  models.ImageField(upload_to='static/images',blank=True,null=True,verbose_name='示例图片-小')
    large_image =  models.ImageField(upload_to='static/images',blank=True,null=True,verbose_name='示例图片-大')


    class Meta:
        verbose_name='商品信息'
        verbose_name_plural='商品信息'
        managed = True
        db_table = 'goods'
        unique_together = ("company", "gcode")

    def __str__(self):
        if self.gname ==None:
            self.gname=''

        return self.gname

    def __init__(self, *args, **kwargs):
        super(Goods, self).__init__(*args, **kwargs)
        self._meta.get_field('goodsct').choices = Goodsct.objects.filter(company=self.company,flag='Y').values_list('goodsct','goodsctname')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        cardtype = Cardtype.objects.get_or_create(company=self.company,cardtype=self.gcode)[0]
        cardtype.cardname=self.gname
        cardtype.price =self.price
        cardtype.suptype='22'
        cardtype.comptype='times'
        cardtype.ttype='G'
        cardtype.sguuid=self.uuid
        cardtype.brand = self.brand
        cardtype.discountclass = self.discountclass
        cardtype.displayclass1 = self.displayclass1
        cardtype.displayclass2 = self.displayclass2
        cardtype.marketclass1 = self.marketclass1
        cardtype.marketclass2 = self.marketclass2
        cardtype.marketclass3 = self.marketclass3
        cardtype.marketclass4 = self.marketclass4
        cardtype.financeclass1 = self.financeclass1
        cardtype.financeclass2 = self.financeclass2
        cardtype.storelist =self.storelist
        cardtype.save()

        goodsprice = Goodsprice.objects.get_or_create(company=self.company,goodsuuid=self,qty=1)[0]
        goodsprice.gcode=self.gcode
        goodsprice.price=self.price
        goodsprice.amount=self.price
        goodsprice.save()

class Goodsprice(GenesisModel):
    goodsuuid = models.ForeignKey('Goods',db_column='goodsuuid',null=True,on_delete=models.SET_NULL,verbose_name='商品')
    gcode = models.CharField(db_column='gcode', max_length=40,blank=True,verbose_name='商品编码')  # Field name made lowercase.
    qty = models.IntegerField(default=1,null=True,blank=True,verbose_name='数量')
    price = models.DecimalField(decimal_places=2,default=0,max_digits=10,null=True,verbose_name='单次价格')
    amount = models.DecimalField(decimal_places=2, default=0,max_digits=10,null=True,verbose_name='总价')
    commission = models.DecimalField(decimal_places=4,default=0, max_digits=5,null=True, verbose_name='销售提成率')
    achievement = models.DecimalField(decimal_places=4,default=1.00, max_digits=5,null=True, verbose_name='销售业绩率')
    fromdate = models.DateField(null=True,blank=True,verbose_name='价格生效起始日期')
    todate = models.DateField(null=True,blank=True,verbose_name='价格生效结束日期')
    saleflag = models.CharField(max_length=8, blank=True, default='Y', null=True, choices=SALESFLAG,verbose_name='可否销售')
    stype = models.CharField(max_length=8,blank=True,null=True,default='N',choices=STYPE,verbose_name='是否赠送')


    class Meta:
        verbose_name = '产品疗程价格'
        verbose_name_plural = '产品疗程价格'
        managed = True
        db_table = 'goodsprice'

class Srvrptype(GenesisModel):
    srvrptypecode = models.CharField( max_length=8, blank=True,null=True,verbose_name='编号')
    srvrptypename = models.CharField(max_length=255, blank=True, null=True,verbose_name='名称')
    srvrptypedesc = models.CharField(max_length=255, blank=True, null=True,verbose_name='描述')

    class Meta:
        verbose_name='报表分类'
        verbose_name_plural='报表分类'
        managed = True
        db_table = 'srvrptype'

    def __unicode__(self):
        return self.srvrptypename

    def __str__(self):
        return self.srvrptypename

class Srvtopty(GenesisModel):
    topcode = models.CharField(db_column='TOPCODE', max_length=16, blank=True,null=True,verbose_name='编号')  # Field name made lowercase.
    ttname = models.CharField(db_column='TTNAME', max_length=100, blank=True, null=True,verbose_name='名称')  # Field name made lowercase.
    ttdesc = models.CharField(db_column='TTDESC', max_length=200, blank=True, null=True)  # Field name made lowercase.
    parentcode = models.CharField(db_column='parentcode',max_length=16,blank=True,null=True,verbose_name='父级')

    class Meta:
        verbose_name='服务大类'
        verbose_name_plural='服务大类'
        managed = True
        db_table = 'srvtopty'

    def __unicode__(self):
        return  u'%s' % self.ttname

    def __str__(self):
        return self.ttname


TOPCODELIST = Srvtopty.objects.filter(company=common.constants.COMPANYID,flag='Y').values_list('topcode','ttname')
class Serviece(GenesisModel,ItemModel,ArchivementBaseModel):
    TRUE_OR_FALSE = (
        ('Y','可以'),
        ('N','不可以'),
        )
    svrcdoe = models.CharField(db_column='SVRCDOE', max_length=16,blank=True,null=False,verbose_name='编号')  # Field name made lowercase.
    svrname = models.CharField(db_column='SVRNAME', max_length=100, blank=True, null=True,verbose_name='名称')  # Field name made lowercase.
    topcode = models.CharField(db_column='TOPCODE',max_length=16, blank=True, null=True,verbose_name='服务销售折扣分类')  # Field name made lowercase.
    cpoint = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True,verbose_name='积分')
    costamount = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True,verbose_name='成本金额')
    stdmins = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='服务时间(分钟）')
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=1,blank=True, null=True,verbose_name='项次')

    class Meta:
        verbose_name='服务项目'
        verbose_name_plural='服务项目'
        managed = True
        db_table = 'serviece'
        unique_together = (('company', 'svrcdoe'),)

    # def __init__(self,*args,**kwargs):
    #     super(Serviece, self).__init__(self,*args, **kwargs)
    #     self._meta.get_field('topcode').choices = Srvtopty.objects.filter(company=self.company,flag='Y').values_list('topcode','ttname')

    def __str__(self):
        return self.svrname

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        cardtype = Cardtype.objects.get_or_create(company=self.company,cardtype=self.svrcdoe)[0]
        cardtype.cardname=self.svrname
        cardtype.price =self.price
        cardtype.comptype='times'
        cardtype.suptype='20'
        cardtype.ttype='S'
        cardtype.sguuid=self.uuid
        cardtype.brand = self.brand
        cardtype.discountclass = self.discountclass
        cardtype.displayclass1 = self.displayclass1
        cardtype.displayclass2 = self.displayclass2
        cardtype.marketclass1 = self.marketclass1
        cardtype.marketclass2 = self.marketclass2
        cardtype.marketclass3 = self.marketclass3
        cardtype.marketclass4 = self.marketclass4
        cardtype.financeclass1 = self.financeclass1
        cardtype.financeclass2 = self.financeclass2
        cardtype.save()

        # servieceprice = Servieceprice.objects.get_or_create(company=self.company,srvuuid=self,qty=1)[0]
        # servieceprice.srvcode = self.svrcdoe
        # servieceprice.amount = self.price
        # servieceprice.save()


class Servieceprice(GenesisModel):
    srvuuid = models.ForeignKey('serviece',db_column='srvuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='服务项目')
    srvcode = models.CharField(db_column='srvcode', max_length=16,blank=True,null=False,verbose_name='项目编号')  # Field name made lowercase.
    qty = models.IntegerField(default=1,null=True,blank=True,verbose_name='次数')
    price = models.DecimalField(decimal_places=2,default=0,max_digits=10,null=True,verbose_name='单次价格')
    amount = models.DecimalField(decimal_places=2,default=0,max_digits=10,null=True,verbose_name='总价')
    commission = models.DecimalField(decimal_places=4,default=0,max_digits=5,null=True,verbose_name='销售提成')
    achivement = models.DecimalField(decimal_places=4,default=1,max_digits=5,null=True,verbose_name='销售业绩')
    fromdate = models.DateField(null=True,blank=True,verbose_name='价格生效起始日期')
    todate = models.DateField(null=True,blank=True,verbose_name='价格生效结束日期')
    saleflag = models.CharField(max_length=8, blank=True, default='Y', null=True, choices=SALESFLAG,verbose_name='可否销售')
    stype = models.CharField(max_length=8,blank=True,null=True,default='N',choices=STYPE,verbose_name='是否赠送')

    class Meta:
        verbose_name='服务疗程价格'
        verbose_name_plural='服务疗程价格'
        managed = True
        db_table='servieceprice'

    def __str__(self):
        return self.srvuuid.svrname +self.qty.__str__()+'次价'

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
        # super(Servieceprice, self).save()
        # self.srvcode=self.srvuuid.svrcdoe
        # self.save()

class Wharehouse(GenesisModel):
    wharehousecode = models.CharField(max_length=16,db_column='wharehousecode',blank=False,default='00',verbose_name='仓库编号')
    wharehousename = models.CharField(max_length=32,db_column='wharehousename',null=True,blank=True,default='',verbose_name='仓库名称')
    lastockdate = models.CharField(max_length=8,db_column='lastockdate',blank=True,null=True,verbose_name='最后一次盘点日期')
    # storecode = models.ForeignKey('Storeinfo',db_column='storecode',null=True,on_delete=models.SET_NULL,verbose_name='所属店铺')
    storecode = models.CharField(max_length=16,choices=STOREINFO,null=True,blank=True,verbose_name='所属店铺')
    saleatr  = models.CharField(max_length=16,choices=SALEATR,null=True,blank=True,verbose_name='允许操作')

    class Meta:
        verbose_name='仓库设定'
        verbose_name_plural='仓库设定'
        managed = True
        db_table ='wharehouse'
        unique_together = ("company", "wharehousecode")

    # def __init__(self,*args,**kwargs):
    #     super(Wharehouse, self).__init__(self,*args, **kwargs)
    #     self._meta.get_field('storecode').choices = Storeinfo.objects.filter(company=self.company,flag='Y').values_list('storecode','storename')

    def __str__(self):
        return self.wharehousename


class Supplier(GenesisModel):
    FLAG =(
        ('Y','有效'),
        ('N','无效'),
    )
    supplierid = models.CharField(max_length=16,blank=True,null=True,verbose_name='往来客户编号')
    suppliername = models.CharField(max_length=64,unique=True,blank=True,null=True,verbose_name='往来客户名称')
    supplieraddress = models.CharField(max_length=64, blank=True, null=True,verbose_name='地址')
    brand = models.CharField(max_length=128, blank=True, null=True)
    currency = models.CharField(max_length=8, blank=True, null=True,verbose_name='结算货币')
    totalmoney = models.DecimalField(max_digits=16, decimal_places=2,default=0,blank=True,verbose_name='总结余金额')
    freezemoney = models.DecimalField(max_digits=16, decimal_places=2,default=0,blank=True,verbose_name='冻结金额')
    availablemoney = models.DecimalField(max_digits=16, decimal_places=2,default=0,blank=True,verbose_name='可用金额')
    flag = models.CharField(max_length=8, choices=FLAG,default='Y',blank=True, null=True,verbose_name='是否有效')


    class Meta:
        verbose_name='往来客户'
        verbose_name_plural='往来客户'
        managed = True
        db_table = 'supplier'
        unique_together = (('company', 'supplierid'),)


    def __str__(self):
        return self.suppliername


class Promotions(GenesisModel):
    MAINTTYPE=(
        ('10','特价活动'),
        ('20','特殊折扣活动'),
        ('30','组合销售活动')
    )
    promotionsid = models.CharField(max_length=16,blank=True,null=True)
    promotionsname = models.CharField(max_length=64, blank=True, null=True,verbose_name='活动名称')
    mainttype = models.CharField(max_length=8, choices=MAINTTYPE,blank=True, null=True,verbose_name='活动大类')
    s_price = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True,verbose_name='')
    emplperc = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fromdate = models.CharField(max_length=8, blank=True, null=True,verbose_name='')
    todate = models.CharField(max_length=8, blank=True, null=True,verbose_name='')
    promotionsstatus = models.CharField(max_length=8, blank=True, null=True,verbose_name='')
    photofile = models.CharField(max_length=64, blank=True, null=True)
    mainpgroupid = models.CharField(max_length=16, blank=True, null=True)
    promotionsgroupid =models.ForeignKey('Promotionsgroup',db_column='Promotionsgroupuuid', blank=True, null=True,on_delete=models.SET_NULL)
    vipgroupid = models.CharField(max_length=16, blank=True, null=True)
    sendgroupid = models.CharField(max_length=16, blank=True, null=True)
    sendqty = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)
    disc = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    mainqty = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'promotions'


class Promotionsdetail(GenesisModel):
    # promotionssukid = models.BigAutoField(primary_key=True)
    # promotionsuuid = models.ForeignKey('Promotions',db_column='promotionsuuid', blank=True, null=True,on_delete=models.SET_NULL)
    SGCODE = Serviece.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('svrcdoe', 'svrname')

    promotionsuuid = models.ForeignKey('Promotions',db_column='promotionsuuid', blank=True, null=True,on_delete=models.SET_NULL)
    # promotionsgroupid =models.ForeignKey('Promotionsgroup',db_column='Promotionsgroupuuid', blank=True, null=True,on_delete=models.SET_NULL)
    promotionsid = models.CharField(max_length=16,db_column='promotionsid', blank=True, null=True)
    promotionsseq = models.CharField(max_length=8, blank=True, null=True)
    ttype = models.CharField(max_length=8, choices=TTYPE,blank=True, null=True)
    sgcode = models.CharField(max_length=24, choices=SGCODE,blank=True, null=True)
    s_qty = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    s_price = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    s_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    custperc = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,verbose_name='会员消费额折算率')
    emplperc = models.DecimalField(max_digits=8, decimal_places=4,default=0, blank=True, null=True)
    emplguideperc = models.DecimalField(max_digits=8,decimal_places=4,default=1,blank=True,null=True)
    emplpoint =  models.DecimalField(max_digits=8,decimal_places=2,default=1,blank=True,null=True)
    stype = models.CharField(max_length=8, choices=STYPE,blank=True, null=True)
    cardtype = models.CharField(max_length=16, blank=True, null=True)
    detailtype = models.CharField(max_length=8, blank=True, null=True,verbose_name='明细对应类型')
    comptype = models.CharField(max_length=8, blank=True, null=True,verbose_name='')
    valdays = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)
    normal_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    normal_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    present_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    present_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oriprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oriqty = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    oriamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotionsprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotionsqty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotionsamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'promotionsdetail'


class Promotionsgroup(GenesisModel):
    # id = models.BigAutoField(primary_key=True)
    pgroupid = models.CharField(max_length=16,unique=True)
    pgroupname = models.CharField(max_length=128,blank=True,null=True)
    pgrouptype = models.CharField(max_length=8, blank=True, null=True)
    fromdate = models.CharField(max_length=8, blank=True, null=True)
    todate = models.CharField(max_length=8, blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'promotionsgroup'


class Promotionsgroupdetail(GenesisModel):
    # id = models.BigAutoField(primary_key=True)
    pgroupuuid = models.ForeignKey('Promotionsgroup',db_column='pgroupuuid',blank=True,null=True,on_delete=models.DO_NOTHING)
    pgroupid = models.CharField(max_length=16, blank=True, null=True,verbose_name='分组编号')
    pgroupitem = models.IntegerField(blank=True, null=True)
    pgroupcondition = models.CharField(max_length=16, blank=True, null=True)
    pgcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='项目编号')
    qty1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,verbose_name='数量')
    price1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,verbose_name='活动价')
    disc = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True,verbose_name='折扣')
    amount1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='金额')
    ttype = models.CharField(max_length=8,choices=TTYPE, blank=True, null=True,verbose_name='类别')
    oriprice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,verbose_name='原价')

    class Meta:
        managed = True
        db_table = 'promotionsgroupdetail'

INFORMATION_TYPE_LIST=(('10','基础信息'),('20','入会信息'),('30','服务信息'))
class VipInformationItemList(GenesisModel):
    information_type = models.CharField(max_length=32,blank=True,null=True,verbose_name='信息类型')
    information_item_id = models.CharField(max_length=16,blank=True,null=True,verbose_name='信息项编码')
    information_item = models.CharField(max_length=64,blank=True,null=True,verbose_name='信息项')

    class Meta:
        managed = True
        db_table = 'vipinformationitemlist'
#
# class VipInformation(GenesisModel):
#     vip=models.ForeignKey('vip',db_column='vipuuid',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='客户')


# POSITION = Position.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('positioncode',
BASENUMTYPE=(
    ('10','实操'),
    ('20','业绩'),
    ('30','积点')
)
class ArchivementRuler(BaseModel):
    storecode = models.CharField(max_length=16,choices=STORECODE,blank=True,null=True,verbose_name='门店')
    archivementclass1 = models.CharField(max_length=16,choices=ARCHIVEMENTCLASS1,default='',blank=True,null=True,verbose_name='业绩分类1')
    archivementclass2 = models.CharField(max_length=16,choices=ARCHIVEMENTCLASS2,default='',blank=True,null=True,verbose_name='业绩分类2')
    position = models.CharField(max_length=16,choices=POSITION,blank=True,null=True,verbose_name='岗位')
    basenumtype = models.CharField(max_length=16,default='10',choices=BASENUMTYPE,blank=True,null=True,verbose_name='提成计算基数类型')
    frombasenum = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='提成计算基数起始金额')
    tobasenum = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True,null=True,verbose_name='提成计算基数截止金额')
    tichengperc = models.DecimalField(max_digits=6,decimal_places=2,default=0,blank=True,null=True,verbose_name='提成比例')
    tichengbase = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='提成速算基数')

    class Meta:
        verbose_name = '提成规则'
        verbose_name_plural = '提成规则'
        managed = True
        db_table = 'archivementruler'



#
# class CompanyItem(CommonBaseModel):
#     company_item_code = models.CharField(max_length=16, blank=True, null=True, verbose_name='收费项目编号')
#     company_item_name = models.CharField(max_length=256, blank=True, null=True, verbose_name='收费项目名称')
#     company_item_desc = models.CharField(max_length=512,blank=True,null=True,verbose_name='收费项目描述')
#     company_item_qty = models.IntegerField(default=1, blank=True, null=True, verbose_name='数量')
#     company_pay_period = models.CharField(max_length=16, choices=COMPANY_PAY_PERIOD, blank=True, null=True, verbose_name='单位')
#     company_item_price = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True, verbose_name='价格')
#     company_item_amount = models.DecimalField(max_digits=16,decimal_places=2, blank=True,null=True,verbose_name='金额')
#     companylist = MultiSelectField(choices=COMPANYLIST, blank=True, null=True, verbose_name='适用公司')
#     storelist = MultiSelectField(choices=STOREINFO, blank=True, null=True, verbose_name='适用门店')
#     # flag= models.CharField(max_length=16,choices=FLAG,blank=True,null=True,verbose_name='是否有效')
#
#     class Meta:
#         managed = True
#         db_table = 'CompanyItem'
#         verbose_name = '商户项目'
#         verbose_name_plural = verbose_name
#
#
# ORDER_STATUS=(
#     ('10','订单未支付'),
#     ('20','订单已支付'),
#     ('90','订单作废')
# )
# class CompanyOrder(CommonBaseModel):
#     wechatuser = models.ForeignKey(WechatUser, blank=True, null=True, verbose_name='微信用户')
#     openid = models.CharField(max_length=128, blank=True, null=True, verbose_name='openid')
#     unionid = models.CharField(max_length=128, blank=True, null=True, verbose_name='unionid')
#     order_no = models.CharField(max_length=128, blank=True, null=True, verbose_name='订单号')
#     order_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='支付金额')
#     order_status = models.CharField(max_length=8, blank=True, null=True, verbose_name='订单状态')
#     payed_datetime = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name='订单支付时间')
#     order_company = models.CharField(max_length=16,blank=True,null=True,verbose_name='订单公司')
#     wx_prepay_id = models.CharField(max_length=64,blank=True,null=True,verbose_name='微信预付订单号')
#     wx_transaction_id = models.CharField(max_length=32,blank=True,null=True,verbose_name='微信订单号')
#
#
#     class Meta:
#         managed = True
#         db_table = 'CompanyOrder'
#         verbose_name = '商户订单'
#         verbose_name_plural = verbose_name
#
#
# class CompanyOrderItem(CommonBaseModel):
#     company_order = models.ForeignKey(CompanyOrder, blank=True, null=True, verbose_name='订单')
#     company_item = models.ForeignKey(CompanyItem,blank=True,null=True,verbose_name='订单项目')
#     order_no = models.CharField(max_length=128, blank=True, null=True, verbose_name='订单号')
#     order_item = models.CharField(max_length=32, blank=True, null=True, verbose_name='订单项目')
#     # companylist = MultiSelectField(choices=STOREINFO, blank=True, null=True, verbose_name='续费公司')
#     storelist = MultiSelectField(choices=STOREINFO, blank=True, null=True, verbose_name='续费门店')
#
#     payed_qty = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True, null=True,
#                                      verbose_name='支付店月数')
#     company_pay_period = models.CharField(max_length=16, choices=COMPANY_PAY_PERIOD, blank=True, null=True, verbose_name='单位')
#     payed_price = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                      verbose_name='店月单价')
#     payed_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                       verbose_name='付款金额')
#     order_fromdate = models.DateField(blank=True, null=True, verbose_name='付款生效开始日期')
#     order_todate = models.DateField(blank=True, null=True, verbose_name='付款生效截止日期')
#
#     class Meta:
#         managed = True
#         db_table = 'CompanyOrderItem'
#         verbose_name = '商户订单内容'
#         verbose_name_plural = verbose_name
#
#
# class CompanyOrderPayInfo(CommonBaseModel):
#     company_order = models.ForeignKey(CompanyOrder, blank=True, null=True, verbose_name='订单')
#     order_no = models.CharField(max_length=128, blank=True, null=True, verbose_name='订单号')
#     payed_method = models.CharField(max_length=32, blank=True, null=True, verbose_name='付款方式')
#     payed_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, blank=True, null=True,
#                                     verbose_name='付款金额')
#
#     class Meta:
#         managed = True
#         db_table = 'CompanyOrderPayInfo'
#         verbose_name = '商户订单付款信息'
#         verbose_name_plural = verbose_name