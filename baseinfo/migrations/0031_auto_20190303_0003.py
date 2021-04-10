# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-02 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0030_auto_20190301_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empl',
            name='photofile',
        ),
        migrations.RemoveField(
            model_name='empl',
            name='positioncode',
        ),
        migrations.RemoveField(
            model_name='empl',
            name='teamid',
        ),
        migrations.AddField(
            model_name='empl',
            name='position',
            field=models.CharField(blank=True, db_column='POSITION', max_length=20, null=True, verbose_name='职位'),
        ),
        migrations.AddField(
            model_name='empl',
            name='team',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='业务组别'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='telcode',
            field=models.CharField(blank=True, db_column='TELCODE', max_length=15, null=True, verbose_name='身份证'),
        ),
    ]