# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-15 07:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0116_auto_20191214_2205'),
        ('report', '0013_auto_20191215_0702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report_Item_Ruler',
            fields=[
                ('last_modified', models.DateTimeField(auto_created=True, default=django.utils.timezone.now, editable=False, verbose_name='最后修改时间')),
                ('uuid', models.UUIDField(auto_created=True, blank=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建立时间')),
                ('creater', models.CharField(blank=True, default='anonymous', editable=False, max_length=16, null=True, verbose_name='创建者')),
                ('flag', models.CharField(blank=True, choices=[('Y', '有效'), ('N', '无效')], default='Y', editable=False, max_length=8, null=True, verbose_name='是否删除')),
                ('company', models.CharField(blank=True, default='yfy', editable=False, max_length=8, null=True, verbose_name='公司')),
                ('storecode', models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='门店')),
                ('report_item_ruler_id', models.CharField(blank=True, max_length=16, null=True, verbose_name='报表项计算规则ID')),
                ('report_item_ruler', models.TextField(blank=True, null=True, verbose_name='报表项计算规则')),
            ],
            options={
                'managed': True,
                'verbose_name': 'Genesis报表项次计算',
                'verbose_name_plural': 'Genesis报表项次计算',
                'db_table': 'report_item_ruler',
            },
        ),
        migrations.CreateModel(
            name='ReportClassData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, max_length=16, null=True, verbose_name='公司')),
                ('storecode', models.CharField(blank=True, max_length=16, null=True, verbose_name='门店')),
                ('reportyear', models.CharField(blank=True, max_length=8, null=True, verbose_name='年')),
                ('reportmonth', models.CharField(blank=True, max_length=8, null=True, verbose_name='月')),
                ('reportdate', models.CharField(blank=True, max_length=8, null=True, verbose_name='日期')),
                ('datarang', models.CharField(blank=True, choices=[('daily', '日'), ('month', '月'), ('year', '年'), ('period', '期间')], max_length=16, null=True, verbose_name='数据类型')),
                ('report_class_type', models.CharField(blank=True, choices=[('200', '身体护理'), ('100', '面部护理'), ('储值卡', '储值卡'), ('YP', '药品'), ('XFL', '欣菲聆'), ('EB', 'EB'), ('XM', '禧满'), ('FZC', '法姿纯'), ('YDM', '伊蒂美'), ('JSM', '简诗美'), ('FML', '菲蜜丽'), ('RCYP', '日常用品'), ('HXM', '海皙曼'), ('QZ', '奇致'), ('SS', '手术'), ('BNJSL', '伯纳佳诗丽'), ('SY', '舒颜'), ('SR', '丝柔'), ('YHP', '易耗品'), ('ACWE', '爱驰维尔'), ('JBJS', '吉备酵素'), ('MLTS', '美丽天使'), ('MFMY', '美芾美源'), ('XBYZ', '细胞因子'), ('YDN', '伊杜娜'), ('CD', 'PCD'), ('BOSS', 'BOSS'), ('PCL', 'PCL'), ('GL', '刚伦'), ('PLD', '普拉朵'), ('QSN', '轻奢尼'), ('SH', '赛涵'), ('NM', '南明'), ('SL', '丝丽'), ('XBE', '旭贝尔-精油'), ('ANS', '安娜苏'), ('AEB', '奥尔滨（奥戴尔、奥比虹、FX、傲之美）'), ('BLQ', '贝丽清'), ('BLY', '博兰雅'), ('FEM', '法儿曼'), ('KYY', '科优研'), ('CPQT', '产品其他'), ('XSC', '芯丝翠'), ('LD', '朗顿'), ('BIO', 'BIO'), ('ZP', '赠品'), ('BOTOX', 'BOTOX'), ('NB', 'NB悦碧施'), ('ALW', '艾莉薇'), ('ANBS', '爱努碧斯'), ('ARD', '爱芮达'), ('AGAQ', '安格安晴'), ('AT', '奥肽'), ('BLLBY', '宝龄丽碧雅'), ('RL', '瑞蓝'), ('FSL', '法思丽'), ('FLJ', '菲洛嘉'), ('HW', '海薇'), ('KHT', '坤和堂（和坤堂）'), ('HT', '嗨体'), ('HL', '衡力'), ('JN', '珈纳'), ('JL', '姣兰'), ('JSY', '今生缘（金生缘）'), ('JB', '巨邦'), ('LJ', '朗健'), ('ZCWZX', '乔雅登'), ('RES', '瑞恩诗'), ('RJA', '瑞嘉奥'), ('RSM', '瑞诗美'), ('RBY', '润百颜（润白颜）'), ('RZ', '润致'), ('SM', '双美'), ('SD', '思蒂'), ('TNTL', '肽能天露'), ('WG', '维观'), ('XLK', '修丽可'), ('YMY', '研美颜'), ('YFQ', '伊肤泉'), ('YW', '伊婉'), ('YZQ', '益之泉'), ('YN', '英诺'), ('SMTH', '圣美天合-俞博士'), ('XZY', '雪之莹'), ('RLSM', '蕊丽'), ('LA', 'LA'), ('HSPOW', '韩式POW'), ('ZFX', '泽芙雪'), ('QT', '其他'), ('YKM', '易可美'), ('JX', '金炫'), ('BJP', '保健品'), ('080', '口腔'), ('700', '抗衰'), ('500', '微整形'), ('600', '客装产品'), ('100', '面部'), ('400', '纹绣'), ('144', '面部爱努碧斯'), ('SGZS', '水光注射'), ('KQK', '口腔科'), ('MNB', 'NB悦碧施'), ('ANBS', '爱努碧斯'), ('MA', '傲之美'), ('MAT', '奥肽'), ('LBY', '宝龄丽碧雅'), ('MF', '法儿曼'), ('MJN', '珈纳'), ('MBJC', '面部检测及其他'), ('MM', '面膜类'), ('MQT', 'TAT面部'), ('MW', '面部微科'), ('MX', '其他面部'), ('RJA', '瑞嘉奥'), ('MS', '思蒂'), ('MVG', '维观小分子'), ('XLKM', '修丽可'), ('MV', '眼部微针'), ('ARD', '爱芮达'), ('SJ', '傲之美身体'), ('SJS', '酵素浴'), ('GBKS', '根部抗衰综合调理'), ('STB', '和坤堂臀部瑜珈'), ('STJN', '珈纳身体'), ('BLQJC', '结肠SPA'), ('JSY', '今生缘'), ('SJB', '巨邦'), ('LJ', '朗健健康美塑'), ('SQT', '其他身体'), ('STYZQ', '身体益之泉'), ('SSD', '思蒂身体'), ('TNTL', '肽能·天露'), ('YBS', '俞博士'), ('BHQ', '瘢痕其他'), ('MHB', '面部瘢痕'), ('STH', '身体瘢痕'), ('BBS', '鼻部手术'), ('BBS0', '鼻部美容手术'), ('BBQT', '鼻部其他'), ('ZRT', '鼻部植入体'), ('BG', '鼻骨'), ('BJD', '鼻基底'), ('BJ', '鼻尖'), ('BK', '鼻孔'), ('BXZ', '鼻小柱'), ('BY', '鼻翼'), ('BZG', '鼻中隔'), ('JM', '筋膜移植   -鼻背'), ('QL', '穹窿'), ('QC', '取出'), ('YT', '异体'), ('CBS', '唇部整形'), ('EBS', '耳部整形'), ('FB', '腹壁成型'), ('HX', '环吸减脂塑形'), ('JZQT', '减脂其他'), ('MJZ', '面部减脂塑形'), ('SJZ', '身体减脂塑形'), ('KBQC', '颏部取出'), ('KBZR', '植入体'), ('LXGBS', '脸形改变手术'), ('MFYZ', '毛发移植'), ('MBS', '眉部美容手术'), ('DZB', '面部定制型'), ('JCB', '面部基础版'), ('JQB', '面部加强版'), ('MSH', '面部奢华版'), ('SM', '私密部位'), ('MBCZ', '经典除皱术'), ('ZJDZ', '专家定制'), ('QTZX', '其他整形'), ('QCF', '清创缝合'), ('ZRTQ', '植入体取出'), ('ZSQC', '注射物取出'), ('SMZX', '私密整形手术'), ('MSX', '塑形'), ('XF', '修复'), ('FR', '副乳手术'), ('RFZXS', '乳房下垂 矫正术'), ('LRXF', '隆乳修复术'), ('RGCX', '乳沟成型术'), ('RTJZ', '乳头矫正术'), ('XBZR', '胸部植入体'), ('TS', '雅芳亚隆乳特色技术'), ('YB', '眼部整形'), ('NZ', '内眦'), ('YBSJ', '上睑'), ('TSJJ', '提上睑肌'), ('YZ', '外眦'), ('XJ', '下睑'), ('YBQT', '眼部其他'), ('YBXF', '眼部修复'), ('CJS', '重睑术'), ('YD', '眼袋美容手术'), ('YDZH', '眼袋综合'), ('CLF', '材料费'), ('MZF', '麻醉费'), ('QTJC', '其他术前检查'), ('SQJC', '术前检查费-Ⅰ'), ('CGY', '常规药费'), ('ZYF', '住院护理费'), ('ZCWZX', '注射微整形'), ('WCWZX', '瘦肩针'), ('MZT', '面部自体 脂肪填充'), ('SZT', '身体自体  脂肪填充'), ('ZFJ', '脂肪加购'), ('ZTQT', '自体脂肪填充其他'), ('WX', '纹绣'), ('WXYC', '水晶漂唇'), ('SWM', '水雾眉'), ('WXYJ', '纤绣眼线'), ('CBWX', '唇部纹绣'), ('FJXWX', '发际线纹绣'), ('JJJM', '嫁接睫毛'), ('MBWX', '眉部纹绣'), ('RYWX', '乳晕纹绣'), ('YBWX', '眼部纹绣'), ('BBLJG', '超级平台BBL激光'), ('MG', '激光仪器'), ('YMY', '医疗仪器'), ('CC', '痤疮'), ('PIN', 'PIN'), ('HQSZ', '褐青色痣'), ('HYQ', '黑眼圈'), ('HHB', '黄褐斑'), ('QB', '雀斑'), ('SH', '晒斑'), ('ZY', '脂溢性角化斑'), ('MGXF', '敏感修复'), ('CYTM', '翠玉脱毛'), ('GZTM', '光子冰点脱毛'), ('YGTM', '月光脱毛'), ('MY', '美容仪器'), ('ZL', '激光基本项目'), ('TJ', '胎记'), ('ZSQT', 'ZS其他'), ('HGL', '汗管瘤'), ('JHY', '睑黄疣'), ('PXJS', '皮下结石'), ('SSZ', '色素痣'), ('XGZ', '血管痣'), ('XCY', '寻常疣'), ('ZFL', '脂肪粒'), ('3D', '3D立体晶格提升'), ('PFYH', 'CGF皮肤银行'), ('ZPCLF', '中胚层疗法'), ('LGC', 'Legacy射频仪'), ('VIVA', 'Viva'), ('GXRZ', '光纤溶脂'), ('HJ', '黄金微针'), ('CSD', '极限音波拉皮'), ('KS', '酷塑'), ('MLY', '魔力仪（雅光射频）'), ('OZX', '欧之星'), ('PMY', '皮秒激光'), ('RMJ', '热玛吉'), ('CLY', '射频磁疗仪'), ('SMYQ', '私密仪器'), ('B', 'B：金牛项目'), ('142', '面部珈纳'), ('200', '身体'), ('510', '整形手术'), ('KYY', '科优研'), ('KZCP', '客装产品'), ('C', 'C：瘦狗项目'), ('500', '手术'), ('610', '保健品'), ('080', '口腔科'), ('产品卡', '产品卡'), ('101', '微整形'), ('102', '整形手术'), ('103', '面部思蒂'), ('104', 'NB悦碧施'), ('105', '面部奥尔滨'), ('106', '苹果干细胞'), ('107', '面部雪之莹'), ('108', '面部小分子'), ('109', '面部瑞嘉奥'), ('110', '面部其他'), ('111', '眼部安格安晴'), ('112', '身体巨邦'), ('113', '臀部'), ('114', '结肠'), ('115', '私密'), ('116', 'BIO'), ('117', '今生缘'), ('118', '身体其他'), ('119', '极限音波拉皮'), ('120', '射频'), ('121', '水光'), ('122', '脱毛'), ('123', '白瓷'), ('124', '光子'), ('125', '仪器'), ('126', '其他'), ('127', '纹绣'), ('128', '产品奥尔滨'), ('129', '产品NB悦碧施'), ('130', '产品思蒂'), ('131', '产品瑞嘉奥'), ('132', '产品修丽可'), ('133', '产品法儿曼'), ('134', '产品私密'), ('135', '荷尔蒙贴'), ('136', '产品其他'), ('137', '保健品'), ('138', '无象源'), ('139', '抗衰'), ('140', '口腔'), ('141', '其他'), ('400', '纹绣'), ('A', 'A：特色项目'), ('XBZX', '胸部整形'), ('D', 'D：问题项目'), ('300', '仪器'), ('MBCZS', '面部除皱术'), ('300', '仪器治疗'), ('143', '面部科优研')], max_length=32, null=True, verbose_name='分类')),
                ('report_class_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='分类编码')),
                ('qty', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=16, null=True, verbose_name='数量')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=16, null=True, verbose_name='金额')),
                ('storeuuid', models.ForeignKey(blank=True, db_column='storeuuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='baseinfo.Storeinfo', verbose_name='店铺')),
            ],
            options={
                'managed': True,
                'verbose_name': '每日数据',
                'verbose_name_plural': '每日数据',
                'db_table': 'reportclassdata',
            },
        ),
    ]
