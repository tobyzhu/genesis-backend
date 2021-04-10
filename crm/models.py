from django.db import models
import sys
import uuid
import django.utils.timezone as timezone
from multiselectfield import MultiSelectField

from common.constants import FLAG, SALESFLAG, COMPTYPE, TTYPE,SCHEDULELIST,VIPTYPE, CASETYPE, CASESTATUS,SOURCE,CommonBaseModel,CompanyCommonBaseModel

from baseinfo.models import Vip,Empl,Appoption
from common.constants import GenesisModel,FLAG,COMPANYID

VIPCASETYPE = Appoption.objects.filter(company=COMPANYID,flag='Y',seg='vipcasetype').values_list('itemname','itemvalues')

class VipCaseDetail(GenesisModel):
    vipuuid = models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    casetype = models.CharField(max_length=8,choices=VIPCASETYPE,default='10',blank=True,null=True,verbose_name='类型')
    detaildescription = models.TextField(blank=True,null=True,verbose_name='沟通情况记录')
    detail = models.CharField(max_length=1024,blank=True,null=True,verbose_name='情况描述')
    ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='员工')
    nextdate = models.DateField(auto_now_add=False,auto_created=False,blank=True,null=True,verbose_name='下次回访日期')
    nextecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='下次任务执行人工号')
    status = models.CharField(max_length=8,choices=CASESTATUS,blank=True,default='10',verbose_name='状态')


    class Meta:
        verbose_name='客户沟通记录'
        verbose_name_plural='客户沟通记录'
        managed = True
        db_table='vipcasedetail'

    def __str__(self):
        return self.casetype


# 客户服务案例规则
# 正常服务/销售：    销售人员回访规则：第a天回访
#                   服务人员：第b天回访
# 新客体验服务规则，
class CaseRuler(models.Model):
    case_ruler_name = models.CharField(max_length=64,blank=True,null=True,verbose_name='规则名称')
    valiflag = models.CharField(max_length=8,choices=FLAG,default='Y',blank=True,null=True,verbose_name='是否有效')

    class Meta:
        verbose_name = '客户服务规则'
        verbose_name_plural = '客户服务规则'
        managed = True
        db_table = 'CaseRuler'

CASETYPE = Appoption.objects.filter(company=COMPANYID,flag='Y',seg='casetype').values_list('itemname','itemvalues')
EMPLLIST = Empl.objects.filter(company=COMPANYID,flag='Y').values_list('ecode','ename')

class CrmCase(GenesisModel):
    casetype = models.CharField(max_length=8,choices=CASETYPE,blank=True,null=True,verbose_name='类型')
    viptype = models.CharField(max_length=8,choices=VIPTYPE, default='10',blank=True,null=True,verbose_name='会员/散客')
    vipuuid = models.ForeignKey(Vip,db_column='vipuuid',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='客户唯一号')
    empl = models.ForeignKey('baseinfo.Empl',db_column='empl',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='责任人')
    ecode = models.CharField(max_length=16,blank=True,null=True,verbose_name='员工')
    ecodelist =  MultiSelectField(choices=EMPLLIST,blank=True,null=True,verbose_name='责任员工')
    status = models.CharField(max_length=8,choices=CASESTATUS,blank=True,default='10',verbose_name='状态')
    finishedate = models.DateField(blank=True,null=True,verbose_name='实际完成日期')
    planbegindate = models.DateField(blank=True,null=True,verbose_name='计划开始日期')
    planfinishdate =  models.DateField(blank=True,null=True,verbose_name='计划完成日期')
    casedesc = models.CharField(max_length=128,blank=True,null=True,verbose_name='描述')
    vsdate = models.DateField(blank=True,null=True,verbose_name='交易日期')

    class Meta:
        verbose_name = '案例'
        verbose_name_plural = '案例'
        managed = True
        db_table = 'crmcase'

    def __str__(self):
        if self.vipuuid.vname==None:
            self.vipuuid.vname= ''

        if self.vipuuid.vcode==None:
            self.vipuuid.vcode= ''

        if self.viptype == '10':
            return  '会员:'+ self.vipuuid.vname + ':'+ self.vipuuid.vcode
        elif self.viptype =='20':
            return  '散客：' + self.vipuuid.vname

class CrmCaseDetail(GenesisModel):
    ACTIONTYPE=(
        ('10','日常回访'),
        ('20','邀约'),
        ('30','客情处理'),
        ('90','其他'),
    )

    caseid = models.ForeignKey('CrmCase',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='案例')
#    vsdate = models.DateTimeField(default=timezone.now(),blank=True,null=True)
    detaildescription = models.TextField(blank=True,null=True,verbose_name='沟通情况记录')
    detail = models.CharField(max_length=512,blank=True,null=True,verbose_name='咨询记录')
    ecode = models.ForeignKey('baseinfo.Empl',db_column='ecode',blank=True,null=True,on_delete=models.SET_NULL,verbose_name='员工')

    class Meta:
        verbose_name='沟通记录'
        verbose_name_plural='沟通记录'
        managed = True
        db_table ='crmcasedetail'

    def __str__(self):
        # return self.uuid
        if self.detail ==None:
            self.detail=''
        return self.detail

class Term(models.Model):
    termtype=models.CharField(max_length=8,blank=True,null=True,verbose_name='术语类型')
    term=models.CharField(max_length=512,blank=True,null=True,verbose_name='服务术语')

class CrmSubReport(CompanyCommonBaseModel):
    crmsubreportName = models.CharField(max_length=64,blank=True,null=True,verbose_name='报表名称')

    class Meta:
        managed=True
        verbose_name='客户关系报表分支表'
        verbose_name_plural=verbose_name
        db_table='crmsubreport'

    def __str__(self):
        return self.crmsubreportName


CRMREPORTITEMTYPE = (
    ('text','文本'),
    ('decimal','数值'),
    ('datetime','日期'),
    ('radio','单选'),
    ('check','多选'),
    ('other','其他')
)

class CrmInfoItem(CompanyCommonBaseModel):
    crmsubreport= models.ForeignKey(CrmSubReport,blank=True,null=True,verbose_name='报表')
    itemid = models.CharField(max_length=8,blank=True,null=True,verbose_name='报表项序号')
    itemname = models.CharField(max_length=64,blank=True,null=True,verbose_name='报表项名称')
    itemtype = models.CharField(max_length=16,choices=CRMREPORTITEMTYPE,blank=True,null=True,verbose_name='报表项类型')
    requireflag = models.CharField(max_length=8,blank=True,choices=FLAG,null=True,verbose_name='是否必填')
    itemflag = models.CharField(max_length=8,choices=FLAG,blank=True,null=True,verbose_name='标志')

    class Meta:
        managed=True
        verbose_name='问题项目'
        verbose_name_plural=verbose_name
        db_table='crm_infoitem'

    def __str__(self):
        return self.itemname

class CrmInfoItemChoice(CompanyCommonBaseModel):
    crminfoitem = models.ForeignKey(CrmInfoItem,blank=True,null=True,verbose_name='报表项次')
    orderno = models.CharField(max_length=8,blank=True,null=True,verbose_name='序号')
    choiceitemname = models.CharField(max_length=64,blank=True,null=True,verbose_name='项次内容')

    class Meta:
        managed=True
        verbose_name='问题选择项'
        verbose_name_plural=verbose_name
        db_table='crm_reportitem_choice'

    def __str__(self):
        return self.choiceitemname