# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-21 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0015_auto_20181221_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldData2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storecode', models.CharField(blank=True, choices=[('1', '青岛店'), ('2', '沈阳店'), ('3', '大连店'), ('5', '济南店')], max_length=8, null=True, verbose_name='店铺')),
                ('saleatr', models.CharField(blank=True, choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出')], default='G', max_length=8, null=True, verbose_name='类型')),
                ('vsdate', models.CharField(blank=True, max_length=8, null=True, verbose_name='日期')),
                ('gcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='商品')),
                ('salesqty', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='数量')),
                ('salesamount', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='金额')),
            ],
            options={
                'db_table': 'olddata2',
                'verbose_name_plural': '往年进货数据',
                'verbose_name': '往年进货数据',
                'managed': True,
            },
        ),
    ]