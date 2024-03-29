# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-05-14 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0046_auto_20190514_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='suptype',
            field=models.CharField(blank=True, choices=[('10', '储值卡'), ('20', '疗程卡'), ('30', '赠送储值卡'), ('40', '赠送疗程卡')], max_length=8, null=True, verbose_name='卡大类'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1001', '全身'), ('1002', '面部'), ('1003', '唇部'), ('1004', '胸部'), ('1005', '腹部'), ('1006', '背部'), ('1007', '腰部'), ('1008', '手臂'), ('1009', '肩颈'), ('1010', '手指'), ('1011', '臀部'), ('1012', '腿部'), ('1013', '颈部'), ('1014', '私密'), ('1015', '眼部'), ('1016', '眉毛'), ('1017', '眼睫线'), ('1018', '肝胆'), ('1019', '肠道'), ('1020', '局部'), ('1050', '手工'), ('1051', '仪器'), ('1052', '泡澡'), ('1053', '大光电'), ('1054', '皮肤管理'), ('1055', '纹绣'), ('1056', '骨雕'), ('1057', '自然疗法'), ('1058', '检测'), ('1059', '大健康'), ('1060', '医美'), ('1061', '细胞'), ('2001', '补水'), ('2002', '去角质'), ('2003', '美白'), ('2004', '柔滑'), ('2005', '亮肤'), ('2006', '均衡肤色'), ('2007', '舒缓放松'), ('2008', '紧致'), ('2009', '减内脂'), ('2010', '塑形'), ('2011', '美化'), ('2012', '循环'), ('2013', '淡斑'), ('2014', '脱毛'), ('2015', '抗皱'), ('2016', '抗敏'), ('2017', '修复'), ('2018', '修护'), ('2019', '抗衰'), ('2020', '抗老化'), ('2021', '免疫提升'), ('2022', '排毒'), ('2023', '面部'), ('2024', '身体'), ('2025', '仪器'), ('2026', '销售'), ('2027', '补充胶原蛋白'), ('2028', '滋养'), ('2028', '提升'), ('2028', '丰满'), ('2028', '疏通'), ('2028', '代谢'), ('2028', '抗疲劳'), ('2028', '活化细胞'), ('2028', '预防'), ('2099', '其他')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1001', '全身'), ('1002', '面部'), ('1003', '唇部'), ('1004', '胸部'), ('1005', '腹部'), ('1006', '背部'), ('1007', '腰部'), ('1008', '手臂'), ('1009', '肩颈'), ('1010', '手指'), ('1011', '臀部'), ('1012', '腿部'), ('1013', '颈部'), ('1014', '私密'), ('1015', '眼部'), ('1016', '眉毛'), ('1017', '眼睫线'), ('1018', '肝胆'), ('1019', '肠道'), ('1020', '局部'), ('1050', '手工'), ('1051', '仪器'), ('1052', '泡澡'), ('1053', '大光电'), ('1054', '皮肤管理'), ('1055', '纹绣'), ('1056', '骨雕'), ('1057', '自然疗法'), ('1058', '检测'), ('1059', '大健康'), ('1060', '医美'), ('1061', '细胞'), ('2001', '补水'), ('2002', '去角质'), ('2003', '美白'), ('2004', '柔滑'), ('2005', '亮肤'), ('2006', '均衡肤色'), ('2007', '舒缓放松'), ('2008', '紧致'), ('2009', '减内脂'), ('2010', '塑形'), ('2011', '美化'), ('2012', '循环'), ('2013', '淡斑'), ('2014', '脱毛'), ('2015', '抗皱'), ('2016', '抗敏'), ('2017', '修复'), ('2018', '修护'), ('2019', '抗衰'), ('2020', '抗老化'), ('2021', '免疫提升'), ('2022', '排毒'), ('2023', '面部'), ('2024', '身体'), ('2025', '仪器'), ('2026', '销售'), ('2027', '补充胶原蛋白'), ('2028', '滋养'), ('2028', '提升'), ('2028', '丰满'), ('2028', '疏通'), ('2028', '代谢'), ('2028', '抗疲劳'), ('2028', '活化细胞'), ('2028', '预防'), ('2099', '其他')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1001', '全身'), ('1002', '面部'), ('1003', '唇部'), ('1004', '胸部'), ('1005', '腹部'), ('1006', '背部'), ('1007', '腰部'), ('1008', '手臂'), ('1009', '肩颈'), ('1010', '手指'), ('1011', '臀部'), ('1012', '腿部'), ('1013', '颈部'), ('1014', '私密'), ('1015', '眼部'), ('1016', '眉毛'), ('1017', '眼睫线'), ('1018', '肝胆'), ('1019', '肠道'), ('1020', '局部'), ('1050', '手工'), ('1051', '仪器'), ('1052', '泡澡'), ('1053', '大光电'), ('1054', '皮肤管理'), ('1055', '纹绣'), ('1056', '骨雕'), ('1057', '自然疗法'), ('1058', '检测'), ('1059', '大健康'), ('1060', '医美'), ('1061', '细胞'), ('2001', '补水'), ('2002', '去角质'), ('2003', '美白'), ('2004', '柔滑'), ('2005', '亮肤'), ('2006', '均衡肤色'), ('2007', '舒缓放松'), ('2008', '紧致'), ('2009', '减内脂'), ('2010', '塑形'), ('2011', '美化'), ('2012', '循环'), ('2013', '淡斑'), ('2014', '脱毛'), ('2015', '抗皱'), ('2016', '抗敏'), ('2017', '修复'), ('2018', '修护'), ('2019', '抗衰'), ('2020', '抗老化'), ('2021', '免疫提升'), ('2022', '排毒'), ('2023', '面部'), ('2024', '身体'), ('2025', '仪器'), ('2026', '销售'), ('2027', '补充胶原蛋白'), ('2028', '滋养'), ('2028', '提升'), ('2028', '丰满'), ('2028', '疏通'), ('2028', '代谢'), ('2028', '抗疲劳'), ('2028', '活化细胞'), ('2028', '预防'), ('2099', '其他')], max_length=64, null=True, verbose_name='标签'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass1',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='项目营销分类1'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='tags',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1001', '全身'), ('1002', '面部'), ('1003', '唇部'), ('1004', '胸部'), ('1005', '腹部'), ('1006', '背部'), ('1007', '腰部'), ('1008', '手臂'), ('1009', '肩颈'), ('1010', '手指'), ('1011', '臀部'), ('1012', '腿部'), ('1013', '颈部'), ('1014', '私密'), ('1015', '眼部'), ('1016', '眉毛'), ('1017', '眼睫线'), ('1018', '肝胆'), ('1019', '肠道'), ('1020', '局部'), ('1050', '手工'), ('1051', '仪器'), ('1052', '泡澡'), ('1053', '大光电'), ('1054', '皮肤管理'), ('1055', '纹绣'), ('1056', '骨雕'), ('1057', '自然疗法'), ('1058', '检测'), ('1059', '大健康'), ('1060', '医美'), ('1061', '细胞'), ('2001', '补水'), ('2002', '去角质'), ('2003', '美白'), ('2004', '柔滑'), ('2005', '亮肤'), ('2006', '均衡肤色'), ('2007', '舒缓放松'), ('2008', '紧致'), ('2009', '减内脂'), ('2010', '塑形'), ('2011', '美化'), ('2012', '循环'), ('2013', '淡斑'), ('2014', '脱毛'), ('2015', '抗皱'), ('2016', '抗敏'), ('2017', '修复'), ('2018', '修护'), ('2019', '抗衰'), ('2020', '抗老化'), ('2021', '免疫提升'), ('2022', '排毒'), ('2023', '面部'), ('2024', '身体'), ('2025', '仪器'), ('2026', '销售'), ('2027', '补充胶原蛋白'), ('2028', '滋养'), ('2028', '提升'), ('2028', '丰满'), ('2028', '疏通'), ('2028', '代谢'), ('2028', '抗疲劳'), ('2028', '活化细胞'), ('2028', '预防'), ('2099', '其他')], max_length=64, null=True, verbose_name='标签'),
        ),
    ]
