# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-02 22:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0003_remove_cardtype_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, choices=[('10', '法尔曼'), ('20', 'NB'), ('30', '思蒂'), ('40', '其他')], db_column='brand', max_length=16, null=True, verbose_name='品牌'),
        ),
    ]
