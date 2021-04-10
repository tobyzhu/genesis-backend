# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-18 22:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0031_auto_20191009_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='oweamount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='欠款金额'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='payamount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='定金金额'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='planamount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='预订金额'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='playqty',
            field=models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=8, null=True, verbose_name='预订数量'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='remark',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='备注'),
        ),
    ]
