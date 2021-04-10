# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-16 22:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0119_auto_20191215_0746'),
        ('report', '0015_reportitem_report_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportclassdata',
            name='ecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='员工工号'),
        ),
        migrations.AddField(
            model_name='reportclassdata',
            name='empl',
            field=models.ForeignKey(blank=True, db_column='empluuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Empl', verbose_name='员工'),
        ),
        migrations.AddField(
            model_name='reportclassdata',
            name='report_type',
            field=models.CharField(blank=True, choices=[('empl', '员工'), ('store', '门店'), ('vip', '会员')], max_length=16, null=True, verbose_name='报表类别'),
        ),
        migrations.AddField(
            model_name='reportclassdata',
            name='ttype',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='交易类型'),
        ),
        migrations.AddField(
            model_name='reportclassdata',
            name='vcode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='会员号'),
        ),
        migrations.AddField(
            model_name='reportclassdata',
            name='vip',
            field=models.ForeignKey(blank=True, db_column='vipuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Vip', verbose_name='客户'),
        ),
        migrations.AlterField(
            model_name='reportclassdata',
            name='datarang',
            field=models.CharField(blank=True, choices=[('daily', '日'), ('month', '月'), ('year', '年'), ('period', '期间')], max_length=16, null=True, verbose_name='数据日期范围'),
        ),
    ]