# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-05 14:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0005_auto_20181205_2201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saledtl',
            name='id',
        ),
        migrations.AddField(
            model_name='saledtl',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='02', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AddField(
            model_name='saledtl',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='建立时间'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='saledtl',
            name='creater',
            field=models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='saledtl',
            name='flag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除'),
        ),
        migrations.AddField(
            model_name='saledtl',
            name='last_modified',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间'),
        ),
        migrations.AddField(
            model_name='saledtl',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AddField(
            model_name='saledtl',
            name='uuid',
            field=models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
