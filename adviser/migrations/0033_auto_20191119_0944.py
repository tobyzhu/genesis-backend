# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-19 09:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adviser', '0032_auto_20191118_2256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='payamount',
            new_name='payedamount',
        ),
    ]