# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-10 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0026_shoppingcart_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='所属店铺'),
        ),
        migrations.AlterField(
            model_name='room',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='所属店铺'),
        ),
    ]