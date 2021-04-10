# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-09 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0030_auto_20190917_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardblacklist',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardinfo',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='emplschedule',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='expensehung',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='expvstollhung',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='room',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipinfogroup1',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]