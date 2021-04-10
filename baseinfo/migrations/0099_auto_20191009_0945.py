# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-09 09:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0098_auto_20191008_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivementruler',
            name='position',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='岗位'),
        ),
        migrations.AlterField(
            model_name='appoption',
            name='seg',
            field=models.CharField(choices=[('viplevel', '会员级别'), ('brand', '品牌'), ('tags', '标签'), ('financeclass1', '财务分类（一）'), ('financeclass2', '财务分类（二）'), ('displayclass1', '显示分类(方法一)'), ('displayclass2', '显示分类(方法二)'), ('bodyparts1', '身体部位'), ('marketclass1', '营销分类(一)'), ('marketclass2', '营销分类(二)'), ('marketclass3', '营销分类(三）'), ('marketclass4', '项目分类4'), ('source', '来店渠道'), ('archivementclass1', '业绩分类（一）')], max_length=40, verbose_name='类别'),
        ),
    ]