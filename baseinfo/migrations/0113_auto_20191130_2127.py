# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-30 21:27
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0112_auto_20191129_2327'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='storeinfo',
        #     name='uuid',
        #     field=models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        # ),
        migrations.AlterField(
            model_name='archivementruler',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='position',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='岗位'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='storecode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='pcode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
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
            model_name='cardtype',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='suptype',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='卡大类'),
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
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
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
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=128, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='item',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
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
            model_name='item',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='sgcode',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
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
        migrations.AlterField(
            model_name='serviece',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='topcode',
            field=models.CharField(blank=True, db_column='TOPCODE', max_length=16, null=True, verbose_name='服务销售折扣分类'),
        ),
    ]
