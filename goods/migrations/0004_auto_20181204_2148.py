# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-04 13:48
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20181204_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstranslog',
            name='create_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 12, 4, 13, 47, 57, 201284, tzinfo=utc), null=True),
        ),
    ]
