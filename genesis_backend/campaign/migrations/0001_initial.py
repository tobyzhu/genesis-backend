# Generated manually
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrialLead',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=128, verbose_name='门店名称')),
                ('contact_name', models.CharField(max_length=64, verbose_name='联系人')),
                ('phone', models.CharField(max_length=20, verbose_name='手机号')),
                ('store_count', models.IntegerField(default=1, help_text='计划使用的门店数', verbose_name='门店数量')),
                ('current_system', models.CharField(blank=True, help_text='如有请填写，方便我们了解你的需求', max_length=256, null=True, verbose_name='当前在用的系统')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('status', models.CharField(choices=[('pending', '待联系'), ('contacted', '已联系'), ('trial', '试用中'), ('converted', '已转化'), ('lost', '已流失')], default='pending', max_length=16, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('contacted_at', models.DateTimeField(blank=True, null=True, verbose_name='联系时间')),
            ],
            options={
                'verbose_name': '试用线索',
                'verbose_name_plural': '试用线索',
                'db_table': 'campaign_trial_lead',
                'ordering': ['-created_at'],
            },
        ),
    ]
