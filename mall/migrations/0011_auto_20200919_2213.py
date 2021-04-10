# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-09-19 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mall', '0010_auto_20200903_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineshowtype',
            name='showtypecode',
            field=models.CharField(blank=True, choices=[('228', 'EPS'), ('229', '峰尚美'), ('223', '马步'), ('230', '伊立信'), ('227', '寇瀛'), ('193', '富丽活'), ('190', '外包项目'), ('203', '法儿曼'), ('189', '基纳'), ('212', '芳疗个性方案'), ('195', '市场采购'), ('179', '丝维诗兰 swiss line'), ('198', '抗旨君'), ('210', '美芾美源'), ('196', '彩护'), ('200', '普洱茶'), ('216', '资生堂'), ('183', '仪器辅料'), ('207', '礼品'), ('218', '酒水'), ('197', '托宁'), ('181', '云南特色'), ('215', '诗泽'), ('209', '罗正杰'), ('202', '水岸渔歌'), ('235', '普丽马维拉'), ('225', '悦历'), ('234', '艾贝诗'), ('226', '安娜'), ('105', '其他'), ('106', '12C'), ('107', '自研品牌'), ('108', '奥丽肤'), ('109', '珈纳'), ('110', 'Amala雅蔓兰'), ('111', '瑞妍'), ('112', '伊人专属'), ('117', '光学'), ('123', '托尼盖'), ('124', '戴安娜/凝肌'), ('126', '雍卡'), ('127', '药拓'), ('128', '吉备'), ('129', '晓酵素'), ('131', '蒂克'), ('133', '肌肤丽琦 GEMOLOGY'), ('137', '谷胱甘肽'), ('138', '美齿口'), ('139', '身体的辅助'), ('143', '小懒肉'), ('145', '胸部'), ('147', '懒虫'), ('154', '店内消耗品'), ('163', '丁航尧'), ('164', '李泽晨'), ('224', '攥住')], max_length=32, null=True, verbose_name='代码'),
        ),
    ]
