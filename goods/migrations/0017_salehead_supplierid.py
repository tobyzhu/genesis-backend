# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-06-14 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0016_auto_20190602_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='salehead',
            name='supplierid',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
