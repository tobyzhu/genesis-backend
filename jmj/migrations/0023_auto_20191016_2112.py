# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-16 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jmj', '0022_auto_20190810_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='olddata',
            name='saleatr',
            field=models.CharField(blank=True, choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出'), ('SL', '申领单'), ('CG', '采购单')], default='G', max_length=8, null=True, verbose_name='类型'),
        ),
        migrations.AlterField(
            model_name='olddata2',
            name='saleatr',
            field=models.CharField(blank=True, choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出'), ('SL', '申领单'), ('CG', '采购单')], default='G', max_length=8, null=True, verbose_name='类型'),
        ),
        migrations.AlterField(
            model_name='olddata4',
            name='saleatr',
            field=models.CharField(blank=True, choices=[('G', '销售'), ('I', '进货'), ('O', '出货'), ('F', '退货'), ('U', '领用'), ('C', '盘点'), ('TI', '转入'), ('TO', '转出'), ('SL', '申领单'), ('CG', '采购单')], default='G', max_length=8, null=True, verbose_name='类型'),
        ),
    ]
