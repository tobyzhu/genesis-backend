# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-18 02:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0014_auto_20190218_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='pmguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问营业额拆分率'),
        ),
        migrations.AddField(
            model_name='item',
            name='pmperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问提成率'),
        ),
        migrations.AddField(
            model_name='item',
            name='pmpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='顾问提成'),
        ),
        migrations.AddField(
            model_name='item',
            name='secguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1营业额拆分率'),
        ),
        migrations.AddField(
            model_name='item',
            name='secperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1提成率'),
        ),
        migrations.AddField(
            model_name='item',
            name='secpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师1提成'),
        ),
        migrations.AddField(
            model_name='item',
            name='thrguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2营业额拆分率'),
        ),
        migrations.AddField(
            model_name='item',
            name='thrperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2提成率'),
        ),
        migrations.AddField(
            model_name='item',
            name='thrpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师2提成'),
        ),
    ]
