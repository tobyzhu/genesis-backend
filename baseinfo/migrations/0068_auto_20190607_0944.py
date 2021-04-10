# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-06-07 01:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0067_auto_20190606_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardsupertype',
            name='pcode',
            field=models.CharField(blank=True, choices=[('A', '现金'), ('A2', '银联卡'), ('A3', '美团'), ('A4', '记账'), ('A5', '微信'), ('A6', '支付宝'), ('B', '储值卡付'), ('B2', '疗程卡付'), ('B3', '赠送储值卡付'), ('Z1', '赠送'), ('Z2', '优惠券')], max_length=16, null=True, verbose_name='对应付款方式'),
        ),
        migrations.AlterField(
            model_name='cardtype',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('KQK', '口腔科'), ('MNB', 'NB悦碧施'), ('ANBS', '爱努碧斯'), ('MA', '傲之美'), ('MAT', '奥肽'), ('LBY', '宝龄丽碧雅'), ('MF', '法儿曼'), ('MJN', '珈纳'), ('MBJC', '面部检测及其他'), ('MM', '面膜类'), ('MQT', 'TAT面部'), ('MW', '面部微科'), ('MX', '其他面部'), ('RJA', '瑞嘉奥面部'), ('MS', '思蒂'), ('MVG', '维观小分子'), ('XLKM', '修丽可'), ('MV', '眼部微针'), ('ARD', '爱芮达'), ('SJ', '傲之美身体'), ('SJS', '酵素浴'), ('GBKS', '根部抗衰综合调理'), ('STB', '和坤堂臀部瑜珈'), ('STJN', '珈纳身体'), ('BLQJC', '结肠SPA'), ('JSY', '今生缘'), ('SJB', '巨邦'), ('LJ', '朗健健康美塑'), ('SQT', '其他身体'), ('STYZQ', '身体益之泉'), ('SSD', '思蒂身体'), ('TNTL', '肽能·天露'), ('YBS', '俞博士'), ('BHQ', '瘢痕其他'), ('MHB', '面部瘢痕'), ('STH', '身体瘢痕'), ('BBS', '鼻部手术'), ('BBS0', '鼻部美容手术'), ('BBQT', '鼻部其他'), ('ZRT', '鼻部植入体'), ('BG', '鼻骨'), ('BJD', '鼻基底'), ('BJ', '鼻尖'), ('BK', '鼻孔'), ('BXZ', '鼻小柱'), ('BY', '鼻翼'), ('BZG', '鼻中隔'), ('JM', '筋膜移植   -鼻背'), ('QL', '穹窿'), ('QC', '取出'), ('YT', '异体'), ('CBS', '唇部整形'), ('EBS', '耳部整形'), ('FB', '腹壁成型'), ('HX', '环吸减脂塑形'), ('JZQT', '减脂其他'), ('MJZ', '面部减脂塑形'), ('SJZ', '身体减脂塑形'), ('KBQC', '颏部取出'), ('KBZR', '植入体'), ('LXGBS', '脸形改变手术'), ('MFYZ', '毛发移植'), ('MBS', '眉部美容手术'), ('DZB', '面部定制型'), ('JCB', '面部基础版'), ('JQB', '面部加强版'), ('MSH', '面部奢华版'), ('SM', '私密部位'), ('MBCZ', '经典除皱术'), ('ZJDZ', '专家定制'), ('QTZX', '其他整形'), ('QCF', '清创缝合'), ('ZRTQ', '植入体取出'), ('ZSQC', '注射物取出'), ('SMZX', '私密整形手术'), ('MSX', '塑形'), ('XF', '修复'), ('FR', '副乳手术'), ('RFZXS', '乳房下垂 矫正术'), ('LRXF', '隆乳修复术'), ('RGCX', '乳沟成型术'), ('RTJZ', '乳头矫正术'), ('XBZR', '胸部植入体'), ('TS', '雅芳亚隆乳特色技术'), ('YB', '眼部整形'), ('NZ', '内眦'), ('YBSJ', '上睑'), ('TSJJ', '提上睑肌'), ('YZ', '外眦'), ('XJ', '下睑'), ('YBQT', '眼部其他'), ('YBXF', '眼部修复'), ('CJS', '重睑术'), ('YD', '眼袋美容手术'), ('YDZH', '眼袋综合'), ('CLF', '材料费'), ('MZF', '麻醉费'), ('QTJC', '其他术前检查'), ('SQJC', '术前检查费-Ⅰ'), ('CGY', '常规药费'), ('ZYF', '住院护理费'), ('ZCWZX', '注射微整形'), ('WCWZX', '瘦肩针'), ('MZT', '面部自体 脂肪填充'), ('SZT', '身体自体  脂肪填充'), ('ZFJ', '脂肪加购'), ('ZTQT', '自体脂肪填充其他'), ('WX', '纹绣'), ('WXYC', '水晶漂唇'), ('SWM', '水雾眉'), ('WXYJ', '纤绣眼线'), ('CBWX', '唇部纹绣'), ('FJXWX', '发际线纹绣'), ('JJJM', '嫁接睫毛'), ('MBWX', '眉部纹绣'), ('RYWX', '乳晕纹绣'), ('YBWX', '眼部纹绣'), ('BBLJG', '超级平台BBL激光'), ('MG', '激光仪器'), ('YMY', '医疗仪器'), ('CC', '痤疮'), ('PIN', 'PIN'), ('HQSZ', '褐青色痣'), ('HYQ', '黑眼圈'), ('HHB', '黄褐斑'), ('QB', '雀斑'), ('SH', '晒斑'), ('ZY', '脂溢性角化斑'), ('MGXF', '敏感修复'), ('CYTM', '翠玉脱毛'), ('GZTM', '光子冰点脱毛'), ('YGTM', '月光脱毛'), ('MY', '美容仪器'), ('ZL', '激光基本项目'), ('TJ', '胎记'), ('ZSQT', 'ZS其他'), ('HGL', '汗管瘤'), ('JHY', '睑黄疣'), ('PXJS', '皮下结石'), ('SSZ', '色素痣'), ('XGZ', '血管痣'), ('XCY', '寻常疣'), ('ZFL', '脂肪粒'), ('3D', '3D立体晶格提升'), ('PFYH', 'CGF皮肤银行'), ('ZPCLF', '中胚层疗法'), ('LGC', 'Legacy射频仪'), ('VIVA', 'Viva'), ('GXRZ', '光纤溶脂'), ('HJ', '黄金微针'), ('CSD', '极限音波拉皮'), ('KS', '酷塑'), ('MLY', '魔力仪（雅光射频）'), ('OZX', '欧之星'), ('PMY', '皮秒激光'), ('RMJ', '热玛吉'), ('CLY', '射频磁疗仪'), ('SMYQ', '私密仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('KQK', '口腔科'), ('MNB', 'NB悦碧施'), ('ANBS', '爱努碧斯'), ('MA', '傲之美'), ('MAT', '奥肽'), ('LBY', '宝龄丽碧雅'), ('MF', '法儿曼'), ('MJN', '珈纳'), ('MBJC', '面部检测及其他'), ('MM', '面膜类'), ('MQT', 'TAT面部'), ('MW', '面部微科'), ('MX', '其他面部'), ('RJA', '瑞嘉奥面部'), ('MS', '思蒂'), ('MVG', '维观小分子'), ('XLKM', '修丽可'), ('MV', '眼部微针'), ('ARD', '爱芮达'), ('SJ', '傲之美身体'), ('SJS', '酵素浴'), ('GBKS', '根部抗衰综合调理'), ('STB', '和坤堂臀部瑜珈'), ('STJN', '珈纳身体'), ('BLQJC', '结肠SPA'), ('JSY', '今生缘'), ('SJB', '巨邦'), ('LJ', '朗健健康美塑'), ('SQT', '其他身体'), ('STYZQ', '身体益之泉'), ('SSD', '思蒂身体'), ('TNTL', '肽能·天露'), ('YBS', '俞博士'), ('BHQ', '瘢痕其他'), ('MHB', '面部瘢痕'), ('STH', '身体瘢痕'), ('BBS', '鼻部手术'), ('BBS0', '鼻部美容手术'), ('BBQT', '鼻部其他'), ('ZRT', '鼻部植入体'), ('BG', '鼻骨'), ('BJD', '鼻基底'), ('BJ', '鼻尖'), ('BK', '鼻孔'), ('BXZ', '鼻小柱'), ('BY', '鼻翼'), ('BZG', '鼻中隔'), ('JM', '筋膜移植   -鼻背'), ('QL', '穹窿'), ('QC', '取出'), ('YT', '异体'), ('CBS', '唇部整形'), ('EBS', '耳部整形'), ('FB', '腹壁成型'), ('HX', '环吸减脂塑形'), ('JZQT', '减脂其他'), ('MJZ', '面部减脂塑形'), ('SJZ', '身体减脂塑形'), ('KBQC', '颏部取出'), ('KBZR', '植入体'), ('LXGBS', '脸形改变手术'), ('MFYZ', '毛发移植'), ('MBS', '眉部美容手术'), ('DZB', '面部定制型'), ('JCB', '面部基础版'), ('JQB', '面部加强版'), ('MSH', '面部奢华版'), ('SM', '私密部位'), ('MBCZ', '经典除皱术'), ('ZJDZ', '专家定制'), ('QTZX', '其他整形'), ('QCF', '清创缝合'), ('ZRTQ', '植入体取出'), ('ZSQC', '注射物取出'), ('SMZX', '私密整形手术'), ('MSX', '塑形'), ('XF', '修复'), ('FR', '副乳手术'), ('RFZXS', '乳房下垂 矫正术'), ('LRXF', '隆乳修复术'), ('RGCX', '乳沟成型术'), ('RTJZ', '乳头矫正术'), ('XBZR', '胸部植入体'), ('TS', '雅芳亚隆乳特色技术'), ('YB', '眼部整形'), ('NZ', '内眦'), ('YBSJ', '上睑'), ('TSJJ', '提上睑肌'), ('YZ', '外眦'), ('XJ', '下睑'), ('YBQT', '眼部其他'), ('YBXF', '眼部修复'), ('CJS', '重睑术'), ('YD', '眼袋美容手术'), ('YDZH', '眼袋综合'), ('CLF', '材料费'), ('MZF', '麻醉费'), ('QTJC', '其他术前检查'), ('SQJC', '术前检查费-Ⅰ'), ('CGY', '常规药费'), ('ZYF', '住院护理费'), ('ZCWZX', '注射微整形'), ('WCWZX', '瘦肩针'), ('MZT', '面部自体 脂肪填充'), ('SZT', '身体自体  脂肪填充'), ('ZFJ', '脂肪加购'), ('ZTQT', '自体脂肪填充其他'), ('WX', '纹绣'), ('WXYC', '水晶漂唇'), ('SWM', '水雾眉'), ('WXYJ', '纤绣眼线'), ('CBWX', '唇部纹绣'), ('FJXWX', '发际线纹绣'), ('JJJM', '嫁接睫毛'), ('MBWX', '眉部纹绣'), ('RYWX', '乳晕纹绣'), ('YBWX', '眼部纹绣'), ('BBLJG', '超级平台BBL激光'), ('MG', '激光仪器'), ('YMY', '医疗仪器'), ('CC', '痤疮'), ('PIN', 'PIN'), ('HQSZ', '褐青色痣'), ('HYQ', '黑眼圈'), ('HHB', '黄褐斑'), ('QB', '雀斑'), ('SH', '晒斑'), ('ZY', '脂溢性角化斑'), ('MGXF', '敏感修复'), ('CYTM', '翠玉脱毛'), ('GZTM', '光子冰点脱毛'), ('YGTM', '月光脱毛'), ('MY', '美容仪器'), ('ZL', '激光基本项目'), ('TJ', '胎记'), ('ZSQT', 'ZS其他'), ('HGL', '汗管瘤'), ('JHY', '睑黄疣'), ('PXJS', '皮下结石'), ('SSZ', '色素痣'), ('XGZ', '血管痣'), ('XCY', '寻常疣'), ('ZFL', '脂肪粒'), ('3D', '3D立体晶格提升'), ('PFYH', 'CGF皮肤银行'), ('ZPCLF', '中胚层疗法'), ('LGC', 'Legacy射频仪'), ('VIVA', 'Viva'), ('GXRZ', '光纤溶脂'), ('HJ', '黄金微针'), ('CSD', '极限音波拉皮'), ('KS', '酷塑'), ('MLY', '魔力仪（雅光射频）'), ('OZX', '欧之星'), ('PMY', '皮秒激光'), ('RMJ', '热玛吉'), ('CLY', '射频磁疗仪'), ('SMYQ', '私密仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='item',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('KQK', '口腔科'), ('MNB', 'NB悦碧施'), ('ANBS', '爱努碧斯'), ('MA', '傲之美'), ('MAT', '奥肽'), ('LBY', '宝龄丽碧雅'), ('MF', '法儿曼'), ('MJN', '珈纳'), ('MBJC', '面部检测及其他'), ('MM', '面膜类'), ('MQT', 'TAT面部'), ('MW', '面部微科'), ('MX', '其他面部'), ('RJA', '瑞嘉奥面部'), ('MS', '思蒂'), ('MVG', '维观小分子'), ('XLKM', '修丽可'), ('MV', '眼部微针'), ('ARD', '爱芮达'), ('SJ', '傲之美身体'), ('SJS', '酵素浴'), ('GBKS', '根部抗衰综合调理'), ('STB', '和坤堂臀部瑜珈'), ('STJN', '珈纳身体'), ('BLQJC', '结肠SPA'), ('JSY', '今生缘'), ('SJB', '巨邦'), ('LJ', '朗健健康美塑'), ('SQT', '其他身体'), ('STYZQ', '身体益之泉'), ('SSD', '思蒂身体'), ('TNTL', '肽能·天露'), ('YBS', '俞博士'), ('BHQ', '瘢痕其他'), ('MHB', '面部瘢痕'), ('STH', '身体瘢痕'), ('BBS', '鼻部手术'), ('BBS0', '鼻部美容手术'), ('BBQT', '鼻部其他'), ('ZRT', '鼻部植入体'), ('BG', '鼻骨'), ('BJD', '鼻基底'), ('BJ', '鼻尖'), ('BK', '鼻孔'), ('BXZ', '鼻小柱'), ('BY', '鼻翼'), ('BZG', '鼻中隔'), ('JM', '筋膜移植   -鼻背'), ('QL', '穹窿'), ('QC', '取出'), ('YT', '异体'), ('CBS', '唇部整形'), ('EBS', '耳部整形'), ('FB', '腹壁成型'), ('HX', '环吸减脂塑形'), ('JZQT', '减脂其他'), ('MJZ', '面部减脂塑形'), ('SJZ', '身体减脂塑形'), ('KBQC', '颏部取出'), ('KBZR', '植入体'), ('LXGBS', '脸形改变手术'), ('MFYZ', '毛发移植'), ('MBS', '眉部美容手术'), ('DZB', '面部定制型'), ('JCB', '面部基础版'), ('JQB', '面部加强版'), ('MSH', '面部奢华版'), ('SM', '私密部位'), ('MBCZ', '经典除皱术'), ('ZJDZ', '专家定制'), ('QTZX', '其他整形'), ('QCF', '清创缝合'), ('ZRTQ', '植入体取出'), ('ZSQC', '注射物取出'), ('SMZX', '私密整形手术'), ('MSX', '塑形'), ('XF', '修复'), ('FR', '副乳手术'), ('RFZXS', '乳房下垂 矫正术'), ('LRXF', '隆乳修复术'), ('RGCX', '乳沟成型术'), ('RTJZ', '乳头矫正术'), ('XBZR', '胸部植入体'), ('TS', '雅芳亚隆乳特色技术'), ('YB', '眼部整形'), ('NZ', '内眦'), ('YBSJ', '上睑'), ('TSJJ', '提上睑肌'), ('YZ', '外眦'), ('XJ', '下睑'), ('YBQT', '眼部其他'), ('YBXF', '眼部修复'), ('CJS', '重睑术'), ('YD', '眼袋美容手术'), ('YDZH', '眼袋综合'), ('CLF', '材料费'), ('MZF', '麻醉费'), ('QTJC', '其他术前检查'), ('SQJC', '术前检查费-Ⅰ'), ('CGY', '常规药费'), ('ZYF', '住院护理费'), ('ZCWZX', '注射微整形'), ('WCWZX', '瘦肩针'), ('MZT', '面部自体 脂肪填充'), ('SZT', '身体自体  脂肪填充'), ('ZFJ', '脂肪加购'), ('ZTQT', '自体脂肪填充其他'), ('WX', '纹绣'), ('WXYC', '水晶漂唇'), ('SWM', '水雾眉'), ('WXYJ', '纤绣眼线'), ('CBWX', '唇部纹绣'), ('FJXWX', '发际线纹绣'), ('JJJM', '嫁接睫毛'), ('MBWX', '眉部纹绣'), ('RYWX', '乳晕纹绣'), ('YBWX', '眼部纹绣'), ('BBLJG', '超级平台BBL激光'), ('MG', '激光仪器'), ('YMY', '医疗仪器'), ('CC', '痤疮'), ('PIN', 'PIN'), ('HQSZ', '褐青色痣'), ('HYQ', '黑眼圈'), ('HHB', '黄褐斑'), ('QB', '雀斑'), ('SH', '晒斑'), ('ZY', '脂溢性角化斑'), ('MGXF', '敏感修复'), ('CYTM', '翠玉脱毛'), ('GZTM', '光子冰点脱毛'), ('YGTM', '月光脱毛'), ('MY', '美容仪器'), ('ZL', '激光基本项目'), ('TJ', '胎记'), ('ZSQT', 'ZS其他'), ('HGL', '汗管瘤'), ('JHY', '睑黄疣'), ('PXJS', '皮下结石'), ('SSZ', '色素痣'), ('XGZ', '血管痣'), ('XCY', '寻常疣'), ('ZFL', '脂肪粒'), ('3D', '3D立体晶格提升'), ('PFYH', 'CGF皮肤银行'), ('ZPCLF', '中胚层疗法'), ('LGC', 'Legacy射频仪'), ('VIVA', 'Viva'), ('GXRZ', '光纤溶脂'), ('HJ', '黄金微针'), ('CSD', '极限音波拉皮'), ('KS', '酷塑'), ('MLY', '魔力仪（雅光射频）'), ('OZX', '欧之星'), ('PMY', '皮秒激光'), ('RMJ', '热玛吉'), ('CLY', '射频磁疗仪'), ('SMYQ', '私密仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
        migrations.AlterField(
            model_name='serviece',
            name='displayclass2',
            field=models.CharField(blank=True, choices=[('KQK', '口腔科'), ('MNB', 'NB悦碧施'), ('ANBS', '爱努碧斯'), ('MA', '傲之美'), ('MAT', '奥肽'), ('LBY', '宝龄丽碧雅'), ('MF', '法儿曼'), ('MJN', '珈纳'), ('MBJC', '面部检测及其他'), ('MM', '面膜类'), ('MQT', 'TAT面部'), ('MW', '面部微科'), ('MX', '其他面部'), ('RJA', '瑞嘉奥面部'), ('MS', '思蒂'), ('MVG', '维观小分子'), ('XLKM', '修丽可'), ('MV', '眼部微针'), ('ARD', '爱芮达'), ('SJ', '傲之美身体'), ('SJS', '酵素浴'), ('GBKS', '根部抗衰综合调理'), ('STB', '和坤堂臀部瑜珈'), ('STJN', '珈纳身体'), ('BLQJC', '结肠SPA'), ('JSY', '今生缘'), ('SJB', '巨邦'), ('LJ', '朗健健康美塑'), ('SQT', '其他身体'), ('STYZQ', '身体益之泉'), ('SSD', '思蒂身体'), ('TNTL', '肽能·天露'), ('YBS', '俞博士'), ('BHQ', '瘢痕其他'), ('MHB', '面部瘢痕'), ('STH', '身体瘢痕'), ('BBS', '鼻部手术'), ('BBS0', '鼻部美容手术'), ('BBQT', '鼻部其他'), ('ZRT', '鼻部植入体'), ('BG', '鼻骨'), ('BJD', '鼻基底'), ('BJ', '鼻尖'), ('BK', '鼻孔'), ('BXZ', '鼻小柱'), ('BY', '鼻翼'), ('BZG', '鼻中隔'), ('JM', '筋膜移植   -鼻背'), ('QL', '穹窿'), ('QC', '取出'), ('YT', '异体'), ('CBS', '唇部整形'), ('EBS', '耳部整形'), ('FB', '腹壁成型'), ('HX', '环吸减脂塑形'), ('JZQT', '减脂其他'), ('MJZ', '面部减脂塑形'), ('SJZ', '身体减脂塑形'), ('KBQC', '颏部取出'), ('KBZR', '植入体'), ('LXGBS', '脸形改变手术'), ('MFYZ', '毛发移植'), ('MBS', '眉部美容手术'), ('DZB', '面部定制型'), ('JCB', '面部基础版'), ('JQB', '面部加强版'), ('MSH', '面部奢华版'), ('SM', '私密部位'), ('MBCZ', '经典除皱术'), ('ZJDZ', '专家定制'), ('QTZX', '其他整形'), ('QCF', '清创缝合'), ('ZRTQ', '植入体取出'), ('ZSQC', '注射物取出'), ('SMZX', '私密整形手术'), ('MSX', '塑形'), ('XF', '修复'), ('FR', '副乳手术'), ('RFZXS', '乳房下垂 矫正术'), ('LRXF', '隆乳修复术'), ('RGCX', '乳沟成型术'), ('RTJZ', '乳头矫正术'), ('XBZR', '胸部植入体'), ('TS', '雅芳亚隆乳特色技术'), ('YB', '眼部整形'), ('NZ', '内眦'), ('YBSJ', '上睑'), ('TSJJ', '提上睑肌'), ('YZ', '外眦'), ('XJ', '下睑'), ('YBQT', '眼部其他'), ('YBXF', '眼部修复'), ('CJS', '重睑术'), ('YD', '眼袋美容手术'), ('YDZH', '眼袋综合'), ('CLF', '材料费'), ('MZF', '麻醉费'), ('QTJC', '其他术前检查'), ('SQJC', '术前检查费-Ⅰ'), ('CGY', '常规药费'), ('ZYF', '住院护理费'), ('ZCWZX', '注射微整形'), ('WCWZX', '瘦肩针'), ('MZT', '面部自体 脂肪填充'), ('SZT', '身体自体  脂肪填充'), ('ZFJ', '脂肪加购'), ('ZTQT', '自体脂肪填充其他'), ('WX', '纹绣'), ('WXYC', '水晶漂唇'), ('SWM', '水雾眉'), ('WXYJ', '纤绣眼线'), ('CBWX', '唇部纹绣'), ('FJXWX', '发际线纹绣'), ('JJJM', '嫁接睫毛'), ('MBWX', '眉部纹绣'), ('RYWX', '乳晕纹绣'), ('YBWX', '眼部纹绣'), ('BBLJG', '超级平台BBL激光'), ('MG', '激光仪器'), ('YMY', '医疗仪器'), ('CC', '痤疮'), ('PIN', 'PIN'), ('HQSZ', '褐青色痣'), ('HYQ', '黑眼圈'), ('HHB', '黄褐斑'), ('QB', '雀斑'), ('SH', '晒斑'), ('ZY', '脂溢性角化斑'), ('MGXF', '敏感修复'), ('CYTM', '翠玉脱毛'), ('GZTM', '光子冰点脱毛'), ('YGTM', '月光脱毛'), ('MY', '美容仪器'), ('ZL', '激光基本项目'), ('TJ', '胎记'), ('ZSQT', 'ZS其他'), ('HGL', '汗管瘤'), ('JHY', '睑黄疣'), ('PXJS', '皮下结石'), ('SSZ', '色素痣'), ('XGZ', '血管痣'), ('XCY', '寻常疣'), ('ZFL', '脂肪粒'), ('3D', '3D立体晶格提升'), ('PFYH', 'CGF皮肤银行'), ('ZPCLF', '中胚层疗法'), ('LGC', 'Legacy射频仪'), ('VIVA', 'Viva'), ('GXRZ', '光纤溶脂'), ('HJ', '黄金微针'), ('CSD', '极限音波拉皮'), ('KS', '酷塑'), ('MLY', '魔力仪（雅光射频）'), ('OZX', '欧之星'), ('PMY', '皮秒激光'), ('RMJ', '热玛吉'), ('CLY', '射频磁疗仪'), ('SMYQ', '私密仪器')], default='', max_length=16, null=True, verbose_name='显示分类（方法二）'),
        ),
    ]
