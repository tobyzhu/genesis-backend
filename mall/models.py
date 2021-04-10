#coding = utf-8

from django.db import models


from adviser.models import *
from baseinfo.models import Serviece,Goods,Srvtopty,Goodsct,BRAND
from cashier.models import *
from common.constants import *
# Create your models here.


class onlineCommonBaseModel(models.Model):
    # uuid = models.UUIDField(primary_key=True,auto_created=True,editable=False,default=uuid.uuid4,null=False,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name='建立时间')
    last_modified = models.DateTimeField(auto_created=True,default=timezone.now,editable=False,verbose_name='最后修改时间')
    creater = models.CharField(max_length=16,default='anonymous',blank=True,null=True,verbose_name='创建者')
    flag = models.CharField(max_length=8,choices=FLAG,default='Y',editable=False,blank=True,null=True,verbose_name='是否删除')
    company = models.CharField(max_length=8,default=common.constants.COMPANYID,null=True,blank=True,verbose_name='公司')
    # storecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='门店')

    class Meta:
        abstract=True

    def delete(self, using=None, keep_parents=False):
        self.flag='N'
        self.save()

class Banner(onlineCommonBaseModel):
    appcode = models.CharField(max_length=16,blank=True,null=True,verbose_name='小程序编号')
    apppage = models.CharField(max_length=128,blank=True,null=True,verbose_name='页面')
    linkURL = models.URLField(max_length=128,blank=True,null=True,verbose_name='链接')
    bannerimage = models.ImageField(upload_to='static/images',blank=True,null=True,verbose_name='展示图片')
    orderno = models.DecimalField(max_digits=8,decimal_places=2,default=100,blank=True,null=True,verbose_name='序号')

    class Meta:
        verbose_name='Banner'
        verbose_name_plural=verbose_name
        managed =True
        db_table='banner'

class onlineShowType(onlineCommonBaseModel):
    ttype = models.CharField(max_length=16,choices=common.constants.TTYPE,blank=True,null=True,verbose_name='分类')
    showtypecode = models.CharField(max_length=32,choices=BRAND,blank=True,null=True,verbose_name='代码')
    showtypename = models.CharField(max_length=32,blank=True,null=True,verbose_name='名称')
    showtypeimage =  models.ImageField(upload_to='static/images',blank=True,null=True,verbose_name='展示图片')
    showtypeurl = models.URLField(blank=True,null=True,verbose_name='链接')
    orderno = models.IntegerField(default=100,blank=True,null=True,verbose_name='序号')

    class Meta:
        verbose_name='线上显示分类'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'onlineshowtype'

    def __init__(self, *args, **kwargs):
        super(onlineShowType, self).__init__(*args, **kwargs)
        self._meta.get_field('showtypecode').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='brand').values_list( 'itemname', 'itemvalues')

    def __str__(self):
        return self.showtypename

class onlineShowItem(onlineCommonBaseModel):
    onlineShowType = models.ForeignKey('onlineShowType',blank=True,null=True,verbose_name='在线显示分类')
    serviece = models.ForeignKey(Serviece,blank=True,null=True,verbose_name='服务项目')
    goods = models.ForeignKey(Goods,blank=True,null=True,verbose_name='商品')
    itemdesc = models.CharField(max_length=128,blank=True,null=True,verbose_name='项目描述')
    small_showimage =  models.ImageField(upload_to='static/images',blank=True,null=True,verbose_name='小展示图片')
    # large_showimage = models.ImageField(upload_to='static/images', blank=True, null=True, verbose_name='大展示图片')
    onlineprice = models.DecimalField(max_digits=16,decimal_places=2,default=0,blank=True,null=True,verbose_name='线上价格')
    orderno = models.IntegerField(default=100,blank=True,null=True,verbose_name='序号')

    class Meta:
        verbose_name='线上项目'
        verbose_name_plural=verbose_name
        managed = True
        db_table = 'onlineshowitem'

    # def __init__(self, *args, **kwargs):
    #     super(onlineShowItem, self).__init__(*args, **kwargs)
        # self._meta.get_field('').choices = Appoption.objects.filter(company=self.company, flag='Y', seg='brand').values_list( 'itemname', 'itemvalues')

    def __str__(self):
        return self.itemdesc

IMAGETYPELIST = (
    ('small','小图'),
    ('large','大图'),
    ('detail','详图')
)
class onlineItemImage(onlineCommonBaseModel):
    onlineshowitem = models.ForeignKey(onlineShowItem,blank=True,null=True,verbose_name='线上项目')
    imagetype = models.CharField(max_length=16,choices=IMAGETYPELIST,blank=True,null=True,verbose_name='图片类型')
    image_url= models.ImageField(upload_to='static/images', blank=True, null=True, verbose_name='展示图片')
    orderno = models.IntegerField(default=100, blank=True, null=True, verbose_name='序号')

    class Meta:
        verbose_name='线上项目图片'
        verbose_name_plural = verbose_name
        managed = True
        db_table = 'onlineitemimage'

    def __str__(self):
        return self.imagetype

