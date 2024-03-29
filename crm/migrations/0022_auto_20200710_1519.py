# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-07-10 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0021_auto_20200611_1012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crmsubreport',
            options={'managed': True, 'verbose_name': '客户关系报表分支表', 'verbose_name_plural': '客户关系报表分支表'},
        ),
        migrations.RenameField(
            model_name='crmcase',
            old_name='ecode',
            new_name='empl',
        ),
        migrations.AlterField(
            model_name='crmcase',
            name='casetype',
            field=models.CharField(blank=True, choices=[('20', '到店回访型任务'), ('10', '阶段性任务')], max_length=8, null=True, verbose_name='类型'),
        ),
        migrations.AlterField(
            model_name='crminfoitem',
            name='itemflag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], max_length=8, null=True, verbose_name='标志'),
        ),
        migrations.AlterField(
            model_name='crminfoitem',
            name='requireflag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], max_length=8, null=True, verbose_name='是否必填'),
        ),
        migrations.AlterField(
            model_name='vipcasedetail',
            name='casetype',
            field=models.CharField(blank=True, choices=[('20', '到店回访'), ('10', '阶段性任务')], default='10', max_length=8, null=True, verbose_name='类型'),
        ),
    ]
