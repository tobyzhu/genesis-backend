# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-04 00:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0008_auto_20191101_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatappfunctions',
            name='appcode',
            field=models.CharField(blank=True, choices=[('100', '帮小主'), ('200', '最小主'), ('300', '小主咖')], max_length=32, null=True, verbose_name='小程序代号'),
        ),
        migrations.AlterField(
            model_name='wechatappfunctions',
            name='wxusertype',
            field=models.CharField(blank=True, choices=[('100', '商家员工'), ('200', '消费者')], max_length=16, null=True, verbose_name='小程序用户类型'),
        ),
    ]
