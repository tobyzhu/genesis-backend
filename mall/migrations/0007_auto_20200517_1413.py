# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-17 14:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mall', '0006_banner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='banner',
            old_name='pages',
            new_name='apppage',
        ),
    ]
