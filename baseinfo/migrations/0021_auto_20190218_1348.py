# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-18 05:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0020_auto_20190218_1339'),
    ]

    operations = [
        # migrations.RenameField(
        #     model_name='item',
        #     old_name='salesflag',
        #     new_name='saleflag',
        # ),
        migrations.RenameField(
            model_name='serviece',
            old_name='salesflag',
            new_name='saleflag',
        ),
    ]
