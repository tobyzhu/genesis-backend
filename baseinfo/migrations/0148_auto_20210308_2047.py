# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-03-08 20:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import multiselectfield.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0147_auto_20210307_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('uuid', models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司')),
                ('accountcode', models.CharField(blank=True, max_length=16, null=True, verbose_name='编号')),
                ('accountname', models.CharField(blank=True, max_length=128, null=True, verbose_name='账号名称')),
                ('bankname', models.CharField(blank=True, max_length=128, null=True, verbose_name='开户银行')),
                ('accountnumber', models.CharField(blank=True, max_length=128, null=True, verbose_name='银行账号')),
                ('accountdesc', models.CharField(blank=True, max_length=128, null=True, verbose_name='描述')),
                ('status', models.CharField(blank=True, max_length=128, null=True, verbose_name='状态')),
                ('storelist', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店')),
            ],
            options={
                'verbose_name': '账户设定',
                'db_table': 'bankaccount',
                'verbose_name_plural': '账户设定',
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='appoption',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='position',
            field=models.CharField(blank=True, choices=[('311', '运营总监'), ('312', '培训师'), ('313', '店长'), ('314', '顾问'), ('321', '操作师'), ('331', '前台运营'), ('341', '保洁'), ('4111', '物流调拔'), ('4112', '物流库'), ('413', '采购'), ('421', '财务'), ('431', '人力资源'), ('441', '后台运营')], max_length=16, null=True, verbose_name='岗位'),
        ),
        migrations.AlterField(
            model_name='archivementruler',
            name='storecode',
            field=models.CharField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=16, null=True, verbose_name='门店'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='normal_pcode',
            field=models.CharField(blank=True, choices=[('A', '店微信'), ('B', '现金'), ('C1', '银行卡'), ('C2', '银行卡'), ('C3', '银行卡'), ('C4', '银行卡'), ('D1', '支票'), ('D2', '支票'), ('D3', '支票'), ('D4', '支票'), ('E', '卡付'), ('F', '疗程卡付'), ('G', '管理卡赠送'), ('H', '免单'), ('I', '储值积分卡赠送'), ('J', '活动积分卡赠送')], max_length=16, null=True, verbose_name='正常对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='pcode',
            field=models.CharField(blank=True, choices=[('A', '店微信'), ('B', '现金'), ('C1', '银行卡'), ('C2', '银行卡'), ('C3', '银行卡'), ('C4', '银行卡'), ('D1', '支票'), ('D2', '支票'), ('D3', '支票'), ('D4', '支票'), ('E', '卡付'), ('F', '疗程卡付'), ('G', '管理卡赠送'), ('H', '免单'), ('I', '储值积分卡赠送'), ('J', '活动积分卡赠送')], max_length=16, null=True, verbose_name='默认付款方式'),
        ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='present_pcode',
            field=models.CharField(blank=True, choices=[('A', '店微信'), ('B', '现金'), ('C1', '银行卡'), ('C2', '银行卡'), ('C3', '银行卡'), ('C4', '银行卡'), ('D1', '支票'), ('D2', '支票'), ('D3', '支票'), ('D4', '支票'), ('E', '卡付'), ('F', '疗程卡付'), ('G', '管理卡赠送'), ('H', '免单'), ('I', '储值积分卡赠送'), ('J', '活动积分卡赠送')], max_length=16, null=True, verbose_name='赠送对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, choices=[('001', '元馔'), ('003', '原液之谜'), ('002', '养生')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('006', '6'), ('003', '3'), ('001', '1'), ('004', '4'), ('002', '2'), ('005', '5')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, default='', max_length=128, null=True, verbose_name='项目营销分类（方法四）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='suptype',
            field=models.CharField(blank=True, choices=[('20', '疗程卡'), ('22', '家居'), ('10', '储值卡'), ('30', '赠送储值'), ('26', '即时')], max_length=8, null=True, verbose_name='卡大类'),
        ),
        migrations.AlterField(
            model_name='cardtypevsdiscountclass',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='cardvsdi',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='position',
            field=models.CharField(blank=True, choices=[('311', '运营总监'), ('312', '培训师'), ('313', '店长'), ('314', '顾问'), ('321', '操作师'), ('331', '前台运营'), ('341', '保洁'), ('4111', '物流调拔'), ('4112', '物流库'), ('413', '采购'), ('421', '财务'), ('431', '人力资源'), ('441', '后台运营')], db_column='POSITION', max_length=20, null=True, verbose_name='职位'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='storecode',
            field=models.CharField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=16, null=True, verbose_name='所属门店'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='team',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='业务组别'),
        ),
        migrations.AlterField(
            model_name='enactmen',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='brand',
            field=models.CharField(blank=True, choices=[('001', '元馔'), ('003', '原液之谜'), ('002', '养生')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('006', '6'), ('003', '3'), ('001', '1'), ('004', '4'), ('002', '2'), ('005', '5')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            field=models.CharField(blank=True, choices=[('01', '测试')], db_column='goodsct', max_length=16, null=True, verbose_name='商品折扣分类'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, default='', max_length=128, null=True, verbose_name='项目营销分类（方法四）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='goodsct',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='goodsprice',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=128, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='item',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(blank=True, choices=[('001', '元馔'), ('003', '原液之谜'), ('002', '养生')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='item',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('006', '6'), ('003', '3'), ('001', '1'), ('004', '4'), ('002', '2'), ('005', '5')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            model_name='item',
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, default='', max_length=128, null=True, verbose_name='项目营销分类（方法四）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='itemtype',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='objectvalue2',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='paymode',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='position',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotions',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='sgcode',
            field=models.CharField(blank=True, choices=[('2000000', '即时护肤全套'), ('2000001', '即时身体全套'), ('21010111', '即时护肤全套')], max_length=24, null=True),
        ),
        migrations.AlterField(
            model_name='promotionsgroup',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='promotionsgroupdetail',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='archivementclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='业绩分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='brand',
            field=models.CharField(blank=True, choices=[('001', '元馔'), ('003', '原液之谜'), ('002', '养生')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('006', '6'), ('003', '3'), ('001', '1'), ('004', '4'), ('002', '2'), ('005', '5')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('010', '面部'), ('020', '身体'), ('030', '仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            name='marketclass4',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, default='', max_length=128, null=True, verbose_name='项目营销分类（方法四）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('88', '练习')], max_length=5, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='servieceprice',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvrptype',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='srvtopty',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='team',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='useright',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vip',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipaddress',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipinformationitemlist',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipspecialdate',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='vipspecialdate',
            name='specdatetype',
            field=models.CharField(blank=True, choices=[('011', '阴历生日'), ('020', '入会日期'), ('021', '结婚纪念日'), ('010', '生日')], default='', max_length=16, null=True, verbose_name='日期类型'),
        ),
        migrations.AlterField(
            model_name='wharehouse',
            name='company',
            field=models.CharField(blank=True, default='dsdemo', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
    ]
