# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-14 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0014_auto_20190514_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstock',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='goodstransdetail',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='goodstranshead',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='owelist',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='saledtl',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='salehead',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='stockdetail',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='stockmst',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='transdtl',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='transhead',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='vgtranslog',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者'),
        ),
    ]