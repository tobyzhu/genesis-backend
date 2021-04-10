# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-19 22:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0028_auto_20210319_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreportvip',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='report',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='report_item_ruler',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='reportclassdata',
            name='report_class_type',
            field=models.CharField(blank=True, choices=[('006', '6'), ('003', '家居/商品'), ('001', '储值'), ('010', '面部'), ('004', '即时'), ('020', '身体'), ('002', '服务/疗程'), ('030', '仪器'), ('005', '5')], max_length=32, null=True, verbose_name='分类'),
        ),
    ]
