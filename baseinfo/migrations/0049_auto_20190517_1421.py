# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-17 06:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0048_auto_20190515_0801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotionsdetail',
            name='promotionsid',
        ),
        migrations.AddField(
            model_name='promotionsdetail',
            name='promotionsuuid',
            field=models.ForeignKey(blank=True, db_column='promotionsuuid', null=True, on_delete=django.db.models.deletion.SET_NULL, to='baseinfo.Promotions'),
        ),
        migrations.AlterField(
            model_name='appoption',
            name='seg',
            field=models.CharField(choices=[('brand', '品牌'), ('tags', '标签'), ('displayclass1', '显示分类'), ('bodyparts1', '身体部位'), ('marketclass4', '项目分类4')], max_length=40, verbose_name='类别'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('全身', '全身'), ('面部', '面部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('手工', '手工'), ('泡澡', '泡澡'), ('仪器', '仪器')], default='', max_length=128, null=True, verbose_name='项目营销分类4'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('全身', '全身'), ('面部', '面部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('手工', '手工'), ('泡澡', '泡澡'), ('仪器', '仪器')], default='', max_length=128, null=True, verbose_name='项目营销分类4'),
        ),
        migrations.AlterField(
            model_name='item',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('全身', '全身'), ('面部', '面部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('手工', '手工'), ('泡澡', '泡澡'), ('仪器', '仪器')], default='', max_length=128, null=True, verbose_name='项目营销分类4'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('全身', '全身'), ('面部', '面部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('手工', '手工'), ('泡澡', '泡澡'), ('仪器', '仪器')], default='', max_length=128, null=True, verbose_name='项目营销分类4'),
        ),
    ]
