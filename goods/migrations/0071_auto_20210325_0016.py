# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-25 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0070_auto_20210319_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstransdetail',
            name='gcode',
            field=models.CharField(blank=True, choices=[('2030700000', '育肌酶'), ('2030701000', '育肌酶'), ('2030702001', '还氧蛋白精华液'), ('2041200000', '平衡焕肤-喷雾-HYDB')], db_column='gcode', max_length=16, null=True, verbose_name='商品'),
        ),
    ]
