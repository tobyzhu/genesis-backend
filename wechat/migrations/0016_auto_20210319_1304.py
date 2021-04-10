# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-19 13:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0015_auto_20210308_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatappfunctions',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='wechatuser',
            name='company',
            field=models.CharField(blank=True, default='yfy', max_length=8, null=True, verbose_name='公司'),
        ),
    ]