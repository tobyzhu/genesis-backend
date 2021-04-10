from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
# from baseinfo.models import Appoption,Storeinfo,Position,Empl,Vip,STOREINFO,COMPANYLIST

from baseinfo.models import Appoption,COMPANYLIST,VIPTAGS
import common.constants as constants
import uuid
from common.constants import GenesisModel,BaseModel
from multiselectfield import MultiSelectField

# class wxUser(AbstractUser):
#     USER_GENDER_CHOICES = (
#         (0, '女'),
#         (1, '男'),
#     )
#
#     sex = models.SmallIntegerField(choices=USER_GENDER_CHOICES, default=1, verbose_name="性别")
#     avatar = models.CharField(max_length=50, default="", null=True, blank=True, verbose_name="头像")
#     openid = models.CharField(max_length=64, db_index=True, verbose_name='openid')
#     unionid = models.CharField(max_length=64,blank=True,null=True,verbose_name='UnionId')
#
#     class Meta:
#         db_table = 'tb_users'
#         verbose_name = '用户'
#         verbose_name_plural = verbose_name
WEIXIN_USERTYPE_LIST=(
    ('100','商家员工'),
    ('200','消费者')
)

COMPANYLIST= Appoption.objects.filter(flag='Y',company='common',seg='company').values_list('itemname','itemvalues')

class WechatUser(BaseModel):
    """
    微信用户信息，与公众平台返回的信息保持一致;
    同时记录用户手机或id
    """
    openid = models.CharField(max_length=128, unique=True, db_index=True)
    unionid = models.CharField(max_length=128, blank=True, null=True)
    nickname = models.CharField(max_length=256, blank=True, null=True)
    sex = models.IntegerField(default=0)
    province = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    language = models.CharField(max_length=128, blank=True, null=True)
    avatarUrl = models.CharField(max_length=256, blank=True, null=True)
    privilege = models.CharField(max_length=128, blank=True, null=True)

    # 是否是真正的微信用户
    is_phantom = models.BooleanField(default=False)

    # 在用户注册之前，记录其手机号，注册之后就直接记录用户id了
    mobile = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    # customer = models.ForeignKey('customer.Customer', blank=True, null=True, related_name="+")
    # customer_binded = models.ForeignKey('customer.Customer', blank=True, null=True, related_name="+")  # 绑定账户
    is_follow = models.BooleanField(default=False)  # 是否关注美东东公众号
    sign = models.CharField(max_length=16, blank=True, null=True)
    sign_expire = models.BigIntegerField(default=0)

    user_type = models.CharField(max_length=8, choices=WEIXIN_USERTYPE_LIST,blank=True,null=True, verbose_name='用户类型')
    useruuid = models.UUIDField(null=True,blank=True,verbose_name='用户UUID')
    companylist = MultiSelectField(choices=COMPANYLIST,blank=True,null=True,verbose_name='可用公司')
    appcode = models.CharField(max_length=8,blank=True,null=True,verbose_name='应用编码')

    # def __unicode__(self):
    #     return self.openid + '^' + str(self.phone) + '^' +self.nickname

    class Meta:
        db_table = 'Wechat_User'

    def get_simple_dic(self):
        dic = {
            'nickname': self.nickname,
            'avatarUrl': self.avatarUrl,
        }
        return dic

    def check_openid(openid):
        user = WechatUser.objects.get(openid=openid)
        if user:
            return

    def get_ecode(self):
        if self.appcode=='100':
            try:
                empl =Empl.objects.get(company=self.company,openid=self.openid)
                ecode=empl.ecode
            except:
                ecode='888'
        return  ecode

    def get_vipuuid(self):
        if self.appcode=='300':
            try:
                vip = Vip.objects.get(company=self.company,openid=self.openid)
                vipuuid=vip.uuid
            except:
                vipuuid=''
            return vipuuid



APPLIST=(
    ('100','帮小主'),
    ('200','最小主'),
    ('300','小主咖')
)
class WechatAppFunctions(constants.GenesisModel):
    appcode = models.CharField(max_length=32,choices=APPLIST,blank=True,null=True,verbose_name='小程序代号')
    functiontype = models.CharField(max_length=16,blank=True,null=True,verbose_name='功能类型')
    functionid = models.CharField(max_length=16,blank=True,null=True,verbose_name='功能模块编号')
    functionname = models.CharField(max_length=32,blank=True,null=True,verbose_name='功能名称')
    # ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='员工编号')
    wxusertype = models.CharField(max_length=16,choices=WEIXIN_USERTYPE_LIST,blank=True,null=True,verbose_name='小程序用户类型')
    id = models.IntegerField(default=1,blank=True,null=True,verbose_name='序号')
    text = models.CharField(max_length=32,blank=True,null=True,verbose_name='描述')
    url = models.CharField(max_length=128,blank=True,null=True,verbose_name='链接')
    image= models.CharField(max_length=128,blank=True,null=True,verbose_name='图片')
    parentfunction = models.CharField(max_length=16,blank=True,null=True,verbose_name='上级模块')
    valiflag = models.CharField(max_length=8,choices=constants.FLAG,default='Y',blank=True,null=True,verbose_name='是否有效')

    class Meta:
        db_table = 'WechatAppFunctions'
        verbose_name = '微信小程序配置'
        verbose_name_plural = verbose_name
