# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-02 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cardpayout',
            fields=[
                ('payout_ukid', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('cardownareacode', models.CharField(max_length=8)),
                ('cardowncompany', models.CharField(blank=True, max_length=16, null=True)),
                ('cardownstore', models.CharField(max_length=16)),
                ('cardexpcompany', models.CharField(blank=True, max_length=8, null=True)),
                ('cardexpstore', models.CharField(max_length=16)),
                ('cardno', models.CharField(max_length=40)),
                ('exptxserno', models.CharField(max_length=40)),
                ('cardtype', models.CharField(blank=True, max_length=8, null=True)),
                ('moneytype', models.CharField(max_length=8)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('vdate', models.CharField(blank=True, max_length=8, null=True)),
                ('vtime', models.CharField(blank=True, max_length=8, null=True)),
                ('vcode', models.CharField(blank=True, max_length=16, null=True)),
                ('vname', models.CharField(blank=True, max_length=32, null=True)),
                ('pcode', models.CharField(blank=True, max_length=16, null=True)),
                ('pname', models.CharField(blank=True, max_length=32, null=True)),
                ('casher', models.CharField(blank=True, max_length=16, null=True)),
                ('cashername', models.CharField(blank=True, max_length=32, null=True)),
                ('vflag', models.CharField(blank=True, max_length=1, null=True)),
                ('note', models.CharField(blank=True, max_length=100, null=True)),
                ('ttype', models.CharField(blank=True, max_length=8, null=True)),
                ('srvcode', models.CharField(blank=True, max_length=40, null=True)),
                ('srvname', models.CharField(blank=True, max_length=64, null=True)),
                ('leftmoney', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('rfmac', models.CharField(blank=True, max_length=16, null=True)),
                ('sector', models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True)),
            ],
            options={
                'db_table': 'cardpayout',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cpayatout',
            fields=[
                ('ukid', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('cardownstore', models.CharField(max_length=10)),
                ('cardexpstore', models.CharField(max_length=10)),
                ('cardno', models.CharField(max_length=40)),
                ('exptxserno', models.CharField(max_length=40)),
                ('cardtype', models.CharField(blank=True, max_length=10, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True)),
                ('vdate', models.CharField(blank=True, max_length=8, null=True)),
                ('vtime', models.CharField(blank=True, max_length=8, null=True)),
                ('vcode', models.CharField(blank=True, max_length=40, null=True)),
                ('vname', models.CharField(blank=True, max_length=40, null=True)),
                ('pcode', models.CharField(blank=True, max_length=10, null=True)),
                ('pname', models.CharField(blank=True, max_length=10, null=True)),
                ('casher', models.CharField(blank=True, max_length=10, null=True)),
                ('cashername', models.CharField(blank=True, max_length=10, null=True)),
                ('vflag', models.CharField(blank=True, max_length=1, null=True)),
                ('note', models.CharField(blank=True, max_length=100, null=True)),
                ('updateflag', models.CharField(blank=True, max_length=1, null=True)),
                ('ttype', models.CharField(blank=True, max_length=8, null=True)),
                ('srvcode', models.CharField(blank=True, max_length=40, null=True)),
                ('srvname', models.CharField(blank=True, max_length=64, null=True)),
                ('leftmoney', models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True)),
                ('rfmac', models.CharField(blank=True, max_length=16, null=True)),
                ('sector', models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True)),
            ],
            options={
                'db_table': 'cpayatout',
                'managed': True,
            },
        ),
    ]