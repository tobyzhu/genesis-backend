# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-04 14:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0046_auto_20210304_1432'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vipitemtranshead',
            old_name='transdat额',
            new_name='transdate',
        ),
    ]
