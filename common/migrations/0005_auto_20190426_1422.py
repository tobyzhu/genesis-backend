# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-04-26 06:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20190412_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequence',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='wifilist',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
    ]
