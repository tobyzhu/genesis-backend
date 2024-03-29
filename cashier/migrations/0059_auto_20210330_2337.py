# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-30 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0058_expense_depositeflag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='newcardtype',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='expense',
            name='oldcardtype',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='expvstoll',
            name='cardtype',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='expvstoll',
            name='normalflag',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='expvstoll',
            name='oldcustflag',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='expvstoll',
            name='vipcode',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
