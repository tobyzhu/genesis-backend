# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-17 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0052_promotionsgroupdetail_pgroupuuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotions',
            name='mainttype',
            field=models.CharField(blank=True, choices=[('10', '特价活动'), ('20', '特殊折扣活动'), ('30', '组合销售活动')], max_length=8, null=True, verbose_name='活动大类'),
        ),
    ]