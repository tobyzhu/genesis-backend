# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 02:56
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0023_auto_20190226_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=16, null=True, verbose_name='标签')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器'), ('040', '销售'), ('100', '拓客项目'), ('110', '留客项目'), ('120', '升客项目'), ('130', '挖客项目')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='serviece',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器'), ('040', '销售'), ('100', '拓客项目'), ('110', '留客项目'), ('120', '升客项目'), ('130', '挖客项目')], max_length=64, null=True, verbose_name='标签'),
        ),
    ]
