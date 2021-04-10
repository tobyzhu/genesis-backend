# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-27 15:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0009_auto_20181227_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviece',
            name='srvrptypecode',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='所属报表分类'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='topcode',
            field=models.CharField(blank=True, db_column='TOPCODE', max_length=16, null=True, verbose_name='大类'),
        ),
        migrations.AlterField(
            model_name='useright',
            name='sys_userid',
            field=models.ForeignKey(db_column='SYS_USERID', max_length=32, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Hdsysuser'),
        ),
    ]
