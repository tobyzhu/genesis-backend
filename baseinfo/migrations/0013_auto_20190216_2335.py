# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-16 15:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0012_auto_20190216_1534'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'managed': True, 'verbose_name': 'item', 'verbose_name_plural': 'item'},
        ),
        migrations.AlterModelTable(
            name='item',
            table='item',
        ),
    ]
