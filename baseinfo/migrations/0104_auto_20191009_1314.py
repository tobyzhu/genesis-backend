# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-09 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0103_archivementruler_storecode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivementruler',
            name='storecode',
            field=models.CharField(blank=True, choices=[('00', '总部'), ('01', '丽迪亚店'), ('02', '军创店'), ('03', '国际城店'), ('04', '天蕴店'), ('05', '信诚店'), ('88', '练习')], max_length=16, null=True, verbose_name='门店'),
        ),
    ]