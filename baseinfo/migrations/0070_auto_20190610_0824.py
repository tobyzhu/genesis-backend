# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-06-10 00:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0069_auto_20190607_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardtype',
            name='presentpoint',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='赠送美疗师提成'),
        ),
        migrations.AddField(
            model_name='goods',
            name='presentpoint',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='赠送美疗师提成'),
        ),
        migrations.AddField(
            model_name='item',
            name='presentpoint',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='赠送美疗师提成'),
        ),
        migrations.AddField(
            model_name='serviece',
            name='presentpoint',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='赠送美疗师提成'),
        ),
        migrations.AlterField(
            model_name='appoption',
            name='seg',
            field=models.CharField(choices=[('brand', '品牌'), ('tags', '标签'), ('financeclass1', '财务分类（一）'), ('financeclass2', '财务分类（二）'), ('displayclass1', '显示分类(方法一)'), ('displayclass2', '显示分类(方法二)'), ('bodyparts1', '身体部位'), ('marketclass4', '项目分类4'), ('source', '来店渠道')], max_length=40, verbose_name='类别'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='storecode',
            field=models.CharField(blank=True, choices=[('00', '总部'), ('01', '丽迪亚店'), ('02', '军创店'), ('03', '国际城店'), ('04', '天蕴店'), ('05', '信诚店'), ('88', '练习')], max_length=16, null=True, verbose_name='所属门店'),
        ),
    ]
