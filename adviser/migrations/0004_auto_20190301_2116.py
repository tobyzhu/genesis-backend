# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 13:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0003_auto_20190301_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardinfo',
            name='areacode',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='c_note',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='c_prec',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='companyid',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='ecode1',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='ecode2',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='fstopdate',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode1',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode2',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode3',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode4',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode5',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='rptcode6',
        ),
        migrations.RemoveField(
            model_name='cardinfo',
            name='tstopdate',
        ),
        migrations.AlterField(
            model_name='cardinfo',
            name='cardtype',
            field=models.CharField(blank=True, db_column='CARDTYPE', max_length=16, null=True, verbose_name='卡类'),
        ),
    ]
