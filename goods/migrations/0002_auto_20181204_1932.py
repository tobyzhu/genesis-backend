# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-04 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodstranslog',
            name='company',
        ),
        migrations.RemoveField(
            model_name='goodstranslog',
            name='create_time',
        ),
        migrations.RemoveField(
            model_name='goodstranslog',
            name='creater',
        ),
        migrations.RemoveField(
            model_name='goodstranslog',
            name='flag',
        ),
        migrations.RemoveField(
            model_name='goodstranslog',
            name='last_modified',
        ),
        migrations.RemoveField(
            model_name='goodstranslog',
            name='uuid',
        ),
        migrations.AddField(
            model_name='goodstranslog',
            name='gtranukid',
            field=models.BigAutoField( primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
