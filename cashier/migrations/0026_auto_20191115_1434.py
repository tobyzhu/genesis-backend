# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-15 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0031_auto_20191009_1239'),
        ('baseinfo', '0109_auto_20191115_1434'),
        ('cashier', '0025_auto_20191111_2326'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarnestMoeny',
            fields=[
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('uuid', models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司')),
                ('storecode', models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店')),
                ('vcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='会员号')),
                ('ttype', models.CharField(blank=True, max_length=8, null=True, verbose_name='类型')),
                ('itemcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='项目编号')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='单价')),
                ('planqty', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='计划购买数量')),
                ('planamount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='计划支付金额')),
                ('payedamount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='已付金额')),
                ('oweamount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=2, max_length=16, null=True, verbose_name='欠款金额')),
                ('payedqty', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='已付金额折合数量')),
                ('payedleftmeony', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='已经金额折合卡余额')),
                ('oweqty', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=2, max_length=16, null=True, verbose_name='欠款数量')),
                ('oweleftmoeny', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, max_length=16, null=True, verbose_name='欠款金额折合卡余额')),
                ('ecode', models.CharField(blank=True, max_length=16, null=True, verbose_name='负责员工')),
                ('status', models.CharField(blank=True, choices=[('10', '定金开单')], max_length=8, null=True, verbose_name='当前状态')),
                ('remark', models.CharField(blank=True, max_length=128, null=True, verbose_name='备注')),
                ('hungsuuid', models.ForeignKey(blank=True, db_column='hungsuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='adviser.ExpvstollHung', verbose_name='开单记录')),
                ('transuuid', models.ForeignKey(blank=True, db_column='transuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='cashier.Expvstoll', verbose_name='交易记录')),
                ('vipuuid', models.ForeignKey(blank=True, db_column='vipuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Vip', verbose_name='客人')),
            ],
            options={
                'verbose_name': '客户定金清单',
                'verbose_name_plural': '客户定金清单',
                'managed': True,
                'db_table': 'earnestmoeny',
            },
        ),
        migrations.RemoveField(
            model_name='earnestmoenylist',
            name='vipuuid',
        ),
        migrations.DeleteModel(
            name='EarnestMoenyList',
        ),
    ]
