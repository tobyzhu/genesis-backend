# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-06-02 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_auto_20190514_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmcase',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='crmcasedetail',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipcasedetail',
            name='company',
            field=models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]
