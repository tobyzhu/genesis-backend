# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-24 06:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0007_auto_20190324_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingevent',
            name='vcode',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='bookingevent',
            name='vname',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
