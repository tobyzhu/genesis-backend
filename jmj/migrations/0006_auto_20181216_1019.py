# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-16 02:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0005_olddata_saleatr'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='olddata',
            options={'managed': True, 'verbose_name': '往年销售数据', 'verbose_name_plural': '往年销售数据'},
        ),
        migrations.AlterField(
            model_name='olddata',
            name='salesamount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='金额'),
        ),
        migrations.AlterField(
            model_name='olddata',
            name='salesqty',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='数量'),
        ),
        migrations.AlterField(
            model_name='olddata',
            name='storecode',
            field=models.CharField(blank=True, choices=[('1', '青岛店'), ('2', '沈阳店'), ('3', '大连店'), ('5', '济南店')], max_length=8, null=True, verbose_name='店铺'),
        ),
    ]
