# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-07 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0036_auto_20191221_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='depositeflag',
            field=models.CharField(blank=True, db_column='depositeflag', default='N', max_length=8, null=True, verbose_name='是否存院'),
        ),
    ]
