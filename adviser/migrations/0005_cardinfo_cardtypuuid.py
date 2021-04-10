# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 13:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0030_auto_20190301_1541'),
        ('adviser', '0004_auto_20190301_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardinfo',
            name='cardtypuuid',
            field=models.ForeignKey(blank=True, db_column='cardtypeuuid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='baseinfo.Cardtype', verbose_name='卡类'),
        ),
    ]