# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-16 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0037_shoppingcart_depositeflag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='depositeflag',
            field=models.CharField(blank=True, default='N', max_length=8, null=True, verbose_name='是否存院'),
        ),
    ]
