# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-11 20:39
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0091_auto_20190902_2036'),
    ]

    operations = [
        # migrations.AlterField(
        #     model_name='appoption',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='brand',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='cardsupertype',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='cardsupertype',
            name='pcode',
            field=models.CharField(blank=True, choices=[('A', '现金'), ('A1', '银联'), ('A2', '支付宝'), ('A3', '微信'), ('A4', '美团'), ('B', '储值卡付'), ('B1', '疗程卡付'), ('Z', '免单/赠送'), ('Z1', '赠送储值卡付'), ('Z2', '赠送疗程卡付'), ('Z9', '转卡')], max_length=16, null=True, verbose_name='对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('400', '肠道'), ('100', '面部'), ('110', '眼部'), ('230', '背部'), ('300', '肝胆'), ('200', '身体'), ('210', '胸部'), ('220', '腹部'), ('205', '肩颈'), ('240', '腿部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='brand',
            field=models.CharField(blank=True, choices=[('223', '马步'), ('193', '富丽活'), ('190', '外包项目'), ('203', '法儿曼'), ('189', '基纳'), ('212', '芳疗个性方案'), ('195', '市场采购'), ('179', '丝维诗兰 swiss line'), ('198', '抗旨君'), ('210', '美芾美源'), ('196', '彩护'), ('200', '普洱茶'), ('216', '资生堂'), ('183', '仪器辅料'), ('207', '礼品'), ('218', '酒水'), ('197', '托宁'), ('181', '云南特色'), ('215', '诗泽'), ('209', '罗正杰'), ('202', '水岸渔歌'), ('225', '悦历'), ('105', '其他'), ('106', '12C'), ('107', '自研品牌'), ('108', '奥丽肤'), ('109', '珈纳'), ('110', 'Amala雅蔓兰'), ('111', '瑞妍'), ('112', '伊人专属'), ('117', '光学'), ('123', '托尼盖'), ('124', '戴安娜/凝肌'), ('126', '雍卡'), ('127', '药拓'), ('128', '吉备'), ('129', '晓酵素'), ('131', '蒂克'), ('133', '肌肤丽琦 GEMOLOGY'), ('137', '谷胱甘肽'), ('138', '美齿口'), ('139', '身体的辅助'), ('143', '小懒肉'), ('145', '胸部'), ('147', '懒虫'), ('154', '店内消耗品'), ('163', '丁航尧'), ('164', '李泽晨'), ('224', '攥住')], max_length=16, null=True, verbose_name='品牌'),
        ),
        # migrations.AlterField(
        #     model_name='cardtype',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('80', '储值卡'), ('60', '造型'), ('106', '12C'), ('110', 'Amala雅蔓兰'), ('108', '奥丽肤'), ('196', '彩护'), ('124', '戴安娜/凝肌'), ('131', '蒂克'), ('154', '店内消耗品'), ('163', '丁航尧'), ('203', '法儿曼'), ('212', '芳疗个性方案'), ('193', '富丽活'), ('137', '谷胱甘肽'), ('117', '光学'), ('133', '肌肤丽琦 GEMOLOGY'), ('189', '基纳'), ('128', '吉备'), ('109', '珈纳'), ('218', '酒水'), ('198', '抗旨君'), ('147', '懒虫'), ('207', '礼品'), ('164', '李泽晨'), ('209', '罗正杰'), ('138', '美齿口'), ('210', '美芾美源'), ('200', '普洱茶'), ('105', '其他'), ('111', '瑞妍'), ('215', '诗泽'), ('195', '市场采购'), ('202', '水岸渔歌'), ('179', '丝维诗兰 swiss line'), ('123', '托尼盖'), ('197', '托宁'), ('190', '外包项目'), ('129', '晓酵素'), ('145', '胸部'), ('127', '药拓'), ('183', '仪器辅料'), ('126', '雍卡'), ('181', '云南特色'), ('216', '资生堂'), ('107', '自研品牌'), ('90', '其它'), ('82', '疗程卡'), ('10', '面部'), ('83', '时效卡'), ('81', '产品卡'), ('20', '身体')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('40', '懒虫美睫'), ('50', '无妆感丰眉'), ('60', '无妆感厘睫'), ('70', '懒虫美发'), ('10', '全套服务'), ('30', '懒虫美甲'), ('20', '单加项')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            field=models.CharField(blank=True, choices=[('C', 'C:瘦狗项目'), ('B', 'B:金牛项目'), ('D', 'D:问题项目'), ('A', 'A:明星项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('C', 'C:合作项目'), ('A', 'A:基础项目'), ('D', 'D:医美'), ('B', 'B:大项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='suptype',
            field=models.CharField(blank=True, choices=[('20', '疗程卡'), ('40', '赠送疗程'), ('10', '储值卡'), ('30', '赠送储值'), ('14', '产品卡'), ('15', '月卡/季卡')], max_length=8, null=True, verbose_name='卡大类'),
        ),
        # migrations.AlterField(
        #     model_name='cardtypevsdiscountclass',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='cardvsdi',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='empl',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='empl',
            name='position',
            field=models.CharField(blank=True, choices=[('210', '店长'), ('110', '身体护理师'), ('200', '准店长'), ('200', '顾问'), ('100', '美疗师'), ('400', '其他'), ('100', '面部护理师'), ('110', '美体师'), ('300', '库管')], db_column='POSITION', max_length=20, null=True, verbose_name='职位'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='storecode',
            field=models.CharField(blank=True, choices=[('00', '总部'), ('01', '赛特店'), ('02', '安立店'), ('03', '长安店'), ('04', '马奈店'), ('88', '练习店')], max_length=16, null=True, verbose_name='所属门店'),
        ),
        migrations.AlterField(
            model_name='empl',
            name='team',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='业务组别'),
        ),
        # migrations.AlterField(
        #     model_name='enactmen',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='goods',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('400', '肠道'), ('100', '面部'), ('110', '眼部'), ('230', '背部'), ('300', '肝胆'), ('200', '身体'), ('210', '胸部'), ('220', '腹部'), ('205', '肩颈'), ('240', '腿部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='brand',
            field=models.CharField(blank=True, choices=[('223', '马步'), ('193', '富丽活'), ('190', '外包项目'), ('203', '法儿曼'), ('189', '基纳'), ('212', '芳疗个性方案'), ('195', '市场采购'), ('179', '丝维诗兰 swiss line'), ('198', '抗旨君'), ('210', '美芾美源'), ('196', '彩护'), ('200', '普洱茶'), ('216', '资生堂'), ('183', '仪器辅料'), ('207', '礼品'), ('218', '酒水'), ('197', '托宁'), ('181', '云南特色'), ('215', '诗泽'), ('209', '罗正杰'), ('202', '水岸渔歌'), ('225', '悦历'), ('105', '其他'), ('106', '12C'), ('107', '自研品牌'), ('108', '奥丽肤'), ('109', '珈纳'), ('110', 'Amala雅蔓兰'), ('111', '瑞妍'), ('112', '伊人专属'), ('117', '光学'), ('123', '托尼盖'), ('124', '戴安娜/凝肌'), ('126', '雍卡'), ('127', '药拓'), ('128', '吉备'), ('129', '晓酵素'), ('131', '蒂克'), ('133', '肌肤丽琦 GEMOLOGY'), ('137', '谷胱甘肽'), ('138', '美齿口'), ('139', '身体的辅助'), ('143', '小懒肉'), ('145', '胸部'), ('147', '懒虫'), ('154', '店内消耗品'), ('163', '丁航尧'), ('164', '李泽晨'), ('224', '攥住')], max_length=16, null=True, verbose_name='品牌'),
        ),
        # migrations.AlterField(
        #     model_name='goods',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('80', '储值卡'), ('60', '造型'), ('106', '12C'), ('110', 'Amala雅蔓兰'), ('108', '奥丽肤'), ('196', '彩护'), ('124', '戴安娜/凝肌'), ('131', '蒂克'), ('154', '店内消耗品'), ('163', '丁航尧'), ('203', '法儿曼'), ('212', '芳疗个性方案'), ('193', '富丽活'), ('137', '谷胱甘肽'), ('117', '光学'), ('133', '肌肤丽琦 GEMOLOGY'), ('189', '基纳'), ('128', '吉备'), ('109', '珈纳'), ('218', '酒水'), ('198', '抗旨君'), ('147', '懒虫'), ('207', '礼品'), ('164', '李泽晨'), ('209', '罗正杰'), ('138', '美齿口'), ('210', '美芾美源'), ('200', '普洱茶'), ('105', '其他'), ('111', '瑞妍'), ('215', '诗泽'), ('195', '市场采购'), ('202', '水岸渔歌'), ('179', '丝维诗兰 swiss line'), ('123', '托尼盖'), ('197', '托宁'), ('190', '外包项目'), ('129', '晓酵素'), ('145', '胸部'), ('127', '药拓'), ('183', '仪器辅料'), ('126', '雍卡'), ('181', '云南特色'), ('216', '资生堂'), ('107', '自研品牌'), ('90', '其它'), ('82', '疗程卡'), ('10', '面部'), ('83', '时效卡'), ('81', '产品卡'), ('20', '身体')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('40', '懒虫美睫'), ('50', '无妆感丰眉'), ('60', '无妆感厘睫'), ('70', '懒虫美发'), ('10', '全套服务'), ('30', '懒虫美甲'), ('20', '单加项')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            field=models.CharField(blank=True, choices=[('200', '酵素'), ('500', '美发品'), ('100', '护肤品')], db_column='goodsct', max_length=16, null=True, verbose_name='商品折扣分类'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass1',
            field=models.CharField(blank=True, choices=[('C', 'C:瘦狗项目'), ('B', 'B:金牛项目'), ('D', 'D:问题项目'), ('A', 'A:明星项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('C', 'C:合作项目'), ('A', 'A:基础项目'), ('D', 'D:医美'), ('B', 'B:大项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法二）'),
        ),
        # migrations.AlterField(
        #     model_name='goodsct',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='goodsprice',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='hdsysuser',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='hdsysuser',
            name='storelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('00', '总部'), ('01', '赛特店'), ('02', '安立店'), ('03', '长安店'), ('04', '马奈店'), ('88', '练习店')], max_length=128, null=True, verbose_name='可用门店'),
        ),
        migrations.AlterField(
            model_name='item',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('400', '肠道'), ('100', '面部'), ('110', '眼部'), ('230', '背部'), ('300', '肝胆'), ('200', '身体'), ('210', '胸部'), ('220', '腹部'), ('205', '肩颈'), ('240', '腿部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(blank=True, choices=[('223', '马步'), ('193', '富丽活'), ('190', '外包项目'), ('203', '法儿曼'), ('189', '基纳'), ('212', '芳疗个性方案'), ('195', '市场采购'), ('179', '丝维诗兰 swiss line'), ('198', '抗旨君'), ('210', '美芾美源'), ('196', '彩护'), ('200', '普洱茶'), ('216', '资生堂'), ('183', '仪器辅料'), ('207', '礼品'), ('218', '酒水'), ('197', '托宁'), ('181', '云南特色'), ('215', '诗泽'), ('209', '罗正杰'), ('202', '水岸渔歌'), ('225', '悦历'), ('105', '其他'), ('106', '12C'), ('107', '自研品牌'), ('108', '奥丽肤'), ('109', '珈纳'), ('110', 'Amala雅蔓兰'), ('111', '瑞妍'), ('112', '伊人专属'), ('117', '光学'), ('123', '托尼盖'), ('124', '戴安娜/凝肌'), ('126', '雍卡'), ('127', '药拓'), ('128', '吉备'), ('129', '晓酵素'), ('131', '蒂克'), ('133', '肌肤丽琦 GEMOLOGY'), ('137', '谷胱甘肽'), ('138', '美齿口'), ('139', '身体的辅助'), ('143', '小懒肉'), ('145', '胸部'), ('147', '懒虫'), ('154', '店内消耗品'), ('163', '丁航尧'), ('164', '李泽晨'), ('224', '攥住')], max_length=16, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='item',
            name='company',
            field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('80', '储值卡'), ('60', '造型'), ('106', '12C'), ('110', 'Amala雅蔓兰'), ('108', '奥丽肤'), ('196', '彩护'), ('124', '戴安娜/凝肌'), ('131', '蒂克'), ('154', '店内消耗品'), ('163', '丁航尧'), ('203', '法儿曼'), ('212', '芳疗个性方案'), ('193', '富丽活'), ('137', '谷胱甘肽'), ('117', '光学'), ('133', '肌肤丽琦 GEMOLOGY'), ('189', '基纳'), ('128', '吉备'), ('109', '珈纳'), ('218', '酒水'), ('198', '抗旨君'), ('147', '懒虫'), ('207', '礼品'), ('164', '李泽晨'), ('209', '罗正杰'), ('138', '美齿口'), ('210', '美芾美源'), ('200', '普洱茶'), ('105', '其他'), ('111', '瑞妍'), ('215', '诗泽'), ('195', '市场采购'), ('202', '水岸渔歌'), ('179', '丝维诗兰 swiss line'), ('123', '托尼盖'), ('197', '托宁'), ('190', '外包项目'), ('129', '晓酵素'), ('145', '胸部'), ('127', '药拓'), ('183', '仪器辅料'), ('126', '雍卡'), ('181', '云南特色'), ('216', '资生堂'), ('107', '自研品牌'), ('90', '其它'), ('82', '疗程卡'), ('10', '面部'), ('83', '时效卡'), ('81', '产品卡'), ('20', '身体')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('40', '懒虫美睫'), ('50', '无妆感丰眉'), ('60', '无妆感厘睫'), ('70', '懒虫美发'), ('10', '全套服务'), ('30', '懒虫美甲'), ('20', '单加项')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            field=models.CharField(blank=True, choices=[('C', 'C:瘦狗项目'), ('B', 'B:金牛项目'), ('D', 'D:问题项目'), ('A', 'A:明星项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('C', 'C:合作项目'), ('A', 'A:基础项目'), ('D', 'D:医美'), ('B', 'B:大项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法二）'),
        ),
        # migrations.AlterField(
        #     model_name='objectvalue2',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='paymode',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='position',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='promotions',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='promotionsdetail',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='promotionsdetail',
            name='sgcode',
            field=models.CharField(blank=True, choices=[('110240', '水润紧致-肌理重组筋膜棒水光护理组合2016'), ('110241', '敏感修复-肌理重组筋膜棒水光护理组合2016'), ('110242', '净白紧致-肌理重组筋膜棒水光护理组合2016'), ('110243', '紧致再生-组织重建筋膜棒水光护理组合2016'), ('110244', '弹润嫩白-组织重建筋膜棒水光护理组合2016'), ('110245', '小微轮水润紧致护理2016'), ('110246', '小微轮嫩白护理2016'), ('110247', '小微轮净化护理2016'), ('110248', '胶原再生仪护理-2017版'), ('110249', '轮廓提升仪-2017版'), ('110250', '小小微轮玻尿酸水润护理 22周年版'), ('110251', '小微轮抗氧化年轻态护理 22周年版'), ('110252', "筋膜水光护理服务费 70'"), ('110253', "小微轮抗氧化年轻态护理服务费 60'"), ('110254', '骨缝重构面部2阶护理'), ('110255', '骨缝重构面部I阶护理'), ('110256', '盈润经典胶原护理 （C O M）2016'), ('110257', '香润紧致玫瑰护理（STYX）2016'), ('110258', '补水修复老虎草护理（STYX）2016'), ('110259', '净白活氧护理（Klapp）2016'), ('110260', '青春保湿紫草护理(Olive)2016'), ('110261', '紧致胶原护理（O K M）2016'), ('110262', '紫草紧致护理（含仪器） 22周年版'), ('110263', "钻石美颜抗皱护理80'"), ('120002', '过敏急救护理'), ('120003', '开启 7天净化方案'), ('120004', '胶原.唇膜'), ('120005', '胶原.眼膜'), ('120006', '脑部充电-SPA'), ('120105', '射频紧肤局部-2017版 25分钟（额头、眼部、颈部）'), ('120106', '辅助2-射频/轮廓'), ('120107', '水飞梭洁肤护理 22周年版'), ('120108', '舒压亮眼护理2016'), ('120109', '肌理重组仪2016'), ('120110', '经典净肤2016'), ('120111', '活力净肤2016'), ('120112', '四重净肤2016'), ('120113', '紧致提升肌肉操2016'), ('120114', '肌腹拍打操2016'), ('120115', '舒压平衡操2016'), ('120116', '高压养疗2016'), ('120117', 'LPG紧致强化-2016'), ('120118', '11度笑眼-2016'), ('120119', '胶原精华膜-美白2016'), ('120120', '胶原精华膜-修复2016'), ('120121', '胶原精华膜-补水2016'), ('120122', '抗皱紧肤胶原精华膜2016'), ('120123', '紧致提升整体操2016'), ('120124', '净化松解操'), ('120125', '射频迷你紧肤仪'), ('120126', '射频迷你塑型仪'), ('120127', '微电流仪 22周年版'), ('120128', '谷胱甘肽靓肤面膜 22周年版'), ('120129', '四级射频 23周年版'), ('120130', "颈部肌肉锻炼 15' 2017版"), ('120131', "面颈部肌肉力量训练2.0 15'"), ('120132', '自带面膜手工服务费'), ('120133', "面颈部肌肉力量训练 30'"), ('120134', '开口笑'), ('120135', '钻石凝时紧致面膜套装'), ('120136', "会员价 肌腹拍打操2019 30'不打折"), ('120137', '强效镇静补湿面膜护理2019'), ('120138', '鱼子精华2016'), ('120139', '嫩白浓缩液2016'), ('120140', '弹力浓缩液2016'), ('210002', '产后疲劳恢复'), ('210327', "超能纤美 60' 2016"), ('210328', "超能纤美 90'  2016"), ('210329', "专业骨缝重构腰椎骨盆50'"), ('210330', "女性骨盆矫正缩窄手工护理50'"), ('210331', '舒缓放松2016'), ('210332', '速纤塑型 2016'), ('210333', '肩颈痛沉改善-乐音体感全身护理2016'), ('210334', '颈背舒压全身护理2.0（舒缓放松2.0）'), ('220002', '产后肩颈痛沉局部项目'), ('220003', 'LPG舒缓腿部肿胀'), ('220004', '胸部.保养膜'), ('220005', '香氛.泡浴'), ('220034', "超能纤美 30' 2016"), ('220035', '骨缝重构-腰椎 骨盆调整'), ('220036', '骨缝重构-颈胸椎调整'), ('220037', '女性中段37℃热循环2016'), ('220038', '肩颈痛沉改善-乐音体感手工护理2016'), ('220039', '胃肠不适改善-乐音体感手工护理2016'), ('220040', '腿部肿胀舒缓-乐音体感手工护理2016'), ('220041', 'LPG身体局部强化护理2016'), ('220042', '手工护理-局部强化关节精细护理'), ('220043', '香氛泡浴2016'), ('220044', "速纤塑型局部强化护理 30' 2016"), ('220045', '海盐&水疗精油净肤'), ('220046', '高跟鞋脚精细护理 23周年版'), ('220047', "小懒肉1.0-局部护理 15' 2017版"), ('220048', "小懒肉1.0-心肺功能改善 10' 2017版"), ('220049', "手膜护理 35'"), ('220050', "足膜护理35'"), ('220051', "颈肩养护-上交叉 II阶 45'"), ('220052', "青少年含胸驼背预防护理 30'"), ('220053', '方拓单次-微循环改善'), ('220054', '方拓单次-暖宫散寒'), ('630002', '康醇纯色款（含2个跳色）手部'), ('630003', '康醇纯色款（含2个跳色）脚部'), ('630004', '康醇造型甲油胶简约款 手部（法式 渐变 简约彩绘设计款）'), ('630005', '康醇造型甲油胶简约款 脚部（法式 渐变 简约彩绘设计款）'), ('630006', '康醇甲油造型胶时尚款 手部'), ('630007', '康醇甲油造型胶时尚款 脚部'), ('630008', '日本SACRA纯色款I(含2个跳色）  手部'), ('630009', '日本SACRA纯色款I(含2个跳色）  脚部'), ('630010', '日本SACRA造型甲油胶简约 手部（法式 渐变 简约设计款）'), ('630011', '日本SACRA造型甲油胶简约款 脚部（法式 渐变 简约设计款）'), ('630012', '日本SACRA造型甲油胶时尚款 手部'), ('630013', '日本SACRA造型甲油胶时尚款 脚部'), ('630014', '甲油胶封层（不含修手）'), ('630015', '卸除贴片/水晶/光疗甲'), ('630016', 'LCN指甲深层滋养护理 手部'), ('630017', 'LCN指甲深层滋养护理 脚部'), ('630018', 'LCN手部SPA'), ('630019', 'LCN脚部SPA'), ('630020', '蚕丝蛋白空心美睫'), ('630021', '手指造型 2个'), ('630022', '日本魔镜粉（手脚均可使用）'), ('630023', '日本贴纸或饰品（2选1）'), ('630024', '卸除甲油胶'), ('630025', 'OPI手部基础护理'), ('630026', 'OPI脚部基础护理'), ('630027', '手指造型 一只手'), ('630028', '软枕液 次'), ('630029', '手部 日本SACRA纯色款I(含2个跳色）'), ('630030', '脚部 日本SACRA纯色款I(含2个跳色）'), ('630031', '手部日本SACRA造型甲油胶简约（法式 渐变 简约设计款）'), ('630032', '贴片甲'), ('630033', '贴片水晶'), ('630034', '水晶 光疗甲修补/加固'), ('630035', '修甲'), ('630036', '单色水晶甲、光疗甲'), ('640002', '蚕丝蛋白加密美睫'), ('640003', '修补睫毛 美国LASA BE LONG'), ('640004', '日本MISS纤细3D美睫'), ('640005', '日本MISS铂金6D美睫'), ('640006', '修补睫毛 日本MISS EYE DOR'), ('640007', '卸除假睫毛'), ('640008', '睫毛加密 美国LASH BE LONG'), ('640009', '彩色睫毛'), ('640010', '单加彩色睫毛'), ('650002', '无妆感丰眉-内部价'), ('650003', '无妆感丰眉-B'), ('650004', '无妆感丰眉-C'), ('650005', '无妆感丰眉-D'), ('650006', '丰妆感丰眉-D'), ('650007', '无妆感丰眉-E'), ('660002', '无妆感眼睫线'), ('660003', '无妆感美瞳线'), ('660004', '无妆感亮瞳黑'), ('660005', '无妆感3D芭比眼睫毛线'), ('670002', '护理加工费 22周年版'), ('670003', '剪发-创意总监 22周年版'), ('670004', '剪发-技术总监 22周年版'), ('670005', '剪发-高级发型师 22周年版'), ('670006', '剪流海-创意总监 22周年版'), ('670007', '剪流海-高级发型师 22周年版'), ('670008', '烫流海-安立 22周年版'), ('670009', '洗吹造型（短） 22周年版'), ('670010', '洗吹造型（长） 22周年版'), ('670011', '电棒造型 22周年版'), ('670012', '晚宴造型 22周年版'), ('670013', '晚宴化妆 22周年版'), ('670014', '日妆 22周年版'), ('670015', '全效洗发 22周年版'), ('670016', '润丝洗发 22周年版'), ('670017', '头部按摩 22周年版'), ('670018', '自带彩焗加工费 22周年版'), ('670019', '柔亮染发（短） 22周年版'), ('670020', '柔亮染发（中） 22周年版'), ('670021', '柔亮染发（长） 22周年版'), ('670022', '柔亮染发（特长） 22周年版'), ('670023', '奢华修护染发（短） 22周年版'), ('670024', '奢华修护染发（中） 22周年版'), ('670025', '奢华修护染发（长） 22周年版'), ('670026', '奢华修护染发（特长） 22周年版'), ('670027', '创意染发（短） 22周年版'), ('670028', '创意染发（中） 22周年版'), ('670029', '创意染发（长） 22周年版'), ('670030', '创意染发（特长） 22周年版'), ('670031', '韩国酸护打蜡（短） 22周年版'), ('670032', '韩国酸护打蜡（中） 22周年版'), ('670033', '韩国酸护打蜡（长） 22周年版'), ('670034', '韩国酸护打蜡（特长） 22周年版'), ('670035', '韩国酸护打蜡/片（短） 22周年版'), ('670036', '韩国酸护打蜡/片（中） 22周年版'), ('670037', '韩国酸护打蜡/片（长） 22周年版'), ('670038', '漂染（短） 22周年版'), ('670039', '漂染（中） 22周年版'), ('670040', '漂染（长） 22周年版'), ('670041', '漂染（特长） 22周年版'), ('670042', '挑染/片 22周年版'), ('670043', '局部染-安立 22周年版'), ('670044', '局部锡纸挑染（短） 22周年版'), ('670045', '局部锡纸挑染（中） 22周年版'), ('670046', '局部锡纸挑染（长） 22周年版'), ('670047', '局部锡纸挑染（特长） 22周年版'), ('670048', '炫丝冷烫（短） 22周年版'), ('670049', '炫丝冷烫（中） 22周年版'), ('670050', '炫丝冷烫（长） 22周年版'), ('670051', '炫丝冷烫（特长） 22周年版'), ('670052', '韩国营养烫（短） 22周年版'), ('670053', '韩国营养烫（中） 22周年版'), ('670054', '韩国营养烫（长） 22周年版'), ('670055', '韩国营养烫（特长） 22周年版'), ('670056', '护理烫（短） 22周年版'), ('670057', '护理烫（中） 22周年版'), ('670058', '护理烫（长） 22周年版'), ('670059', '护理烫（特长） 22周年版'), ('670060', '健康热烫（短） 22周年版'), ('670061', '健康热烫（中） 22周年版'), ('670062', '健康热烫（长） 22周年版'), ('670063', '健康热烫（特长） 22周年版'), ('670064', '护理热烫（短） 22周年版'), ('670065', '护理热烫（中） 22周年版'), ('670066', '护理热烫（长） 22周年版'), ('670067', '护理热烫（特长） 22周年版'), ('670068', '局部烫（短） 22周年版'), ('670069', '局部烫（中） 22周年版'), ('670070', '局部烫（长） 22周年版'), ('670071', '局部烫（特长） 22周年版'), ('670072', '离子烫（短） 22周年版'), ('670073', '离子烫（中） 22周年版'), ('670074', '离子烫（长） 22周年版'), ('670075', '离子烫（特长） 22周年版'), ('670076', '离子顺直烫（短） 22周年版'), ('670077', '离子顺直烫（中） 22周年版'), ('670078', '离子顺直烫（长） 22周年版'), ('670079', '离子顺直烫（特长） 22周年版'), ('670080', '离子护理烫（短） 22周年版'), ('670081', '离子护理烫（中） 22周年版'), ('670082', '离子护理烫（长） 22周年版'), ('670083', '离子护理烫（特长） 22周年版'), ('670084', '特殊烫加收服务费 22周年版'), ('670085', '韩国植物故事头皮调理 22周年版'), ('670086', '韩国植物故事头皮补水发膜 22周年版'), ('670087', '韩国植物故事头皮舒缓凝乳修复 22周年版'), ('670088', '基础营养护理（短） 22周年版'), ('670089', '基础营养护理（中） 22周年版'), ('670090', '基础营养护理（长） 22周年版'), ('670091', '基础营养护理（特长） 22周年版'), ('670092', '深层修复发膜（短） 22周年版'), ('670093', '深层修复发膜（中） 22周年版'), ('670094', '深层修复发膜（长） 22周年版'), ('670095', '深层修复发膜（特长）22周年版'), ('670096', '极致修复发膜（短） 22周年版'), ('670097', '极致修复发膜（中） 22周年版'), ('670098', '极致修复发膜（长） 22周年版'), ('670099', '极致修复发膜（特长）22周年版'), ('670100', '纳米离子头皮发丝补水 22周年版'), ('670101', '微型无痕（L）基础 22周年版'), ('670102', '微型无痕（L）好发质 22周年版'), ('670103', '微型无痕（XL）基础 22周年版'), ('670104', '微型无痕（XL）好发质 22周年版'), ('670105', '微型无痕（XXL）基础 22周年版'), ('670106', '微型无痕（XXL）好发质 22周年版'), ('670107', '微型无痕（XXXL）基础 22周年版'), ('670108', '微型无痕（XXXL）好发质 22周年版'), ('670109', '水晶无痕（L）基础 22周年版'), ('670110', '水晶无痕（L）好发质 22周年版'), ('670111', '水晶无痕（XL）基础 22周年版'), ('670112', '水晶无痕（XL）好发质 22周年版'), ('670113', '水晶无痕（XXL）基础 22周年版'), ('670114', '水晶无痕（XXL）好发质 22周年版'), ('670115', '局部接发 22周年版'), ('670116', '洗剪吹 22周年版'), ('670117', '洗吹（S） 22周年版'), ('670118', '洗吹（M） 22周年版'), ('670119', '洗吹（L） 22周年版'), ('670120', '普通烫(S)  22周年版'), ('670121', '普通烫(M) 22周年版'), ('670122', '普通烫(L) 22周年版'), ('670123', '普通烫(XL) 22周年版'), ('670124', '安心烫(S)  22周年版'), ('670125', '安心烫(M) 22周年版'), ('670126', '安心烫(L) 22周年版'), ('670127', '安心烫(XL) 22周年版'), ('670128', '特殊烫(S) 22周年版'), ('670129', '特殊烫(M) 22周年版'), ('670130', '特殊烫(L) 22周年版'), ('670131', '特殊烫(XL) 22周年版'), ('670132', '陶瓷烫(S) 22周年版'), ('670133', '陶瓷烫(M) 22周年版'), ('670134', '陶瓷烫(L) 22周年版'), ('670135', '陶瓷烫(XL) 22周年版'), ('670136', '数码烫(S) 22周年版'), ('670137', '数码烫(M) 22周年版'), ('670138', '数码烫(L) 22周年版'), ('670139', '数码烫(XL) 22周年版'), ('670140', '离子烫(S) 22周年版'), ('670141', '离子烫(M) 22周年版'), ('670142', '离子烫(L) 22周年版'), ('670143', '离子烫(XL) 22周年版'), ('670144', '局部烫(S) 22周年版'), ('670145', '局部烫(M) 22周年版'), ('670146', '局部烫(L) 22周年版'), ('670147', '烫流海(冷烫） 22周年版'), ('670148', '烫流海（热烫） 22周年版'), ('670149', '柔亮染发(S)  22周年版'), ('670150', '柔亮染发(M) 22周年版'), ('670151', '柔亮染发(L) 22周年版'), ('670152', '柔亮染发(XL) 22周年版'), ('670153', '染发/漂染(S) 22周年版'), ('670154', '染发/漂染(M) 22周年版'), ('670155', '染发/漂染(L) 22周年版'), ('670156', '染发/漂染(XL) 22周年版'), ('670157', '安心染发(S)  22周年版'), ('670158', '安心染发(M) 22周年版'), ('670159', '安心染发(L) 22周年版'), ('670160', '安心染发(XL) 22周年版'), ('670161', '局部染 22周年版'), ('670162', '安心局部染 22周年版'), ('670163', '局部锡纸挑染(S) 22周年版'), ('670164', '局部锡纸挑染(M) 22周年版'), ('670165', '局部锡纸挑染(L) 22周年版'), ('670166', '局部锡纸挑染(XL) 22周年版'), ('670167', '锡纸挑染(S) 22周年版'), ('670168', '锡纸挑染(M) 22周年版'), ('670169', '锡纸挑染(L) 22周年版'), ('670170', '锡纸挑染(XL) 22周年版'), ('670171', '片染/条 22周年版'), ('670172', 'INOA无胺染(S) 22周年版'), ('670173', 'INOA无胺染(M) 22周年版'), ('670174', 'INOA无胺染(L) 22周年版'), ('670175', 'INOA无胺染(XL) 22周年版'), ('670176', '基础营养(S) 22周年版'), ('670177', '基础营养(M) 22周年版'), ('670178', '基础营养(L) 22周年版'), ('670179', '基础营养(XL) 22周年版'), ('670180', '资生堂专业调理系统(S) 22周年版'), ('670181', '资生堂专业调理系统(M) 22周年版'), ('670182', '资生堂专业调理系统(L) 22周年版'), ('670183', 'MOCOTA 深层护理(S) 22周年版'), ('670184', 'MOCOTA 深层护理(M) 22周年版'), ('670185', 'MOCOTA 深层护理(L) 22周年版'), ('670186', 'MOCOTA 深层护理(XL) 22周年版'), ('670187', '头皮焕发 22周年版'), ('670188', '染烫修护 22周年版'), ('670189', '发蕊强化精华 22周年版'), ('670190', '剪流海 22周年版'), ('670191', '剪流海(含洗） 22周年版'), ('670192', '单洗 22周年版'), ('670193', '头皮修复护理'), ('670194', '局部无胺染-1'), ('670195', '非洲烫（小卷）（M)'), ('670196', '非洲烫（小卷）（S)'), ('670197', '非洲烫（小卷）（L)'), ('670198', '非洲烫（小卷）（XL)'), ('670199', '资生堂专业调理系统（XL） 22周年版'), ('670200', '头皮生发护理'), ('670201', '染发 自带产品'), ('670202', '洗剪吹'), ('670203', '剪流海'), ('670204', '剪流海(含洗）'), ('670205', '单洗'), ('670206', '洗吹（S)'), ('670207', '洗吹（M)'), ('670208', '洗吹（L）'), ('670209', '普通烫(S)'), ('670210', '普通烫(M)'), ('670211', '普通烫(L)'), ('670212', '特殊烫(S)'), ('670213', '特殊烫(M)'), ('670214', '特殊烫(L)'), ('670215', '特殊烫(XL)'), ('670216', '陶瓷烫(S)'), ('670217', '陶瓷烫(M)'), ('670218', '陶瓷烫(L)'), ('670219', '陶瓷烫(XL)'), ('670220', '数码烫(S)'), ('670221', '数码烫(M)'), ('670222', '数码烫(L)'), ('670223', '数码烫(XL)'), ('670224', '离子烫(S)'), ('670225', '离子烫(M)'), ('670226', '离子烫(L)'), ('670227', '离子烫(XL)'), ('670228', '局部烫(S)'), ('670229', '局部烫(M)'), ('670230', '局部烫(L)'), ('670231', '烫流海(冷烫）'), ('670232', '烫流海（热烫）'), ('670233', '柔亮染发(S)'), ('670234', '柔亮染发(M)'), ('670235', '柔亮染发(L)'), ('670236', '柔亮染发(XL)'), ('670237', '染发/漂染(S)'), ('670238', '染发/漂染(M)'), ('670239', '染发/漂染(L)'), ('670240', '染发/漂染(XL)'), ('670241', '安心染发(S)'), ('670242', '安心染发(M)'), ('670243', '安心染发(L)'), ('670244', '安心染发(XL)'), ('670245', 'Z 局部染'), ('670246', '安心局部染'), ('670247', '局部锡纸挑染(S)'), ('670248', '局部锡纸挑染(M)'), ('670249', '局部锡纸挑染(L)'), ('670250', '局部锡纸挑染(XL)'), ('670251', '锡纸挑染(S)'), ('670252', '锡纸挑染(M)'), ('670253', '锡纸挑染(L)'), ('670254', '锡纸挑染(XL)'), ('670255', '片染/条'), ('670256', 'INOA无胺染(S)'), ('670257', 'INOA无胺染(M)'), ('670258', 'INOA无胺染(L)'), ('670259', 'INOA无胺染(XL)'), ('670260', '局部无胺染'), ('670261', 'Z基础营养(S)'), ('670262', 'Z基础营养(M)'), ('670263', 'Z基础营养(L)'), ('670264', 'Z基础营养(XL)'), ('670265', 'Z资生堂专业调理系统(S)'), ('670266', 'Z 资生堂专业调理系统(M)'), ('670267', 'Z 资生堂专业调理系统(L)'), ('670268', 'Z 资生堂专业调理系统(XL)'), ('670269', 'Z MOCOTA 深层护理(S)'), ('670270', 'Z MOCOTA 深层护理(M)'), ('670271', 'Z MOCOTA 深层护理(L)'), ('670272', 'Z MOCOTA 深层护理(XL)'), ('670273', 'Z头皮焕发'), ('670274', 'Z染烫修护'), ('670275', 'Z发蕊强化精华'), ('670276', 'Z头皮防护乳'), ('670277', 'Z头皮修复护理'), ('670278', 'Z局部无胺染-1'), ('670279', 'Z非洲烫（小卷）（S)'), ('670280', 'Z非洲烫（小卷）（M)'), ('670281', 'Z非洲烫（小卷）（L)'), ('670282', 'Z非洲烫（小卷）（XL)'), ('670283', '盘发'), ('670284', 'z头皮生发护理'), ('670285', 'Z染发 自带产品'), ('910002', '骨缝重构评估'), ('910003', '一对一交流 检测与评估'), ('910004', '体成份检测 评估'), ('910005', '健康讲座门票'), ('WZ162003', 'LCN真甲护理手'), ('WZ162004', 'LCN 真甲护理脚')], max_length=24, null=True),
        ),
        # migrations.AlterField(
        #     model_name='promotionsgroup',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='promotionsgroupdetail',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='serviece',
            name='bodyparts1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('400', '肠道'), ('100', '面部'), ('110', '眼部'), ('230', '背部'), ('300', '肝胆'), ('200', '身体'), ('210', '胸部'), ('220', '腹部'), ('205', '肩颈'), ('240', '腿部')], default='', max_length=128, null=True, verbose_name='身体部位'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='brand',
            field=models.CharField(blank=True, choices=[('223', '马步'), ('193', '富丽活'), ('190', '外包项目'), ('203', '法儿曼'), ('189', '基纳'), ('212', '芳疗个性方案'), ('195', '市场采购'), ('179', '丝维诗兰 swiss line'), ('198', '抗旨君'), ('210', '美芾美源'), ('196', '彩护'), ('200', '普洱茶'), ('216', '资生堂'), ('183', '仪器辅料'), ('207', '礼品'), ('218', '酒水'), ('197', '托宁'), ('181', '云南特色'), ('215', '诗泽'), ('209', '罗正杰'), ('202', '水岸渔歌'), ('225', '悦历'), ('105', '其他'), ('106', '12C'), ('107', '自研品牌'), ('108', '奥丽肤'), ('109', '珈纳'), ('110', 'Amala雅蔓兰'), ('111', '瑞妍'), ('112', '伊人专属'), ('117', '光学'), ('123', '托尼盖'), ('124', '戴安娜/凝肌'), ('126', '雍卡'), ('127', '药拓'), ('128', '吉备'), ('129', '晓酵素'), ('131', '蒂克'), ('133', '肌肤丽琦 GEMOLOGY'), ('137', '谷胱甘肽'), ('138', '美齿口'), ('139', '身体的辅助'), ('143', '小懒肉'), ('145', '胸部'), ('147', '懒虫'), ('154', '店内消耗品'), ('163', '丁航尧'), ('164', '李泽晨'), ('224', '攥住')], max_length=16, null=True, verbose_name='品牌'),
        ),
        # migrations.AlterField(
        #     model_name='serviece',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass1',
            field=models.CharField(blank=True, choices=[('80', '储值卡'), ('60', '造型'), ('106', '12C'), ('110', 'Amala雅蔓兰'), ('108', '奥丽肤'), ('196', '彩护'), ('124', '戴安娜/凝肌'), ('131', '蒂克'), ('154', '店内消耗品'), ('163', '丁航尧'), ('203', '法儿曼'), ('212', '芳疗个性方案'), ('193', '富丽活'), ('137', '谷胱甘肽'), ('117', '光学'), ('133', '肌肤丽琦 GEMOLOGY'), ('189', '基纳'), ('128', '吉备'), ('109', '珈纳'), ('218', '酒水'), ('198', '抗旨君'), ('147', '懒虫'), ('207', '礼品'), ('164', '李泽晨'), ('209', '罗正杰'), ('138', '美齿口'), ('210', '美芾美源'), ('200', '普洱茶'), ('105', '其他'), ('111', '瑞妍'), ('215', '诗泽'), ('195', '市场采购'), ('202', '水岸渔歌'), ('179', '丝维诗兰 swiss line'), ('123', '托尼盖'), ('197', '托宁'), ('190', '外包项目'), ('129', '晓酵素'), ('145', '胸部'), ('127', '药拓'), ('183', '仪器辅料'), ('126', '雍卡'), ('181', '云南特色'), ('216', '资生堂'), ('107', '自研品牌'), ('90', '其它'), ('82', '疗程卡'), ('10', '面部'), ('83', '时效卡'), ('81', '产品卡'), ('20', '身体')], default='', max_length=16, null=True, verbose_name='显示分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('40', '懒虫美睫'), ('50', '无妆感丰眉'), ('60', '无妆感厘睫'), ('70', '懒虫美发'), ('10', '全套服务'), ('30', '懒虫美甲'), ('20', '单加项')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
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
            field=models.CharField(blank=True, choices=[('C', 'C:瘦狗项目'), ('B', 'B:金牛项目'), ('D', 'D:问题项目'), ('A', 'A:明星项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法一）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='marketclass2',
            field=models.CharField(blank=True, choices=[('C', 'C:合作项目'), ('A', 'A:基础项目'), ('D', 'D:医美'), ('B', 'B:大项目')], default='', max_length=16, null=True, verbose_name='项目营销分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='topcode',
            field=models.CharField(blank=True, choices=[('200', '不折扣'), ('301', '懒虫美发'), ('100', '按会员卡折扣')], db_column='TOPCODE', max_length=16, null=True, verbose_name='服务销售折扣分类'),
        ),
        # migrations.AlterField(
        #     model_name='servieceprice',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='srvrptype',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='srvtopty',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='supplier',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='team',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='useright',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='vip',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='vipinformationitemlist',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
        # migrations.AlterField(
        #     model_name='wharehouse',
        #     name='company',
        #     field=models.CharField(blank=True, default='yiren', editable=False, max_length=8, null=True, verbose_name='公司'),
        # ),
    ]
