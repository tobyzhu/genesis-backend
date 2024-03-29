# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-26 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mall', '0008_banner_orderno'),
    ]

    operations = [
        migrations.CreateModel(
            name='onlineItemImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, default='yiren', max_length=8, null=True, verbose_name='公司')),
                ('imagetype', models.CharField(blank=True, choices=[('small', '小图'), ('large', '大图'), ('detail', '详图')], max_length=16, null=True, verbose_name='图片类型')),
                ('image_url', models.ImageField(blank=True, null=True, upload_to='static/images', verbose_name='展示图片')),
                ('orderno', models.IntegerField(blank=True, default=100, null=True, verbose_name='序号')),
                ('onlineshowitem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mall.onlineShowItem', verbose_name='线上项目')),
            ],
            options={
                'verbose_name': '线上项目图片',
                'managed': True,
                'verbose_name_plural': '线上项目图片',
                'db_table': 'onlineitemimage',
            },
        ),
    ]
