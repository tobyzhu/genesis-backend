# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-16 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0007_auto_20181207_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstranshead',
            name='saleatr',
            field=models.CharField(choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出')], db_column='saleatr', max_length=8, verbose_name='单号类型'),
        ),
    ]