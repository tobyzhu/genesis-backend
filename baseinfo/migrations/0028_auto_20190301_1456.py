# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 06:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0027_auto_20190301_1403'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardtype',
            name='saleperc',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='salesrvprec',
        ),
    ]