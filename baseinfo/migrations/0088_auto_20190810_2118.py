# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-10 21:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0087_auto_20190810_2116'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='create_time',
        #     field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='建立时间'),
        #     preserve_default=False,
        # ),
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='creater',
        #     field=models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者'),
        # ),
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='flag',
        #     field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除'),
        # ),
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='last_modified',
        #     field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间'),
        # ),

        # migrations.AlterField(
        #     model_name='storeinfo',
        #     name='storecode',
        #     field=models.CharField(blank=True, db_column='StoreCode', default='0', max_length=16, verbose_name='店铺编号'),
        # ),
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='uuid',
        #     field=models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True,
        #                            serialize=False),
        # ),
    ]
