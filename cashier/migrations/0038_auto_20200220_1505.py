# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-20 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0037_auto_20200220_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='ctype',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='项次类型'),
        ),
    ]
