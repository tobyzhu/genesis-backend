from django.db import models

from common.constants import FLAG, SALESFLAG, COMPTYPE, TTYPE,SCHEDULELIST,VIPTYPE, CASETYPE, CASESTATUS,SOURCE

from baseinfo.models import Vip,Empl,Position,Goods

from common.constants import GenesisModel

# Create your models here.

#
# class Objectvalue2(models.Model):
#     objectname1 = models.CharField(max_length=40)
#     objectname2 = models.CharField(max_length=40)
#     langtype = models.CharField(max_length=1)
#     objectvalue = models.CharField(max_length=40, blank=True, null=True)
#
#     class Meta:
#         managed = True
#         db_table = 'objectvalue2'
#         unique_together = (('objectname1', 'objectname2', 'langtype'),)
#
#     def __str__(self):
#         return  self.objectname1

# class Enactmen(models.Model):
#     corpname = models.CharField(db_column='CORPNAME', max_length=100, blank=True, null=True,verbose_name='公司')  # Field name made lowercase.
#     storecode = models.CharField(db_column='STORECODE', primary_key=True, max_length=10,verbose_name='店铺编号')  # Field name made lowercase.
#     storename = models.CharField(db_column='STORENAME', max_length=100, blank=True, null=True,verbose_name='店铺名称')  # Field name made lowercase.
#     firstday = models.CharField(db_column='FIRSTDAY', max_length=8, blank=True, null=True,verbose_name='开业日期')  # Field name made lowercase.
#     multidiscable = models.CharField(db_column='MULTIDISCABLE', max_length=1, blank=True, null=True,verbose_name='直接打印提示')  # Field name made lowercase.
#     saledept = models.CharField(db_column='SALEDEPT', max_length=40, blank=True, null=True,verbose_name='销售品仓库')  # Field name made lowercase.
#     invoicetitle = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票抬头')
#     invoicefoot = models.CharField(max_length=256, blank=True, null=True,verbose_name='发票页脚')
#     usewhcode = models.CharField(max_length=32, blank=True, null=True,verbose_name='使用品仓库')
#
#     class Meta:
#         managed = False
#         db_table = 'enactmen'
#         verbose_name='门店信息'
#         verbose_name_plural='门店信息'

# 此表用于记录有哪些预警信息种类，各预警进行提醒哪些岗位的员工。
class AlterOption(models.Model):
    ALTERTYPE = (
        ('10','基本类'),
        ('20','CRM类'),
        ('30','库房管理类')
    )
    altername = models.CharField(db_column='altername',max_length=32,default='',blank=True,null=True,verbose_name='预警信息')
    altertype = models.CharField(db_column='altertype',max_length=8,choices=ALTERTYPE,default='10',blank=True,null=True,verbose_name='预警大类')
    positionlist = models.CharField(db_column='positionlist',max_length=32,blank=True,null=True,verbose_name='职位')
    relativewindows = models.CharField(db_column='relativewindows',max_length=64,blank=True,null=True,verbose_name='处理窗口')
    params = models.CharField(db_column='params',max_length=32,blank=True,null=True,verbose_name='参数')

    class Meta:
        verbose_name='预警选项设定'
        verbose_name_plural='预警选项设定'
        managed = True
        db_table = 'alteroption'

    def __str__(self):
        return self.altername

#此表记录各种类预警信息的详细记录。比如某个商品库存预警，010001号顾客流水预警。
class AlterInfo(HdmsModel):
    fromdate = models.DateField(db_column='fromdate',blank=True,null=True,verbose_name='开始日期')
    todate = models.DateField(db_column='todate',blank=True,null=True,verbose_name='截止日期')
    alterid = models.ForeignKey(AlterOption,db_column='alterid',blank=True,null=True,verbose_name='预警')
    ecode = models.ForeignKey(Empl,db_column='ecode',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='员工')
    vipuuid = models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='顾客')
    gcode = models.ForeignKey(Goods,db_column='gcode',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='商品')
    
