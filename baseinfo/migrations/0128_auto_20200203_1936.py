# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-03 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0127_vipspecialdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeinfo',
            name='pay_period',
            field=models.CharField(blank=True, choices=[('5', '年'), ('4', '季'), ('1', '日'), ('2', '周'), ('3', '月')], max_length=16, null=True, verbose_name='付款周期'),
        ),
        migrations.AlterField(
            model_name='vipspecialdate',
            name='specdatetype',
            field=models.CharField(blank=True, choices=[('011', '阴历生日'), ('021', '结婚纪念日'), ('010', '生日'), ('020', '入会日期')], default='', max_length=16, null=True, verbose_name='日期类型'),
        ),
    ]
