# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-16 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0004_remove_perioddata_goodsuuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='olddata',
            name='saleatr',
            field=models.CharField(blank=True, choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出')], default='G', max_length=8, null=True, verbose_name='类型'),
        ),
    ]
