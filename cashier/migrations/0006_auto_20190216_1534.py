# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-16 07:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0012_auto_20190216_1534'),
        ('cashier', '0005_auto_20181204_2148'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='EmplDailyData',
        #     fields=[
        #         ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
        #         ('uuid', models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        #         ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
        #         ('creater', models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者')),
        #         ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
        #         ('company', models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='02', max_length=8, null=True, verbose_name='公司')),
        #         ('storecode', models.CharField(blank=True, max_length=16, null=True, verbose_name='门店')),
        #         ('vsdate', models.DateField(blank=True, null=True, verbose_name='日期')),
        #         ('vipcount', models.IntegerField(blank=True, default=0, null=True, verbose_name='客人数')),
        #         ('newvipcount', models.IntegerField(blank=True, default=0, null=True, verbose_name='新客人数')),
        #         ('vip10count', models.IntegerField(blank=True, default=0, null=True, verbose_name='会员数')),
        #         ('vip20count', models.IntegerField(blank=True, default=0, null=True, verbose_name='散客数')),
        #         ('vipscount', models.IntegerField(blank=True, default=0, null=True, verbose_name='服务客人数')),
        #         ('vipgcount', models.IntegerField(blank=True, default=0, null=True, verbose_name='销售商品会员数')),
        #         ('vipccount', models.IntegerField(blank=True, default=0, null=True, verbose_name='售卡会员数')),
        #         ('archivementtype', models.CharField(blank=True, choices=[('100', '正常服务'), ('130', '正常销售'), ('110', '正常储值卡'), ('120', '正常疗程卡'), ('1DX', '大项'), ('10PS', '赠送服务'), ('10PG', '赠送销售'), ('10PC', '赠送卡')], max_length=8, null=True, verbose_name='数据类型')),
        #         ('qty', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='数量')),
        #         ('ticheng', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='百分比提成')),
        #         ('guideamount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='服务业绩')),
        #         ('point', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='固定提成')),
        #         ('empl', models.ForeignKey(blank=True, db_column='empluuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Empl', verbose_name='员工')),
        #     ],
        #     options={
        #         'managed': True,
        #         'verbose_name_plural': '员工每日业绩',
        #         'db_table': 'empldailidata',
        #         'verbose_name': '员工每日业绩',
        #     },
        # ),
        # migrations.AlterField(
        #     model_name='expense',
        #     name='transuuid',
        #     field=models.ForeignKey(blank=True, db_column='transuuid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cashier.Expvstoll'),
        # ),
        # migrations.AlterField(
        #     model_name='toll',
        #     name='transuuid',
        #     field=models.ForeignKey(blank=True, db_column='transuuid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cashier.Expvstoll'),
        # ),
    ]
