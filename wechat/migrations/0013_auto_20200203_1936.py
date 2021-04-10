# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-03 19:36
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0012_auto_20191221_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatuser',
            name='companylist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('salon', None), ('yfy', '石家庄雅芳亚'), ('yiren', '北京伊人'), ('JMJ', '居明居')], max_length=19, null=True, verbose_name='可用公司'),
        ),
    ]