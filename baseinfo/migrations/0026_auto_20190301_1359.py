# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 05:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0025_auto_20190301_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goods',
            name='saleprc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='svrprc',
        ),
    ]
