# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-16 04:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0009_auto_20181216_1114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportperiod',
            old_name='period',
            new_name='perioddesc',
        ),
    ]
