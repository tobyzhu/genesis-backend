# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-08 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0067_auto_20210306_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstock',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodstransdetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodstransdetail',
            name='gcode',
            field=models.CharField(blank=True, choices=[('110101001', '原液-清爽平衡洁面乳150ml'), ('110901002', '元馔-胎盘粉底液30ml'), ('112202005', 'Huanyangdanbai 30ml')], db_column='gcode', max_length=16, null=True, verbose_name='商品'),
        ),
        migrations.AlterField(
            model_name='goodstranshead',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodstransprocess',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='owelist',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='owereturndetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='saledtl',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='salehead',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviecegoods',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='stockdetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='stockmst',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='transdtl',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='transhead',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vgtranslog',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]
