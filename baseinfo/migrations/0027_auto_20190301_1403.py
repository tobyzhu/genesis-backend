# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 06:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0026_auto_20190301_1359'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cardtype',
            old_name='quickycode',
            new_name='mnemoniccode',
        ),
        migrations.RenameField(
            model_name='goods',
            old_name='quickycode',
            new_name='mnemoniccode',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='quickycode',
            new_name='mnemoniccode',
        ),
        migrations.RenameField(
            model_name='serviece',
            old_name='quickycode',
            new_name='mnemoniccode',
        ),
    ]