# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-02 14:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('baseinfo', '0131_goods_large_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='onlineShowItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, max_length=8, null=True, verbose_name='公司')),
                ('itemdesc', models.CharField(blank=True, max_length=128, null=True, verbose_name='项目描述')),
                ('small_showimage', models.ImageField(blank=True, null=True, upload_to='static/images', verbose_name='小展示图片')),
                ('large_showimage', models.ImageField(blank=True, null=True, upload_to='static/images', verbose_name='大展示图片')),
                ('onlineprice', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='线上价格')),
                ('goods', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Goods', verbose_name='商品')),
            ],
            options={
                'db_table': 'onlineshowitem',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='onlineShowType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, max_length=8, null=True, verbose_name='公司')),
                ('ttype', models.CharField(blank=True, max_length=16, null=True, verbose_name='分类')),
                ('showname', models.CharField(blank=True, max_length=32, null=True, verbose_name='名称')),
                ('showimage', models.ImageField(blank=True, null=True, upload_to='static/images', verbose_name='展示图片')),
                ('showurl', models.URLField(blank=True, null=True, verbose_name='链接')),
                ('orderno', models.IntegerField(blank=True, default=100, null=True, verbose_name='序号')),
            ],
            options={
                'db_table': 'onlineshowtype',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='onlineshowitem',
            name='onlineShowType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mall.onlineShowType', verbose_name='在线显示分类'),
        ),
        migrations.AddField(
            model_name='onlineshowitem',
            name='serviece',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Serviece', verbose_name='服务项目'),
        ),
    ]