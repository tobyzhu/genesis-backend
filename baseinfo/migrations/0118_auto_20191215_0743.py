# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-15 07:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0117_auto_20191215_0733'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='goods',
            unique_together=set([('company', 'gcode')]),
        ),
    ]
