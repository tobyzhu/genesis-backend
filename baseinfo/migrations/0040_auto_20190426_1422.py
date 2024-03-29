# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-04-26 06:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0039_auto_20190412_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appoption',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, choices=[('100', '幽兰'), ('110', '安杰玛'), ('120', '舒活特'), ('140', 'BIO'), ('200', '于教授'), ('210', '内衣'), ('300', '净化器'), ('500', '美容品'), ('510', '仪器配件'), ('900', '杂项')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='discountclass',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AlterField(
            model_name='cardvsdi',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='enactmen',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='brand',
            field=models.CharField(blank=True, choices=[('100', '幽兰'), ('110', '安杰玛'), ('120', '舒活特'), ('140', 'BIO'), ('200', '于教授'), ('210', '内衣'), ('300', '净化器'), ('500', '美容品'), ('510', '仪器配件'), ('900', '杂项')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='discountclass',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AlterField(
            model_name='goodsct',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodsprice',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(blank=True, choices=[('100', '幽兰'), ('110', '安杰玛'), ('120', '舒活特'), ('140', 'BIO'), ('200', '于教授'), ('210', '内衣'), ('300', '净化器'), ('500', '美容品'), ('510', '仪器配件'), ('900', '杂项')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='item',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='item',
            name='discountclass',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AlterField(
            model_name='objectvalue2',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='paymode',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='position',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotions',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsgroup',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsgroupdetail',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='brand',
            field=models.CharField(blank=True, choices=[('100', '幽兰'), ('110', '安杰玛'), ('120', '舒活特'), ('140', 'BIO'), ('200', '于教授'), ('210', '内衣'), ('300', '净化器'), ('500', '美容品'), ('510', '仪器配件'), ('900', '杂项')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='discountclass',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], default='', max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], default='', max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AlterField(
            model_name='servieceprice',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvrptype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvtopty',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='team',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='useright',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vip',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='wharehouse',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居'), ('youlan', '杭州幽兰')], default='JMJ', max_length=8, null=True, verbose_name='公司'),
        ),
    ]
