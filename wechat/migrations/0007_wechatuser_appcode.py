# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-21 22:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0006_auto_20191021_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatuser',
            name='appcode',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='应用编码'),
        ),
    ]