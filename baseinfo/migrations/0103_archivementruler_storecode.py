# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-09 13:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0102_auto_20191009_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivementruler',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='门店'),
        ),
    ]
