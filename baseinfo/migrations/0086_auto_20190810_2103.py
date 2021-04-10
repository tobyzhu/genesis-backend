# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-10 21:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0085_auto_20190810_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='Storeinfo2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storecode', models.CharField(blank=True, db_column='StoreCode', default='0', max_length=16, verbose_name='店铺编号')),
                ('storename', models.CharField(blank=True, db_column='StoreName', max_length=40, null=True, verbose_name='店铺名称')),
                ('dsn', models.CharField(blank=True, db_column='DSN', max_length=20, null=True, verbose_name='DSN')),
                ('database', models.CharField(blank=True, db_column='database', max_length=16, null=True, verbose_name='数据库名称')),
                ('precode', models.CharField(blank=True, db_column='preCode', max_length=8, null=True, verbose_name='卡号前缀')),
                ('areacode', models.CharField(blank=True, max_length=16, null=True, verbose_name='所属地区')),
                ('company', models.CharField(blank=True, max_length=16, null=True, verbose_name='所属公司')),
                ('invoicealter', models.CharField(blank=True, db_column='invoicealter', default='N', max_length=8, null=True, verbose_name='直接打印提示')),
                ('salewhcode', models.CharField(blank=True, db_column='salewhcode', max_length=16, null=True, verbose_name='销售品仓库')),
                ('invoicetitle1', models.CharField(blank=True, max_length=256, null=True, verbose_name='发票抬头')),
                ('invoicetitle2', models.CharField(blank=True, max_length=256, null=True, verbose_name='发票抬头')),
                ('invoicefoot1', models.CharField(blank=True, max_length=256, null=True, verbose_name='发票页脚')),
                ('invoicefoot2', models.CharField(blank=True, max_length=256, null=True, verbose_name='发票页脚')),
                ('usewhcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='使用品仓库')),
                ('hdflag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='N', max_length=8, null=True, verbose_name='是否总部')),
            ],
            options={
                'managed': True,
                'verbose_name': '门店设定',
                'verbose_name_plural': '门店设定',
                'db_table': 'storeinfo2',
            },
        ),
        migrations.AlterUniqueTogether(
            name='storeinfo2',
            unique_together=set([('company', 'storecode')]),
        ),
    ]
