# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-09 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0099_auto_20191009_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivementruler',
            name='position',
            field=models.CharField(blank=True, choices=[('100', '面部护理师'), ('110', '身体护理师'), ('200', '准店长'), ('210', '店长'), ('300', '库管'), ('310', '管理培训生'), ('320', '保洁'), ('400', '其他'), ('500', '发型师')], max_length=16, null=True, verbose_name='岗位'),
        ),
    ]
