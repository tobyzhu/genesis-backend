# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-04-26 06:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0041_auto_20190426_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='achivementcost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='业绩固定成本扣除'),
        ),
        migrations.AddField(
            model_name='goods',
            name='basenum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='顾问提成基数'),
        ),
        migrations.AddField(
            model_name='goods',
            name='pmguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问营业额拆分率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='pmperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问提成率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='pmpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='顾问提成'),
        ),
        migrations.AddField(
            model_name='goods',
            name='secbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师提成基数'),
        ),
        migrations.AddField(
            model_name='goods',
            name='secguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1营业额拆分率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='secperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1提成率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='secpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师1提成'),
        ),
        migrations.AddField(
            model_name='goods',
            name='thrbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师2提成基数'),
        ),
        migrations.AddField(
            model_name='goods',
            name='thrguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2营业额拆分率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='thrperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2提成率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='thrpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师2提成'),
        ),
    ]
