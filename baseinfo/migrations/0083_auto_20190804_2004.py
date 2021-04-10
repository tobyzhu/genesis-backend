# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-04 20:04
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0082_auto_20190803_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardsupertype',
            name='pcode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='financeclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='financeclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='position',
            field=models.CharField(blank=True, db_column='POSITION', max_length=20, null=True, verbose_name='职位'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='所属门店'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='team',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='业务组别'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='financeclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='financeclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='goodsct',
            field=models.CharField(blank=True, db_column='goodsct', max_length=16, null=True, verbose_name='商品折扣分类'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=128, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='financeclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='financeclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='sgcode',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='financeclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='financeclass2',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
    ]
