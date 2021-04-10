# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2021-04-05 14:35
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0034_auto_20210330_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crmcase',
            name='ecodelist',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('20083', '赵爽'), ('14041', '商佳男'), ('14038', '赵文格'), ('18063', '张晗'), ('20088', '王晨洁'), ('06017', '杨芳'), ('17057', '任宇杰'), ('19077', '高小惠'), ('02011', '马欣欣'), ('19073', '化宜荣'), ('04014', '李欣'), ('18062', '付翠芝'), ('10031', '王丽玮'), ('15046', '郭甜'), (None, None), ('17054', '王玉英'), ('02010', '刘金凤'), ('20091', '刘晓花'), ('18060', '袁建爽'), ('13035', '冯立英'), ('18066', '白陆娥'), ('20086', '贾丰华'), ('07024', '李百灵'), ('06018', '林金丽'), ('19079', '牟胜楠'), ('11034', '张可辉'), ('01008', '岳爱瑞'), ('97003', '何秀英'), ('14039', '蒋丽芳'), ('00005', '冯学英'), ('17059', '刘鹏'), ('95001', '孔强'), ('21095', '彭爱容'), ('18065', '贺彩彩'), ('20089', '李瑞华'), ('08027', '王鸿达'), ('15044', '刘娜'), ('20092', '张文青'), ('07021', '艾婷婷'), ('19076', '胡叶茹'), ('18067', '邢翠华'), ('17058', '李秀燕'), ('20090', '秦林佳'), ('09029', '杨忠辉'), ('18068', '邢翠霞'), ('18064', '李琦'), ('20084', '潘春跃'), ('15043', '李佳'), ('15042', '郭浩'), ('18069', '戴晓霞'), ('16050', '王福丽'), ('19075', '梁佳棋'), ('16049', '史晓蓉'), (None, None), ('05016', '孙丽思'), ('10030', '李春玲'), ('11033', '赵萍'), ('05015', '牛红玉'), ('19074', '雷欣茹'), ('20085', '赵红红'), ('17056', '赵霞'), ('20093', '杨娜'), ('15045', '黄静思'), ('20081', '高鑫瑞'), ('04013', '胡蝶'), ('18061', '李福珍'), ('20087', '张蔚'), ('97004', '齐红丽'), ('11032', '崔小芳'), ('', None), ('05015', '牛红玉'), ('16051', '陈晓菲'), ('14037', '王红阳'), ('07025', '王莉'), ('16052', '李婷婷'), ('16048', '王艳艳'), ('18072', '张琳'), ('13036', '李志爽'), ('06020', '刘立飞'), ('07022', '潘玉兰'), ('03012', '雷云飞'), ('19078', '于盼盼'), ('16047', '孙国新'), ('20094', '席瑞媛'), ('08028', '荀玉洁'), ('00006', '张玉梅'), ('17055', '娄变红'), ('20082', '黄秋萍'), ('02009', '王金莲'), ('00007', '孙丽荣'), ('20080', '姜雨馨'), ('08026', '张洛宁'), ('17053', '李金玲')], max_length=550, null=True, verbose_name='责任员工'),
        ),
    ]