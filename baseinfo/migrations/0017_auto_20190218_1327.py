# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-18 05:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0016_auto_20190218_1323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviece',
            name='basenum',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='pmguideperc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='pmpoint',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='pperc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='pricechangeable',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode1',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode2',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode3',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode4',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode5',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='rptcode6',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='saleachivementtype',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='saleflag',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='scperc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='secbasenum',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='secguideperc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='secpoint',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='svrprice2',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='svrprice3',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='svrprice4',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='thprec',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='thrbasenum',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='thrguideperc',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='thrpoint',
        ),
        migrations.RemoveField(
            model_name='serviece',
            name='valiflag',
        ),
    ]