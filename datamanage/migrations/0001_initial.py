# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-22 01:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OldCardTypeItemDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, max_length=16, null=True, verbose_name='公司')),
                ('cardtype', models.CharField(blank=True, db_column='cardtype', max_length=32, null=True, verbose_name='卡类')),
                ('cardname', models.DecimalField(blank=True, decimal_places=0, max_digits=2, null=True, verbose_name='卡类名称')),
                ('codetype', models.CharField(blank=True, db_column='codetype', max_length=8, null=True, verbose_name='编码类型')),
                ('stype', models.CharField(db_column='stype', max_length=16, verbose_name='是否赠送')),
                ('itemcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='项目编号')),
                ('times', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='次数')),
                ('price', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=16, null=True, verbose_name='单次价')),
                ('performance', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=16, null=True, verbose_name='员工业绩')),
                ('linenumber', models.IntegerField(blank=True, default=1, null=True, verbose_name='行次')),
            ],
            options={
                'ordering': ['cardtype'],
                'managed': True,
                'verbose_name': '老卡项目明细',
                'verbose_name_plural': '老卡项目明细',
                'db_table': 'oldcardtypeitemdetail',
            },
        ),
    ]
