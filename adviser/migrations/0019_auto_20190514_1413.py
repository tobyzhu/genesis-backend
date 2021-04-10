# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-14 06:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0018_auto_20190426_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardblacklist',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardblacklist',
            name='storecode',
            field=models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='cardinfo',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='emplschedule',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='emplschedule',
            name='storecode',
            field=models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='expensehung',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='expensehung',
            name='storecode',
            field=models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='expvstollhung',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='expvstollhung',
            name='storecode',
            field=models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='room',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipinfogroup1',
            name='company',
            field=models.CharField(blank=True, default='youlan', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]