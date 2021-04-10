from django.db import models

# Create your models here.

class OldCardTypeItemDetail(models.Model):
    company = models.CharField(max_length=16,blank=True,null=True,verbose_name='公司')
    cardtype = models.CharField(db_column='cardtype', max_length=16, blank=True, null=True,verbose_name='卡类')  # Field name made lowercase.
    cardname = models.CharField(db_column='cardname',max_length=32, blank=True, null=True,verbose_name='卡类名称')
    codetype = models.CharField(db_column='codetype', max_length=8, blank=True, null=True,verbose_name='编码类型')  # Field name made lowercase.
    stype = models.CharField(db_column='stype', max_length=16,verbose_name='是否赠送')  # Field name made lowercase.
    itemcode = models.CharField(max_length=16,blank=True, null=True,verbose_name='项目编号')
    times = models.DecimalField(max_digits=16,decimal_places=2, default=0,blank=True, null=True,verbose_name='次数')
    price = models.DecimalField(max_digits=16, decimal_places=4, default=0,blank=True, null=True,verbose_name='单次价')
    performance = models.DecimalField(max_digits=16, decimal_places=4, default=0,blank=True, null=True,verbose_name='员工业绩')
    linenumber = models.IntegerField(default=1,blank=True,null=True,verbose_name='行次')
    newitemcode =  models.CharField(max_length=16,blank=True, null=True,verbose_name='新项目编号')

    class Meta:
        verbose_name='老卡项目明细'
        verbose_name_plural='老卡项目明细'
        managed = True
        db_table = 'oldcardtypeitemdetail'
        ordering=['cardtype',]

    def __unicode__(self):
        return u'%s' %self.cardname

    def __str__(self):
        return self.cardname

