from django.db import models
from django.conf import settings
#from wechat.models import WechatUser
from multiselectfield import MultiSelectField

# Create your models here.
from common.constants import GenesisModel, CommonBaseModel, FLAG, COMPANYID
# from baseinfo.models import Appoption



# COMPANYLIST= Appoption.objects.filter(flag='Y',company='common',seg='company').values_list('itemname','itemvalues')
# COMPANY_PAY_PERIOD = Appoption.objects.filter(flag='Y',company='common',seg='company_pay_period').values_list('itemname','itemvalues')

class Sequence(GenesisModel):
    sequence = models.DecimalField(db_column='SEQUENCE', max_digits=20, decimal_places=0, default=1,blank=True,
                                   null=True)  # Field name made lowercase.
    tablecode = models.CharField(db_column='TABLECODE',max_length=40)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sequence'


class WifiList(GenesisModel):
    SSID = models.CharField(max_length=32,blank=False,null=False,verbose_name='SSID')
    BSSID = models.CharField(max_length=32,unique=True,blank=True,null=True,verbose_name='BSSID')
    valiflag = models.CharField(max_length=8,default='Y',blank=True,null=True,verbose_name='是否允许')

    class Meta:
        managed = True
        db_table = 'wifilist'

    # def __str__(self):
    #     return self.SSID


class GenesisUserProfile(models.Model):
    """
    扩展 Django auth.User：公司 + 多门店 + 与 hdsysuser/useright 的桥接。
    在 Admin「用户」页内联编辑；小程序/DRF 优先走此 Profile 鉴权。
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='genesis_profile',
        verbose_name='Django 用户',
    )
    company = models.CharField(
        max_length=16,
        default=COMPANYID,
        blank=True,
        verbose_name='所属公司',
    )
    default_storecode = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name='默认门店',
    )
    storelist = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='可用门店',
        help_text='逗号分隔门店编号，如 88,01,02；公司管理员可留空（表示全部门店）',
    )
    employee_code = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name='员工工号',
        help_text='对应 hdsysuser.sys_userid / 小程序 ecode',
    )
    display_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='显示姓名',
    )
    is_company_admin = models.BooleanField(
        default=False,
        verbose_name='公司管理员',
        help_text='等同 hdsysuser.sys_adm=Y，可登录公司下全部门店',
    )
    hdsysuser_uuid = models.UUIDField(
        blank=True,
        null=True,
        db_column='hdsysuser_uuid',
        verbose_name='关联 hdsysuser.uuid',
        help_text='可选；用于继承 useright 模块权限',
    )
    costpriceflag = models.CharField(
        max_length=8,
        choices=FLAG,
        default='N',
        blank=True,
        null=True,
        verbose_name='可查看成本价',
    )

    class Meta:
        managed = True
        db_table = 'genesis_user_profile'
        verbose_name = 'Genesis 用户扩展'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s @ %s' % (self.user.username, self.company)

    def rights_user_key(self):
        if self.hdsysuser_uuid:
            return str(self.hdsysuser_uuid).replace('-', '')
        hu = None
        try:
            from common.genesis_auth import profile_linked_hdsysuser
            hu = profile_linked_hdsysuser(self)
        except Exception:
            pass
        if hu:
            return hu.user_uuid_key()
        return str(self.user_id)

    def allowed_storecodes(self):
        from common.genesis_auth import profile_allowed_storecodes
        return profile_allowed_storecodes(self)

    def can_access_store(self, storecode):
        from common.genesis_auth import profile_can_access_store
        return profile_can_access_store(self, storecode)

    def module_rights(self, storecode=None):
        from common.genesis_auth import profile_module_rights
        return profile_module_rights(self, storecode)


# COMPANYLIST=(
#     ('yfy','yfy'),
#     ('yiren','yiren')
# )
# COMPANY_PAY_PERIOD=(
#     ('1','year')
# )

STOREINFO=(
    ('01','01'),
    ('02','02'),
    ('03','03'),
    ('04','04'),
    ('05','05')
)


# ITEMUNITS = (
#     (1, 'day'),
#     (2, 'month'),
#     (3, 'year')
# )
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