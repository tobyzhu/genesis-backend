# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-21 14:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0014_olddata2'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OldData2',
            new_name='OldData4',
        ),
        migrations.AlterModelTable(
            name='olddata4',
            table='olddata4',
        ),
    ]