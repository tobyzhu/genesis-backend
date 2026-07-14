#coding = utf-8
import uuid
from django.db import models

class TrialLead(models.Model):
    """试用申请线索"""
    STATUS_CHOICES = [
        ('pending', '待联系'),
        ('contacted', '已联系'),
        ('trial', '试用中'),
        ('converted', '已转化'),
        ('lost', '已流失'),
    ]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_name = models.CharField('门店名称', max_length=128)
    contact_name = models.CharField('联系人', max_length=64)
    phone = models.CharField('手机号', max_length=20)
    store_count = models.IntegerField('门店数量', default=1, help_text='计划使用的门店数')
    current_system = models.CharField('当前在用的系统', max_length=256, blank=True, null=True, help_text='如有请填写，方便我们了解你的需求')
    remark = models.TextField('备注', blank=True, null=True)
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    contacted_at = models.DateTimeField('联系时间', blank=True, null=True)

    class Meta:
        db_table = 'campaign_trial_lead'
        ordering = ['-created_at']
        verbose_name = '试用线索'
        verbose_name_plural = '试用线索'

    def __str__(self):
        return f'{self.store_name} - {self.contact_name} ({self.phone})'
