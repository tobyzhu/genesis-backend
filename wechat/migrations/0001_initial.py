# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-12 23:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WechatAppFuntion',
            fields=[
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('uuid', models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司')),
                ('storecode', models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店')),
                ('functiontype', models.CharField(blank=True, max_length=16, null=True, verbose_name='功能类型')),
                ('functionid', models.CharField(blank=True, max_length=16, null=True, verbose_name='功能模块编号')),
                ('functionname', models.CharField(blank=True, max_length=32, null=True, verbose_name='功能名称')),
                ('ecode', models.CharField(blank=True, max_length=16, null=True, verbose_name='员工编号')),
                ('id', models.IntegerField(blank=True, default=1, null=True, verbose_name='序号')),
                ('text', models.CharField(blank=True, max_length=32, null=True, verbose_name='描述')),
                ('url', models.CharField(blank=True, max_length=128, null=True, verbose_name='链接')),
                ('image', models.CharField(blank=True, max_length=128, null=True, verbose_name='图片')),
                ('parentfunction', models.CharField(blank=True, max_length=16, null=True, verbose_name='上级模块')),
            ],
            options={
                'verbose_name_plural': '用户',
                'db_table': 'tb_users',
                'verbose_name': '用户',
            },
        ),
    ]