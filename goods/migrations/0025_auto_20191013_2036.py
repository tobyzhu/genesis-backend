# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-13 20:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0024_auto_20191013_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockmst',
            name='wharehousecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='盘点仓库'),
        ),
    ]
