# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-07-28 01:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0078_auto_20190726_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='hdsysuser',
            name='costpriceflag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='N', max_length=8, null=True, verbose_name='是否有查看成本价权限'),
        ),
    ]
