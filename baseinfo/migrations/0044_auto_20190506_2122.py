# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-06 13:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0043_auto_20190505_2051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardtype',
            name='itemtags',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='itemtags',
        ),
        migrations.RemoveField(
            model_name='item',
            name='itemtags',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='itemtags',
        ),
    ]