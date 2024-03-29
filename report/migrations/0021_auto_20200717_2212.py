# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-07-17 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0020_auto_20200715_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportclassdata',
            name='report_class_type',
            field=models.CharField(blank=True, choices=[('A7', '面膜'), ('102', '020.脸型管理2阶'), ('E', '身体'), ('B6', '手霜/手膜'), ('302', '交响组合A-0.38'), ('A10', '眼膜'), ('201', '形体管理1阶'), ('E', '面部强效项目'), ('101', '010.脸型管理1阶'), ('123', '皮肤精细管理-清洁护理'), ('253', '女性中段管理3阶'), ('40', '懒虫美睫'), ('222', '身体精细管理-手足护理'), ('126', '皮肤精细管理-面膜及营养补充'), ('50', '无妆感丰眉'), ('212', '舒压减痛2阶'), ('104', '脸型管理4阶'), ('C', 'C:合作项目'), ('21', '身体舒压减痛'), ('104', '脸型管理 局部强化'), ('251', '女性中段管理1阶'), ('I', '其它'), ('B7', '颈胸霜'), ('A2', '化妆水/爽肤水'), ('A1', '面部角质调理'), ('513', '眉眼关系-无妆感丰睫'), ('A4', '眼唇精华'), ('B1', '沐浴露'), ('122', '皮肤精细管理-LPG机械手'), ('511', '眉眼关系-无妆感丰眉'), ('12', '面部皮肤精细管理'), ('303', '交响组合B-0.60'), ('121', '皮肤精细管理-紧致塑型'), ('A', 'A:基础项目'), ('512', '眉眼关系-无妆感厘睫'), ('A5', '面霜/乳液'), ('D', 'D:医美'), ('100', '店内项目'), ('252', '女性中段管理2阶'), ('305', '自由节奏A-26'), ('301', '如歌组合B-0.68'), ('306', '创始卡'), ('A3', '面部精华'), ('B5', '身体乳'), ('60', '无妆感厘睫'), ('70', '懒虫美发'), ('D', '面部'), ('23', '体型管理'), ('202', '形体管理2阶'), ('232', '体型管理-懒人运动'), ('125', '皮肤精细管理-眼部护理'), ('304', '交响组合C-10'), ('A9', '套装'), ('51', '眉眼关系管理'), ('233', '体型管理-身体LPG机械手'), ('10', '脸型管理'), ('300', '如歌组合A-0.38'), ('213', '舒压减痛3阶'), ('F', '眉眼关系管理'), ('15', '面部单加项'), ('B', 'B:大项目'), ('B4', '按摩油'), ('231', '体型管理-塑型 消耗'), ('30', '懒虫美甲'), ('500', '外包'), ('20', '形体管理'), ('C', '口服饮品'), ('G', '懒虫美甲'), ('A', '洁面/卸妆'), ('H', '懒虫美发'), ('103', '030.脸型管理3阶'), ('124', '皮肤精细管理-马步会员专享'), ('A8', '防晒'), ('22', '女性精细化管理'), ('B3', '身体角质调理'), ('B2', '浴盐'), ('211', '舒压减痛1阶'), ('306', '自由节奏B-38'), ('254', '女性中段管理4阶'), ('204', '形体管理4阶'), ('25', '女性中段管理'), ('221', '身体精细管理-女性胸部护理'), ('I01', '其它'), ('127', '皮肤精细管理-洁牙护理'), ('F', '身体强效项目'), ('223', '身体精细管理-角质调理及泡浴'), ('A6', '眼霜'), ('B', '洗发护发'), ('203', '形体管理3阶')], max_length=32, null=True, verbose_name='分类'),
        ),
    ]
