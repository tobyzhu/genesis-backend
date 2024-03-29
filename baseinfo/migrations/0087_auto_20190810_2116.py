# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-10 21:16
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0086_auto_20190810_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empl',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='所属门店'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=128, null=True, verbose_name='可用门店'),
        ),
    ]
