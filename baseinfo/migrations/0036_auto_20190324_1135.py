# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-24 03:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0035_auto_20190324_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='VipTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=16, null=True, verbose_name='标签')),
            ],
        ),
        migrations.AddField(
            model_name='vip',
            name='occupation',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='职业'),
        ),
        migrations.AlterField(
            model_name='vip',
            name='source',
            field=models.CharField(blank=True, choices=[('自然客流', '自然客流'), ('熟客推荐', '熟客推荐'), ('网络', '网络'), ('合作单位', '合作单位')], max_length=32, null=True, verbose_name='来店渠道'),
        ),
    ]