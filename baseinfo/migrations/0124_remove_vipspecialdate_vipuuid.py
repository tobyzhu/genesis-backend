# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-01 15:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0123_auto_20200201_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vipspecialdate',
            name='vipuuid',
        ),
    ]
