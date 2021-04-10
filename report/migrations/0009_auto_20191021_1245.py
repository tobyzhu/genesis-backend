# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-21 12:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_auto_20191021_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreportvip',
            name='vipuuid',
            field=models.ForeignKey(blank=True, db_column='vipuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Vip', verbose_name='会员'),
        ),
    ]
