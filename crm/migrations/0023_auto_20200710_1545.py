# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-07-10 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0022_auto_20200710_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmcase',
            name='empl',
            field=models.ForeignKey(blank=True, db_column='empl', null=True, on_delete=django.db.models.deletion.SET_NULL, to='baseinfo.Empl', verbose_name='责任人'),
        ),
    ]
