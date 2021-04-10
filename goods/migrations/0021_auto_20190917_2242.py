# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-17 22:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0020_auto_20190911_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstock',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodstransdetail',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodstranshead',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='owelist',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='saledtl',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='salehead',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='stockdetail',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='stockmst',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='transdtl',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='transhead',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vgtranslog',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]
