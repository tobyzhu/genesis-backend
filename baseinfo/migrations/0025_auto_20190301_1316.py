# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-03-01 05:16
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0024_auto_20190301_1056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardtype',
            name='cardprice2',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='cardprice3',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='cardprice4',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='checkdate',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='isic',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='photofile',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='salesflag',
        ),
        migrations.RemoveField(
            model_name='cardtype',
            name='salethrperc',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='goodsprice2',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='goodsprice3',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='goodsprice4',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='saleperc',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='saleprccurrency',
        ),
        migrations.AddField(
            model_name='cardtype',
            name='achivementcost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='业绩固定成本扣除'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='after_sales_scheme',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='售后服务方案'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='discountclass',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='displayclass1',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='intervalday',
            field=models.IntegerField(blank=True, default=7, null=True, verbose_name='建议间隔天数'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='价格'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='price2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第二价格'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='price3',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第三价格'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='price4',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第四价格'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='pricechangeable',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', max_length=8, null=True, verbose_name='可否修改价格'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='pricecurrency',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='币别'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='quickycode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='助记码'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='saleflag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', max_length=8, null=True, verbose_name='可否销售'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='secbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师提成基数'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器'), ('040', '销售'), ('100', '拓客项目'), ('110', '留客项目'), ('120', '升客项目'), ('130', '挖客项目')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='thrbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师2提成基数'),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='valiflag',
            field=models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', max_length=8, null=True, verbose_name='是否有效'),
        ),
        migrations.AddField(
            model_name='goods',
            name='achivementcost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='业绩固定成本扣除'),
        ),
        migrations.AddField(
            model_name='goods',
            name='after_sales_scheme',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='售后服务方案'),
        ),
        migrations.AddField(
            model_name='goods',
            name='discountclass',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='折扣分类'),
        ),
        migrations.AddField(
            model_name='goods',
            name='displayclass1',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='显示分类1'),
        ),
        migrations.AddField(
            model_name='goods',
            name='financeclass1',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], max_length=16, null=True, verbose_name='项目财务分类1'),
        ),
        migrations.AddField(
            model_name='goods',
            name='financeclass2',
            field=models.CharField(blank=True, choices=[('10', '正常'), ('20', '其他')], max_length=16, null=True, verbose_name='项目财务分类2'),
        ),
        migrations.AddField(
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('10', '拓客项目'), ('20', '留客项目'), ('30', '升客项目'), ('40', '挖客项目'), ('50', '深挖项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AddField(
            model_name='goods',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('10', '基础项目'), ('20', '大项目'), ('30', '循环类项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类2'),
        ),
        migrations.AddField(
            model_name='goods',
            name='marketclass3',
            field=models.CharField(blank=True, choices=[('10', '无差别类项目'), ('20', '必备类项目'), ('30', '一维类项目'), ('40', '魅力类项目'), ('90', '其他')], max_length=16, null=True, verbose_name='项目营销分类3'),
        ),
        migrations.AddField(
            model_name='goods',
            name='pmperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问提成率'),
        ),
        migrations.AddField(
            model_name='goods',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='价格'),
        ),
        migrations.AddField(
            model_name='goods',
            name='price2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第二价格'),
        ),
        migrations.AddField(
            model_name='goods',
            name='price3',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第三价格'),
        ),
        migrations.AddField(
            model_name='goods',
            name='price4',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True, verbose_name='第四价格'),
        ),
        migrations.AddField(
            model_name='goods',
            name='pricecurrency',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='币别'),
        ),
        migrations.AddField(
            model_name='goods',
            name='quickycode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='助记码'),
        ),
        migrations.AddField(
            model_name='goods',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器'), ('040', '销售'), ('100', '拓客项目'), ('110', '留客项目'), ('120', '升客项目'), ('130', '挖客项目')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='item',
            name='quickycode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='助记码'),
        ),
        migrations.AddField(
            model_name='serviece',
            name='quickycode',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='助记码'),
        ),
        migrations.AlterField(
            model_name='appoption',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='basenum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='顾问提成基数'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='pmguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='pmperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问提成率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='pmpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='顾问提成'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='rptcode1',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='rptcode2',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='rptcode3',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='secguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='secperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1提成率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='secpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师1提成'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='srvrptypecode',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='报表分类'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='thrguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='thrperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2提成率'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='thrpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师2提成'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='ttype',
            field=models.CharField(blank=True, choices=[('G', '商品'), ('S', '服务'), ('C', '售卡'), ('I', '充值')], max_length=16, null=True, verbose_name='商品/服务'),
        ),
        migrations.AlterField(
            model_name='cardvsdi',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='enactmen',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='basenum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='顾问提成基数'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='brand',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='pmguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='顾问营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='pmpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='顾问提成'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='secbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师提成基数'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='secguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='secperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师1提成率'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='secpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师1提成'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='thrbasenum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True, verbose_name='美容师2提成基数'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='thrguideperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2营业额拆分率'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='thrperc',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=5, null=True, verbose_name='美疗师2提成率'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='thrpoint',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True, verbose_name='美疗师2提成'),
        ),
        migrations.AlterField(
            model_name='goodsct',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodsprice',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='item',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='objectvalue2',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='paymode',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='position',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotions',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsgroup',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsgroupdetail',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='servieceprice',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvrptype',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvtopty',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='team',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='useright',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vip',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='wharehouse',
            name='company',
            field=models.CharField(blank=True, choices=[('01', '新红妆'), ('02', '居明居')], default='youlan2', max_length=8, null=True, verbose_name='公司'),
        ),
    ]
