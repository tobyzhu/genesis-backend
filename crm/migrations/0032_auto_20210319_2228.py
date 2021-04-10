# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-19 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0031_auto_20210319_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmcase',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='crmcase',
            name='ecodelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('44100002', '超级管理员'), ('32100003', '王红阳'), ('31310002', '孙丽荣'), ('32100004', '郭浩'), ('42100001', '荀玉洁'), ('32100005', '史晓蓉'), ('42100002', '赵霞'), ('33120005', '张晗'), ('44100001', '商佳男'), ('32100002', '冯立英'), ('41100001', '蒋丽芳'), ('32100001', '陈晓菲'), ('42100001', '荀玉洁'), ('33120002', '李婷婷'), ('41130001', '齐红丽'), ('43100001', '杨芳'), ('33120004', '张琳')], max_length=152, null=True, verbose_name='责任员工'),
        ),
        migrations.AlterField(
            model_name='crmcasedetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='crminfoitem',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='crminfoitemchoice',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='crmsubreport',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipcasedetail',
            name='casetype',
            field=models.CharField(blank=True, default='10', max_length=8, null=True, verbose_name='类型'),
        ),
        migrations.AlterField(
            model_name='vipcasedetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]
