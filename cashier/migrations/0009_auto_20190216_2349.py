# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-16 15:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0008_auto_20190216_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='transuuid',
            field=models.ForeignKey(blank=True, db_column='transuuid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cashier.Expvstoll'),
        ),
        migrations.AddField(
            model_name='toll',
            name='transuuid',
            field=models.ForeignKey(blank=True, db_column='transuuid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cashier.Expvstoll'),
        ),
    ]