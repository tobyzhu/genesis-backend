# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-14 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_auto_20191130_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vipcasedetail',
            name='casetype',
            field=models.CharField(blank=True, choices=[('10', '初诊'), ('20', '复诊'), ('40', '再消费'), ('30', '复查')], default='10', max_length=8, null=True, verbose_name='类型'),
        ),
    ]
