# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-05-07 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0053_auto_20200502_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstransdetail',
            name='gcode',
            field=models.CharField(blank=True, choices=[('10500472', '干胶'), ('10500473', '毛鳞片修护液'), ('10500497', '伊人年历本'), ('10500559', '荷荷芭基础油'), ('10500560', '荷荷芭基础油'), ('10500561', '核桃仁基础油'), ('10500562', '核桃仁基础油'), ('10500563', '甜杏仁基础油'), ('10500564', '甜杏仁基础油'), ('10500565', '小麦胚芽基础油'), ('10500566', '小麦胚芽基础油'), ('10500584', '薰衣草纯露'), ('10500585', '薰衣草护理枕'), ('10500586', '薰衣草舒压枕'), ('10500587', '薰衣草一级棒'), ('10500588', '薰衣草泡泡浴精'), ('10500589', '薰衣草美身保湿乳液'), ('10500590', '薰衣草体香剂'), ('10500591', '薰衣草护手霜'), ('10500592', '婴儿香熏精油'), ('10500593', '婴儿柔软按摩油'), ('10500594', '婴儿舒缓乳液'), ('10500595', '婴儿香皂'), ('10500596', '苦橙茉莉香皂'), ('10500597', '苦橙茉莉清新纯露'), ('10500598', '苦橙茉莉紧实乳液'), ('10500599', '舒缓放松泡泡浴精'), ('10500620', '强效美白精华素（院用）'), ('10500625', 'A40清凉保湿液'), ('10500626', 'Y00紧致多效面膜'), ('10500627', '紧致多效面膜（院用）'), ('10500628', '海藻精华洗面乳(院用）'), ('10500629', '抗氧化化妆水（院用）'), ('10500630', '重塑霜（院用）'), ('10500631', '亚马逊莓洁面乳（院用）'), ('10500632', '亮眼凝胶（院用）'), ('10500636', '电极片-小懒肉1.0护理专用'), ('10500637', '海之蓝烫发水'), ('10500638', '沐寇丹LB1'), ('10500639', '沐寇丹A1'), ('10500640', '沐寇丹A2'), ('10500641', '沐寇丹PAPA'), ('10500642', '俏梦直发膏'), ('10500644', '海星'), ('10500645', 'Agrar骨胶原面膜-德国'), ('10500646', '抗皱紧肤面膜-紫膜'), ('10500647', '紧致精华乳'), ('10500663', '檀香精油'), ('10500664', '熏衣草精油'), ('10500666', '舒缓放松精油（自配）'), ('10500667', '提神醒脑精油（自配）'), ('10500668', '脑部放松精油(自配）'), ('10500670', '裹敷舒缓解压精油（自配）'), ('10500671', '开穴精油（自配）'), ('10500672', '经络精油(自配）'), ('10500673', '乳腺精油（自配）'), ('10500674', '舒缓解压精油（自配）'), ('10500676', '荷尔蒙活力精油（自配）'), ('10500678', '葡萄籽油'), ('10500679', '大厅香薰精油(自配)'), ('10500680', '房间香薰精油(自配)'), ('10500682', '棉片精油'), ('10500701', '新洁尔灭消毒液'), ('10500703', '蓝发泥'), ('10500704', '梵蒂植物精华洁净乳'), ('10500705', '梵蒂植物精华活丽霜'), ('10500706', '梵蒂植物精华焕发露'), ('10500719', '眼睫毛胶水'), ('10500720', '商品抵用金'), ('10500721', '年历本（大）'), ('10500722', '年历本（小）'), ('10500723', '玻尿酸精华'), ('10500724', '瑞葩东方皮雕艺术系列产品 Raepa'), ('10500725', '海藻复合胶原粉末1克*60袋'), ('10500733', '正悦普通眼霜'), ('10500734', '商品补差价'), ('10600728', '12C前驱霜（院装）'), ('10600730', '草本平衡霜-新12C'), ('10600731', '草本平衡霜-新12C 院用'), ('10600734', '蒸馏水'), ('10700746', 'CD处方盘'), ('10700754', '微粒角质粉'), ('10700755', '玫瑰露'), ('10700756', '一次性指套'), ('10700757', '复合紧致精油（自配）'), ('10700758', '净化疏通精油（自配）'), ('10700759', '丰满充盈精油（自配）'), ('10700760', '乳腺管疏通精油'), ('10700761', '肩颈痛沉护理精油'), ('10700762', '胸部营养活化精油'), ('10700763', '肠胃调理精油'), ('10700764', '女性中段护理精油'), ('10700765', '腿部肿胀精油'), ('10700766', '关节精细护理精油'), ('10700769', '百里香精油100ml(自配)'), ('10700770', '葡萄柚精油100ml(自配)'), ('10700772', '春之魅惑1号精油'), ('10700773', '电费'), ('10700774', '精油瓶 ml'), ('10700775', '米奇U盘--16G'), ('10700776', '玛莎踏板式垃圾桶170*26*3KG'), ('10700777', '砧板-2件组24*15*0.5公分和34*24*0.8公分'), ('10700778', '库西娜储物篮3件套180*180'), ('10700779', '木质衣架1*8'), ('10700780', '绒毛猴'), ('10700781', '绿植'), ('10700782', '名片/卡盒'), ('10700783', '口琴'), ('10700784', '小汤锅'), ('10700785', '太阳帽（灰色）'), ('10700786', '丝袜'), ('10700787', '丝巾'), ('10700788', '船袜'), ('10700789', '珈纳旅行套 3支/套'), ('10700790', 'AMALA试用装组合'), ('10700791', '一次性塑料手套'), ('10700793', '茶海-680*470*50'), ('10700794', '茶海-760*550*80'), ('10700811', '茶海-640*600*50'), ('10700817', '烟灰缸-420*250*30'), ('10700833', '茶海-470*330*45'), ('10700839', 'DIY复方精油1#（愉悦）'), ('10700840', 'DIY复方精油2#（舒心）'), ('10700859', '飞来特矿泉水500ml'), ('10700861', '云南小粒咖啡-熟-227g'), ('10700864', '身体1阶护理-舒压精油'), ('10700865', '身体1阶护理-缓解不适精油'), ('10700866', '身体2阶护理-挺胸开肩精油'), ('10800874', '滋养精华素'), ('10800875', '滋养精华素-院用'), ('10800878', '柔和乳液'), ('10800879', '柔和乳液（院用）'), ('10800884', '保湿洗面乳'), ('10800888', '保湿平衡水'), ('10800889', '奥丽肤保湿平衡水（院用）'), ('10800891', '奥丽肤小橄榄油'), ('10800892', '奥丽肤纯橄榄油'), ('10800893', '奥丽肤纯橄榄油(大)'), ('10800894', '奥纯橄榄油(院用)'), ('10800901', '美容液(院用）'), ('10800903', '奥防敏补水面罩'), ('10800904', '奥防敏补水面罩(院用）'), ('10800905', '橄榄浴液'), ('10800908', '紫草保湿霜'), ('10800911', '果汁化妆水'), ('10800912', '紫草根霜'), ('10800915', '保湿化妆水'), ('10800919', '保湿卸妆膏-院'), ('10800920', '滋养保湿洗面乳-乳液型'), ('10800921', '滋养保湿面膜'), ('10800923', '滋养平衡水'), ('10800924', '保湿平衡水'), ('10800925', '紫草保湿霜（院用）'), ('10800926', '紫草保湿霜-700g'), ('10800927', '橄榄角鲨烷'), ('10800928', 'AG美容液'), ('10800929', '奥丽肤柔和洗面乳'), ('10800930', '奥丽肤保湿平衡水'), ('10800931', '奥丽肤保湿面霜'), ('10800932', '柔和卸妆油'), ('10800933', '奥丽肤柔和乳液'), ('10800934', '奥丽肤紫草保湿化妆水 200ml'), ('10800935', '奥丽肤保湿卸妆膏'), ('10800936', '奥丽肤保湿洗面霜'), ('10800937', '奥丽肤保湿洁面乳'), ('10800938', '滋养保湿面膜'), ('10800939', '奥丽肤滋养收敛水'), ('10800940', '奥丽肤滋养平衡水'), ('10800941', '奥丽肤滋养霜'), ('10800942', '奥丽肤美白面膜'), ('10800943', '奥丽肤果汁化妆水250ml'), ('10800944', '紫草保湿化妆水 200ml'), ('10800945', '橄榄倍润洗发水'), ('10800946', '橄榄倍润护发素'), ('10800948', '奥丽肤倍润洗发水 300ml 23周年'), ('10800949', '奥丽肤橄榄滋养洗发水'), ('10800950', '奥丽肤橄榄滋养护发素'), ('10800951', '奥丽肤倍润护发素 300ml 23周年'), ('10800952', '奥丽肤 洁面巾'), ('10800954', '奥丽肤滋养美容液50ml'), ('10900958', '镇静强效补湿面膜2019'), ('10900959', 'KLAPP细胞更生滚轮'), ('10900962', 'KLAPP更新净化乳液'), ('10900963', 'KLAPP更新净化洁面啫喱'), ('10900981', 'KLAPP平皱紧肤面霜'), ('10900982', 'KLAPP平皱紧肤眼霜'), ('10900983', '平皱紧肤精华2019'), ('10900995', 'KLAPP水凝海藻保湿面膜'), ('10900997', 'KLAPP更新净化乳液'), ('10900998', 'KLAPP更新净化洁面啫喱'), ('10900999', 'KLAPP更新净化爽肤水'), ('10901000', 'KLAPP更新净化酵素霜'), ('10901001', '水凝能量活氧精华'), ('10901002', '水凝活肌水氧精华'), ('10901003', '水凝轮廓提升精华'), ('10901004', 'KLAPP镇静强效补湿面膜'), ('10901005', 'KLAPP细胞基因修复乳霜'), ('10901006', 'KLAPP三合一细胞基因再生洁面乳'), ('10901010', 'KLAPP手柄-电动细胞更生微研美针'), ('10901013', '能量活肌修护面霜'), ('10901014', '能量活肌水份面膜'), ('10901016', '963KLAPP亮肌活力面膜（能量活氧面膜）-院用'), ('10901019', '三合一洁面乳'), ('10901020', 'KLAPP细胞基因水分精华'), ('10901021', 'KLAPP细胞基因修复精华'), ('10901022', 'KLAPP细胞基因净白精华'), ('10901023', 'KLAPP细胞基因重组胶原精华'), ('10901024', '细胞基因抗敏精华'), ('10901025', '细胞基因暗疮治愈精华'), ('10901026', 'KLAPP细胞基因再生精华'), ('10901027', 'KLAPP细胞基因再生微针套盒'), ('10901034', '抗皱紧肤眼霜2019'), ('10901035', '2522深海鱼子动感滚珠'), ('10901036', '1542胶原紧致面霜'), ('11001051', '雅蔓兰玲珑美体磨砂啫喱'), ('11001066', 'Amala舒缓洁肤霜'), ('11001067', 'Amala舒缓保湿面霜'), ('11001106', 'Amala荷荷巴按摩油'), ('11001135', 'A纯净磨砂啫喱'), ('11001136', 'A纯净爽肤水'), ('11001137', 'A纯净面膜'), ('11001138', 'A茉莉水润洁肤乳'), ('11001139', '雅蔓兰茉莉保湿面部磨砂霜'), ('11001140', 'A茉莉保湿紧肤水'), ('11001141', 'A茉莉保湿滋润面霜'), ('11001142', 'A茉莉保湿面膜'), ('11001143', 'A保湿润肤油'), ('11001144', 'A茉莉保湿护理眼霜'), ('11001145', 'A茉莉保湿护手霜'), ('11001146', '雅蔓兰茉莉保湿紧肤水'), ('11001147', '雅蔓兰玲珑美体浴盐'), ('11001148', '雅蔓兰玲珑美体沐浴乳'), ('11001149', '雅蔓兰玲珑美体沐浴乳'), ('11001150', '雅蔓兰玲珑美体紧肤精华乳'), ('11001151', '雅蔓兰玲珑美体舒缓精华乳'), ('11001152', '雅蔓兰玲珑美体沐浴乳'), ('11001153', 'A薰衣草舒缓药剂芳香精华'), ('11001154', 'A玫瑰更新药剂芳香精华'), ('11001155', '雅蔓兰薄荷清新精华'), ('11001156', 'A舒缓保湿面霜'), ('11001157', 'A舒缓唇膏'), ('11001158', 'A新生润手霜'), ('11001159', 'A纯净修护精华液'), ('11001160', '雅蔓兰纯净保湿乳霜'), ('11001161', '雅蔓兰茉莉保湿面膜'), ('11001162', '雅蔓兰玲珑美体浴盐'), ('11001163', 'A茉莉保湿奢华礼包-盒装'), ('11001164', 'A再生水疗奢华礼包-盒装'), ('11001165', '雅蔓兰舒缓洁面乳'), ('11101132', '2116.1601赋颜活力面颈膜'), ('11101133', '2217.0303柔颜洁肤乳露'), ('11101134', '21131802弹润丝柔修颜乳00号 30ml'), ('11101166', '2214.1101更新水养膜-升级版'), ('11101170', '851.202浓缩修护晚霜'), ('11101171', '861.401活力修复眼霜'), ('11101174', '921.110调理日霜'), ('11101175', '921.120调理晚霜'), ('11101177', '921.130酵素亮肤霜'), ('11101178', '851.501男性专用面霜'), ('11101182', '851.601身体修护乳'), ('11101183', '410.104活力滋养调理水'), ('11101185', '410.103肌肤调理按摩胶露'), ('11101186', '851.301活力生机霜'), ('11101192', '941.140超活力精纯液-院用'), ('11101194', '941.141超活力精纯液-低敏度-院用'), ('11101195', '971.142强化XT微分子胶原弹力浓缩液'), ('11101196', '971.142强化胶原浓缩液（单支）'), ('11101197', '971.142强化胶原浓缩液-院用'), ('11101198', '971.143白皙XT胶原弹力微分子浓缩液'), ('11101199', '971.143活细胞嫩白素浓缩液-院用'), ('11101206', '活力精纯剂420.106-2018年'), ('11101207', '瑞妍赋颜活力眼霜15ml'), ('11101211', '991.100活细胞导引膜（院用）'), ('11101212', '更新水养膜2238.1101-2018年'), ('11101214', '891.903超敏感按摩霜（院用）'), ('11101218', '420.104酵素亮肤霜（院用）'), ('11101223', '861.403活细胞眼部修复霜'), ('11101224', '861.403眼霜（院）'), ('11101230', '活细胞调理按摩面霜891.903-2018年'), ('11101231', '活细胞活力生机按摩面霜891.303-2018年'), ('11101232', '酵素亮肤霜2238.1701-2018年'), ('11101233', '活细胞強化除皱按摩面霜891.203-2018年'), ('11101234', '活细胞修养防护按摩面霜891.103-2018年'), ('11101235', '活细胞眼部修复霜861.403-2018年'), ('11101236', '活细胞修复手霜891.701-2018年'), ('11101237', '身体修护乳891.601-2018年'), ('11101238', '活细胞身体强化霜891.602-2018年'), ('11101239', '瑞妍肌密金露面霜50ml-2018年'), ('11101240', '瑞妍活力肌蜜金露30ml-2018年'), ('11101241', '420.102活力滋养调理水'), ('11101242', '420.102深层角质水（院用）'), ('11101246', '420.113按摩胶露（院用）'), ('11101247', '肌肤调理按摩胶露420.113-2018年'), ('11101248', '温和卸妆胶露（院）-2018年'), ('11101250', '991.009生机精华液（院用）'), ('11101251', '生机精华液2138.1101-2018年'), ('11101252', '强化XT微分子胶原弹力浓缩液-2018年'), ('11101253', '白皙XT胶原弹力微分子浓缩液-2018年'), ('11101263', '瑞妍盈润弹力美胸霜125ml'), ('11101272', '温和卸妆胶露(院用)'), ('11101273', '2313.1701 眼部活力重建精华 15ml'), ('11101276', '420.198活力精纯剂-院用'), ('11101291', '瑞妍活细胞粉底液1# 30ml'), ('11101297', '2218.1301（洁肤胶露）温和卸妆胶露'), ('11101299', '瑞妍柔颜洁肤乳60mi'), ('11101300', '瑞妍赋颜活力面霜50ml'), ('11101301', '瑞妍紧致美肤霜200ml'), ('11101303', '瑞妍赋颜活力乳液50ml'), ('11101308', '213.993瑞妍手霜150ml'), ('11101309', '瑞妍角质调理水90ml'), ('11101310', '柔澈净化洁肤乳60ml'), ('11101311', '21161401盈润弹力美胸霜100ml'), ('11701309', 'E光胶布'), ('11701310', 'E光感光啫哩'), ('12401319', '戴安娜骨胶原面膜-粉'), ('12401321', '戴安娜骨胶原面膜-绿色'), ('12401322', '戴安娜骨胶原面膜-黄色'), ('12401324', '戴安娜骨胶原面膜-深粉色'), ('12401328', '滋润抗皱液'), ('12401331', '鱼子抗皱滋养精华'), ('12401332', '骨胶原面膜-白色'), ('12401333', 'EPS 骨胶原活化露 800ml'), ('12601338', '植物沐浴香精油(大)'), ('12601339', '植物沐浴香精油(院用)'), ('12601352', '复合海藻矿物盐'), ('12701374', '草本拓-蓝色'), ('12701375', '草本拓-蓝色（院装）'), ('12701376', '草本拓-红色'), ('12701377', '草本拓-红色（院装）'), ('12701378', '草本拓-黄色'), ('12701379', '草本拓-黄色（院装）'), ('12701380', '草本拓-绿色'), ('12701381', '草本拓-绿色（院装）'), ('12701382', '草本拓-紫色'), ('12701383', '草本拓-紫色（院装）'), ('12701384', '局部草本拓-肝气郁血型'), ('12701385', '局部草本拓肝气郁血型-院用'), ('12701386', '局部草本拓--气血不足型'), ('12701387', '局部草本拓-气血不足型-院用'), ('12701390', '方拓-呼吸系统改善'), ('12701391', '方拓-呼吸系统改善-院用'), ('12701392', '方拓-植物神经和内分泌改善'), ('12701393', '方拓-植物神经和内分泌改善-院用'), ('12701394', '方拓-微循环改善'), ('12701395', '方拓-微循环改善-院用'), ('12701396', '方拓-暖宫散寒'), ('12701397', '方拓-暖宫散寒-院用'), ('12701399', '药拓布30*30'), ('12801405', '吉备酵素-浓缩片装'), ('12801406', '吉备酵素礼盒装'), ('12801407', '吉备酵素浓缩精装120g'), ('12801408', '5年吉备精装'), ('12801410', '吉备酵素-2015版900ml'), ('12801411', '吉备酵素-2015版180ml'), ('12801413', '富丽活畅净礼盒'), ('12801415', '新吉备酵素·调'), ('12801416', '吉备酵素精装礼盒 120g*3瓶'), ('12801417', '吉备美膳果冻单支 15g'), ('12801418', '吉备美膳固体饮料I单支 6g'), ('12801419', '吉备美膳固体饮料II单支 6g'), ('12801421', '新樱尚特'), ('12801422', '吉备酵素便携礼盒'), ('12801423', '吉备酵素便携---条'), ('12801426', '吉备美膳果冻 450g'), ('12801427', '吉备美膳固体饮料II'), ('12801428', '吉备美膳固体饮料I'), ('12901429', '寿酵素NeoCal-Ⅱ720ml'), ('12901443', '美优蔬果固体饮料（发酵型） 150克'), ('13101458', '蒂克零负担防晒乳SFP30150ml-18513'), ('13101459', '蒂克玫瑰修护晚霜150ml-86433'), ('13101460', '蒂克玫瑰活肤面膜500ml-86445'), ('13101461', '蒂克玫瑰抗皱按摩霜150ml-86453'), ('13101462', '蒂克玫瑰亮采化妆水500ml-86415'), ('13101463', '蒂克玫瑰净白洗面奶500ml-86405'), ('13101464', '蒂克银杏果酸面膜500ml-86075'), ('13101465', '蒂克老虎草回春洗面奶500ml-86115'), ('13101466', '蒂克老虎草回春晚霜150ml-86143'), ('13101467', '蒂克野玫瑰补水果冻面膜500ml-86185'), ('13101468', '蒂克褐藻亮磨砂霜-脸部150ml-85313'), ('13101469', '蒂克绿泥芦荟面膜500ml-85115'), ('13101470', '蒂克保湿锁水安瓶10x3ml-85248'), ('13101471', '蒂克补水按摩霜1000ml-84016'), ('13101472', '甜杏仁油100ml'), ('13101473', '玫瑰纯露1000ml'), ('13101474', '薰衣草纯露 冷藏1000ml'), ('13101475', '蒂克橙花-单方精油10ml'), ('13101476', '蒂克德国洋甘菊-单方精油10ml'), ('13101477', '蒂克乳香-单方精油10ml'), ('13101478', '蒂克凤梨酵素面膜150ml'), ('13101479', '蒂克 凤梨酵素果冻水面膜500ml-86255'), ('13101480', '蒂克玫瑰亮颜日霜150ml-86423'), ('13101481', '蒂克玫瑰活肤面膜 150ml-86443'), ('13101482', '蒂克玫瑰抚纹眼霜 30ml-86477'), ('13101483', '蒂克玫瑰保湿精华乳30ml-86467'), ('13101484', '蒂克老虎草回春化妆水500ml-86125'), ('13101485', '蒂克老虎草回春日霜150ml-86133'), ('13101486', '蒂克按摩油-肌肉健身1000ml-84116'), ('13101487', '蒂克按摩油-舒压解劳1000ml84126'), ('13101488', '蒂克按摩油-舒筋活络1000ml84146'), ('13101489', '蒂克按摩油-美体轻盈1000ml84176'), ('13101490', '蒂克玫瑰亮颜日霜50ml-1040'), ('13101491', '蒂克玫瑰修护晚霜50ml-1041'), ('13101492', '蒂克玫瑰活肤面膜50ml-11021'), ('13101493', '蒂克玫瑰抚纹眼霜30ml-11037'), ('13101494', '蒂克玫瑰保湿精华乳30ml-1045'), ('13101495', '蒂克玫瑰亮采化妆水200ml-11064'), ('13101496', '蒂克玫瑰嫩白洁肤露200ml-1070'), ('13101497', '蒂克玫瑰护手美甲霜50ml-11177'), ('13101498', '蒂克老虎草回春化妆水200ml-86123'), ('13101499', '蒂克老虎草回春日霜50ml-86131'), ('13101500', '蒂克老虎草回春晚霜50ml-86141'), ('13101501', '蒂克绿泥芦荟面膜150ml-85113'), ('13101502', '蒂克野玫瑰补水果冻面膜（蔷薇补水）150ml-86183'), ('13101503', '蒂克神奇粉刺水-熏衣草晶露100ml-5004'), ('13101504', '蒂克按摩油-舒筋活络100ml-1033'), ('13101505', '蒂克按摩油-美体紧实（肌肉健身）100ml-1030'), ('13101506', '蒂克按摩油-舒压解劳100ml-1031'), ('13101507', '蒂克按摩油-美体轻盈100ml-1035'), ('13101508', '蒂克玫瑰嫩白身体乳200ml-1069'), ('13101509', '蒂克舒压高手动能精油喷雾100ml-18332'), ('13101510', '蒂克紧致匀体霜150ml-83143'), ('13101511', '蒂克热力纤体霜150ml-83033'), ('13101512', '蒂克玫瑰浴盐400g-11161'), ('13101513', '蒂克熏衣草浴盐400g-12611'), ('13101514', '蒂克身體去角質塩（细粒海盐）1000g-83376'), ('13101515', '蒂克多功能婴儿油200ml-18404'), ('13101516', '蒂克防护润肤乳200ml-18414'), ('13101517', '蒂克舒压高手150ml-84043'), ('13101518', '屁屁修护霜Baby cream with vitamin E  50 g-18431'), ('13101519', '蒂克玫瑰浴盐1000g'), ('13101520', '茉莉单方精油 5ml'), ('13101521', '依兰单方精油 5ml'), ('13101522', '檀香单方精油 5ml'), ('13101523', '快乐鼠尾草单方精油 5ml'), ('13101524', '蒂克纤体净化排毒浴盐 100g/袋'), ('13101525', '蒂克补水按摩霜150ml'), ('13301525', '钻石凝时紧致护肤套装'), ('13301526', '珍珠柔滑卸妆乳'), ('13301527', '玫瑰保湿调节露'), ('13301528', '矿物调节洁面泡沫'), ('13301529', '珍珠柔滑磨砂膏'), ('13301530', '矿物莹润修护面膜 50ml'), ('13301531', '净肌平衡面霜 50ml'), ('13301532', '莹润滋养面霜'), ('13301533', '净肌平衡面霜 50ml'), ('13301534', '钻石凝时抗皱面霜'), ('13301535', '钻石凝时抗皱精华乳'), ('13301536', '珍珠柔滑卸妆乳'), ('13301537', '珍珠柔滑磨砂膏'), ('13301538', '矿物调节洁面泡沫'), ('13301539', '莹润滋养面霜'), ('13301540', '矿物莹润修护面膜'), ('13301541', '钻石凝时抗皱面霜'), ('13301542', '赋活按摩油'), ('13301543', '紧致安瓶'), ('13301544', '透白无瑕安瓶'), ('13301545', '面部去皱天然按摩精石'), ('13301546', '亮丽精华液'), ('13301547', '玫瑰保湿调节露'), ('13301548', '矿物身体及面部磨砂膏'), ('13301549', '钻石凝时抗皱精华乳'), ('13301550', '钻石凝时抗皱紧肤面膜'), ('13301551', '钻石凝时抗皱紧肤面膜'), ('13301552', '矿物面部按摩霜'), ('13301553', '钻石凝时抗皱紧致眼霜'), ('13301554', '凝时美白抗皱调节露'), ('13301555', '钻石凝时抗皱眼霜'), ('13301556', '钻石凝时美白抗皱调节露'), ('13301557', '珍珠亮丽身体润肤霜'), ('13301558', 'B5109胶原面膜套装'), ('13701558', '谷胱甘肽-15ML'), ('13701559', '谷胱甘肽靓肤凝胶5ML'), ('13801560', '美白溶液 13ml'), ('13801561', '开口器'), ('13801562', '围兜'), ('13801563', '一次性牙具'), ('14501577', '丰胸1号精油'), ('15401606', '啫喱'), ('15401608', '冰电专用啫喱'), ('15401612', '唇膜'), ('15401614', '海星'), ('15401621', '水疗放松精油'), ('15401623', '细海盐'), ('15401624', '身体乳液'), ('15401630', '美胸膜'), ('15401633', '水氧更新操作头'), ('15401634', '长手膜'), ('15401635', '清新香氛喷雾 100ml'), ('15401636', '舒缓香氛喷雾 100ml'), ('15401637', '提振唤醒精油 3ml'), ('15401638', '舒缓放松精油 3ml'), ('15401639', '体态保养配方精油'), ('15401641', '无纺布浴帽'), ('15401642', '棉棒'), ('15401643', '无纺布'), ('15401645', '脱脂棉'), ('15401646', '小方巾'), ('15401649', '调膜棒'), ('15401650', '浴花'), ('15401651', '一次性纸内裤'), ('15401655', '玻璃调膜碗'), ('15401656', '面膜刷'), ('15401658', '酒精瓶'), ('15401662', '一次性注射器'), ('15401663', '洁厕灵'), ('15401664', '创可贴'), ('15401670', '玉石棒'), ('15401672', '美容镜'), ('15401673', '面膜碗'), ('15401674', '牙刷'), ('15401679', '棉片'), ('15401680', '一次性床单'), ('15401682', '一次性鞋套'), ('15401685', '普通洗发水'), ('15401686', '普通护发素'), ('15401687', '纱布'), ('15401688', '酒精500ml'), ('15401689', '眼睫毛套装'), ('15401690', '眼药水'), ('15401691', '口罩'), ('15401692', '身护笔板刷'), ('15401693', '菊花茶'), ('15401694', '冰糖'), ('15401695', '糖'), ('15401696', '咖啡'), ('15401697', '奶粉'), ('15401698', '环保蜡'), ('15401699', '消毒液'), ('15401700', '卫生巾'), ('15401701', '大卫生纸'), ('15401702', '坐便器纸'), ('15401703', '一次性纸杯'), ('15401704', '浴帽'), ('15401705', '保鲜膜'), ('15401711', '胶皮手套'), ('15401712', '空气清新剂'), ('15401713', '香皂'), ('15401714', '洗手液'), ('15401715', '洗涤灵'), ('15401716', '洗衣粉'), ('15401717', '清洁球'), ('15401718', '米线'), ('15401719', '手抽纸'), ('15401720', '玫瑰茄'), ('15401721', '中药包'), ('15401722', '蜂蜜'), ('15401723', '鸡蛋'), ('15401724', '红酒'), ('15401725', '珍珠粉'), ('15401726', '釉子茶'), ('16301727', '致臻修护洗发水 意大利BORAYA 22周年版'), ('16301728', '致臻控油洗发水 意大利BORAYA 22周年版'), ('16301729', '致臻去屑洗发水 意大利BORAYA 22周年版'), ('16301730', '柔丝顺滑护理霜 意大利BORAYA 22周年版'), ('16301731', '薰衣草洗发露 植物故事 韩国 22周年版'), ('16301732', '橙花防敏感洗发露 植物故事 韩国 22周年版'), ('16301733', '杜松去屑洗发露 植物故事 韩国 22周年版'), ('16301734', '强效护发精华 植物故事 韩国 22周年版'), ('16301735', '舒缓凝乳 植物故事 韩国 22周年版'), ('16301736', '补水发膜 植物故事 韩国 22周年版'), ('16301737', '弹力素 password 22周年版'), ('16301738', '发胶 阿丽德 韩国 22周年版'), ('16301739', '蛋白营养水 阿丽德 韩国 22周年版'), ('16301740', '韩国烫染精华 22周年版'), ('16301741', '卡诗活力胶 卡诗 法国 22周年版'), ('16301742', '防脱精华液 欧莱雅 法国 22周年版'), ('16301743', '强化护理液 欧莱雅 法国 22周年版'), ('16301744', 'LPP烫前染前精华 阿丽德 韩国 22周年版'), ('16401745', 'sink 韩国精华素 150ml 22周年版'), ('16401746', 'silk 精华素 60ml 22周年版'), ('16401747', 'silk 精华素 355ml 22周年版'), ('16401749', '资生堂 发泥 200ml 22周年版'), ('16401750', '资生堂 芳氛头皮护理洗发水 250ml 22周年版'), ('16401751', '资生堂 芳氛头皮护理洗发水 500ml 22周年版'), ('16401752', '资生堂 芳氛头皮护理洗发水 1000ml 22周年版'), ('16401753', '资生堂 芳氛头皮护理护发素 250ml 22周年版'), ('16401754', '资生堂 芳氛头皮护理护发素 500ml 22周年版'), ('16401755', '资生堂 芳氛头皮护理护发素 1000ml 22周年版'), ('16401756', '资生堂 水活修复洗发水 250ml 22周年版'), ('16401757', '资生堂 水活修复洗发水 500ml 22周年版'), ('16401758', '资生堂 水活修复护发素 250ml 22周年版'), ('16401759', '资生堂 水活修复护发素 500ml 22周年版'), ('16401760', '资生堂 水活修复发膜 200g 22周年版'), ('16401761', '资生堂 露蜜焕彩护发素 250g 22周年版'), ('16401762', '资生堂 露蜜焕彩护发素 500g 22周年版'), ('16401763', '资生堂 露蜜焕彩洗发水 250ml 22周年版'), ('16401764', '资生堂 露蜜焕彩洗发水 500ml 22周年版'), ('16401765', '资生堂 露蜜护色臻纯凝露精华素 100ml 22周年版'), ('16401766', '施华寇 发胶 300g 22周年版'), ('16401767', '吹风机 23周年版'), ('16401768', '头皮防护乳 22周年版'), ('16401769', '资生堂露蜜发膜 22周年版'), ('16401770', '资生堂头皮生机洗发水 22周年版'), ('16401771', '资生堂头皮生机洗发水 22周年版'), ('16401772', '资生堂头皮生机护发素 22周年版'), ('16401773', '资生堂头皮生机健康发精华液 22周年版'), ('16401774', '施华蔻 水润平衡保湿露'), ('16401775', '芳氛头皮护理精华露'), ('16401777', '头皮生机健发精华液'), ('16401778', '头皮生机赋活喷雾'), ('16401779', '睫毛滋养精华液'), ('16401780', '芳氛头皮护理精华露'), ('16401781', '芳氛头皮护理清洁啫喱'), ('16401782', '头皮修护乳'), ('16401783', '啫喱 2018年'), ('17900130', '1104温和磨砂膏 75ml'), ('17900131', '1104C温和磨砂膏250ml'), ('17900132', '1111活力滋养舒缓水润面膜 75ml'), ('17900133', '1111C活力滋养舒缓水润面膜250ml'), ('17900135', '1118活力水润亮泽保湿精华乳 30ml'), ('17900136', '1119活力水润凝肌润颜面霜 50ml'), ('17900137', '1119C活力水润凝肌润颜面霜250ml'), ('17900140', '1122活力滋养眼部修护乳霜15ml'), ('17900144', '1124丝柔修颜面霜 50ml'), ('17900145', '1130活力滋养丝柔修颜防晒CC霜SPF45'), ('17900146', '1126活力水润精华液30ml'), ('17900147', '1126c活力水润精华液150ml'), ('17900148', '1148紧容秀颜霜 50ml'), ('17900149', '1149活力青春面膜 50ml'), ('17900151', '1159眼部滋养紧致修护眼霜 7.5 & 15ml'), ('17900155', '1161丝维诗兰丰盈护唇精华液 15ml'), ('17900162', '1166时光紧肤安瓶组 18 x 3ml'), ('17900166', '1177 360°紧致抗皱胶原蛋白精华液 30ml'), ('17900167', '1177C360°紧致抗皱胶原蛋白精华液'), ('17900168', '1178修护焕彩眼膜 30ml'), ('17900169', '1178C修护焕彩眼膜75ml'), ('17900170', '1180丝维诗兰臻颜日夜安瓶组 4 x 12 ml'), ('17900171', '1181紧致抗皱胶原蛋白眼部精华液 15ml'), ('17900172', '1182无暇美肌焕肤液 45ml+60pads'), ('17900173', '1183青春焕颜嫩肌滋润修护面霜 50ml'), ('17900174', '1185夜间塑颜紧致面膜套装 30+35ml'), ('17900175', '1186青春焕颜塑颜紧致修护眼霜'), ('17900176', '1187雪肌奥妙紧肤修护精华液30ml'), ('17900178', '1188眼部紧肤精华液15ml'), ('17900179', '1189雪肌奥妙娇颜新生精华液 150ml'), ('17900180', '1189C雪肌奥妙娇颜新生精华液'), ('17900181', '1192雪肌奥妙奢宠紧致胶原致润面霜50ml'), ('17900182', '1192C雪肌奥妙奢宠紧致胶原致润面霜250ML'), ('17900184', '1403柔丝润肤露 150ml'), ('17900185', '1510订制面霜50ml(臻宠娇颜莹润面霜）'), ('17900186', '1701水之奥妙温和洁面乳 160ml'), ('17900188', '1702水之奥妙舒缓护肤液 160ml'), ('17900189', '1703水之奥妙清爽洁净泡沫 160ml'), ('17900190', '1704水之奥妙清透爽肤水 160ml'), ('17900191', '1704C水之奥妙清透爽肤水500ml'), ('17900196', '1802透白面部及眼部精华液 30ml'), ('17900197', '1803透白紧致修复乳液 50ml'), ('17900200', '1814透白赋活焕颜晚霜  50ml'), ('17900201', '1809轻柔防护乳液SPF50 PA++'), ('17900202', '1810雪肌奥妙透白臻萃精华液  150ml'), ('17900203', '1812透白紧致精华液2X20ml'), ('17900204', '1813透白紧致乳液50ml'), ('17900206', '1815透白细致防护乳液SPF35PA++45ml'), ('17900207', '1815t透白细致防护乳液35 PA++'), ('17900208', '1816透白紧致面膜50ml'), ('17900223', '雪肌奥妙时尚节庆礼盒 5件套'), ('17900224', '雪肌奥妙透系列完美假日礼盒 4件套'), ('17900225', '3465活力水润鲜颜礼盒30ml+50ml'), ('17900226', '3474雪肌奥妙防护礼盒 2件'), ('17900230', '紧致抗皱胶原蛋白精华液 10ml'), ('17900235', '透白细致防护乳液10ML'), ('17900236', '9007光电立体塑颜面膜礼盒 （14片1088C+14片1091C）'), ('17900237', '3D立体塑颜修护面膜 1片'), ('17900238', '胶原面部及颈部面膜 1片'), ('17900247', '1811透亮洁面泡沫160ml'), ('17900248', '1701C温和洁面乳500ml'), ('17900249', '雪肌奥妙赋活明眸礼盒'), ('17900250', '1702C 水之奥妙舒缓护肤液'), ('17900251', '1705C 水之奥妙眼唇卸妆液'), ('17900252', '1037 眼部紧肤修护精华液'), ('17900253', '1191 雪肌奥妙奢宠紧致胶原丰润面霜'), ('17900254', '1510 臻宠娇妍盈润面霜'), ('17900255', '1037C 眼部紧肤修护精华液'), ('17900256', '1040C 按摩柔肤霜'), ('17900260', '1122C 活力滋养眼部修护乳霜'), ('17900261', '1060C 亮肤活颜安瓶'), ('17900262', '1816C透白面膜'), ('17900263', '1191C雪肌奥妙奢宠紧致胶原丰润面霜'), ('17900264', '1811C 透亮洁面泡沫'), ('17900266', '1804C透白细致防护乳液SPF35 PA++'), ('17900267', '1199博睿新肌水光肌底精华20ml'), ('17900268', '1196博睿新肌光耀肌底精华20ml'), ('17900269', '1198博睿亲肌莹亮肌底精华20ml'), ('17900270', '1705水之奥妙眼唇卸妆液100ml'), ('17900271', '1815C透白细致防护乳液150ML'), ('17900272', '3475活力滋养凝润保湿修护套组1122（15ml)+1119(50ml)'), ('17900273', '1124C丝柔修颜面霜250ml'), ('17900274', '1123C活力滋养明眸修护乳霜'), ('17900275', '1161C丰盈护唇精华液150ml'), ('17900276', '1149C活力青春面膜250ml'), ('17900277', '1172C青春修护精华液150ML'), ('17900279', '1094C 保湿活颜安瓶'), ('17900280', '3478 奢宠胶原假日礼盒'), ('17900281', '1186C 青春焕颜塑颜紧致修护眼霜75ML'), ('17900282', '1161T丝维诗兰丰盈护唇精华液 15ml'), ('18100379', '熟普洱 40g'), ('18100380', '云南生态绿茶 50g'), ('18100381', '古树红茶 20g'), ('18100382', '2017年明前景迈小饼茶 100g'), ('18100383', '甜角'), ('18100384', '干笋'), ('18100385', '葛根'), ('18100386', '蜜蒙花'), ('18100387', '七里香'), ('18100388', '红糖粉'), ('18100389', '竹荪-30G'), ('18100390', '奶浆菌'), ('18100391', '玫瑰花'), ('18100392', '胎菊'), ('18100393', '白玛卡'), ('18100394', '桃花'), ('18100395', '小黄姜'), ('18100396', '竹荪-20G(黑盖）'), ('18100397', '三七粉-2瓶/盒'), ('18100398', '三七粉-4瓶/盒'), ('18100399', '三七粉-7瓶/盒'), ('18100400', '天麻粉-2瓶/盒'), ('18100401', '天麻粉-4瓶/盒'), ('18100402', '姜粉'), ('18100403', '松花粉-2瓶/盒'), ('18100404', '特级小青柑 200克/瓶'), ('18100405', '白葱牛肝菌 150克/盒'), ('18100406', '顶级黑枸杞 200克/瓶'), ('18100407', '白藜麦 350克/袋'), ('18100408', '黑藜麦 350克/袋'), ('18100409', '红藜麦 350克/袋'), ('18100410', '三七粉 25克/瓶'), ('18100411', '回心草 20克/瓶'), ('18100412', '虎掌菌 150克/盒'), ('18100413', '金边玫瑰 100克/瓶'), ('18100414', '墨红玫瑰 30克/瓶'), ('18100415', '千叶玫瑰 50克/瓶'), ('18100416', '奇亚籽 350克/袋'), ('18100417', '桑葚 300克/瓶'), ('18100418', '云腿'), ('18100419', '茶化石陈皮礼盒'), ('18100420', '小青柑（盒装） 600g'), ('18100421', '山楂  60g'), ('18100422', '高山苦荞茶'), ('18100423', '玫瑰玉蝴蝶'), ('18100424', '三七粉 25g'), ('18100425', '软籽石榴六个装'), ('18100426', '蒙自石榴十个装（小盒）'), ('18100427', '蒙自石榴8个装（大盒）'), ('18100428', '黄芯猕猴桃'), ('18100429', '象牙芒果 20元/斤'), ('18100431', '精装软籽石榴9个装'), ('18100432', '三七粉礼盒装 40g*6支'), ('18100433', '原味红糖 10粒装'), ('18100434', '小黄姜红糖 10粒装'), ('18100435', '玫瑰花生 500g'), ('18100436', '墨红玫瑰 40g'), ('18100437', '小青柑礼盒 5粒'), ('18100438', '褚橙 4.5公斤'), ('18100439', '滇橄榄干'), ('18100440', '象牙芒果/斤'), ('18100441', '玫瑰花红糖（12粒装）'), ('18100442', '糯米香茶（袋）150G'), ('18100443', '菜籽油鸡枞（开菇）850G'), ('18100444', '野生黑枸杞子（顶级）200G'), ('18100445', '小黄姜红糖（12粒装）'), ('18100446', '火腿菌菇酱300G'), ('18100447', '五年沉香普洱茶沱200G'), ('18100448', '干巴笋'), ('18100449', '干巴笋芽'), ('18100450', '紫糯米'), ('18100451', '小黄糯玉米'), ('18100452', '小花糯玉米'), ('18100453', '有机黄豆'), ('18100454', '有机糯薏仁米'), ('18100455', '野生松茸'), ('18100456', '金银花圆罐茶'), ('18300318', '一次性乳胶手套'), ('18300323', '注射器(5ml)'), ('18300324', '注射器(10ml)'), ('18300325', '医用棉签'), ('18300326', '无菌纱布'), ('18300327', '医用棉球'), ('18300329', '生理盐水'), ('18900098', '基纳 玻尿酸原液HES 2ml*10支'), ('18900099', '基纳 玻尿酸原液HES 2ml*1支'), ('19500108', '沐浴露'), ('19500109', '搓澡巾'), ('19500110', '一次性卫生木桶罩'), ('19500111', '纸膜'), ('19500112', '茶包-眼部'), ('19500113', '长足膜'), ('19500114', '圣诞公仔-24周年庆'), ('19500115', '小小红心'), ('19500116', '调味礼包6件套'), ('19500117', '食物称'), ('19500118', '围度尺'), ('19500119', '玻璃密封罐Havio'), ('19500120', '磨咖啡豆机（EUPA灿坤）'), ('19600283', '丝柔复合精华'), ('19600284', '轻柔矿物粉底液32'), ('19600287', '底妆丝柔精华'), ('19800249', '7日轻断食套餐'), ('19800250', '双周轻断食套餐'), ('19800251', '5号 果蔬谷物餐包 抗旨君'), ('19800252', '2号 果蔬谷物餐包 抗旨君'), ('20000291', '2004年普洱熟茶300g'), ('20000292', '2016年景迈古树生茶饼100g'), ('20300012', '臻白净化面霜50ml'), ('20300013', '蜜润补湿精华液 5ml'), ('20300014', '蜜润补湿霜 15ml'), ('20300015', '更新焕肤面膜(幸福面膜) 15ml'), ('20300016', '净之泉洁肤乳 30ml'), ('20300017', '生命之泉润肤露 30ml'), ('20300018', '修护精华液30 ml'), ('20300019', '水润补湿精华露20ml'), ('20300020', '水润补湿精华乳 30ml'), ('20300021', '蜜润补湿霜50 ml'), ('20300022', '蜜润补湿精华30 ml'), ('20300023', '水润补湿露125ml'), ('20300024', '水润补湿面霜  50ml'), ('20300025', '水润补湿面膜 50ml'), ('20300027', '净之泉洁肤乳125ml'), ('20300029', '生命之泉润肤露 150ml'), ('20300031', '至臻修护露14X3ml-2018'), ('20300032', '防晒修护霜SPF30  50 ml'), ('20300034', '澈净洁肤面膜50ml-2018'), ('20300039', '升效修护液30 ml'), ('20300040', '升效眼唇护理霜15 ml'), ('20300041', '升效日夜保湿霜50 ml'), ('20300042', '升效I号活化霜50 ml'), ('20300043', '升效II号活化霜50 ml'), ('20300044', '更新焕肤面膜50 ml'), ('20300045', '升效护颈营养霜 50ml'), ('20300046', '紧密面霜Ⅲ号50 ml'), ('20300047', '平滑纹理眼胶Ⅰ号15 ml'), ('20300048', '紧致眼霜Ⅱ号15 ml'), ('20300049', '紧密眼霜Ⅲ号15 ml'), ('20300052', '升效修护液 5ml'), ('20300053', '升效日夜保湿霜 15ml'), ('20300054', '冰凝面霜50 ml'), ('20300055', '冰凝眼霜15 ml'), ('20300056', '冰凝精华乳30 ml'), ('20300058', '冰凝眼唇卸妆液60ml-2018'), ('20300060', '冰凝澈净卸妆水125ml-2018'), ('20300062', '水润补湿精华乳125ml-2018'), ('20300063', '蜜润补湿霜100ml'), ('20300064', '蜜润补湿霜100ml-2018'), ('20300066', '蜜润补湿精华125ml-2018'), ('20300068', '水润补湿露500ml-2018'), ('20300070', '水润补湿面霜200ml-2018'), ('20300072', '水润补湿面膜200ml-2018'), ('20300077', '澈净洁肤面膜200ml-2018'), ('20300079', '臻白净化面霜100ml-2018'), ('20300080', '臻白净化面膜200ml'), ('20300082', '升效修护液125ml-2018'), ('20300083', '升效日夜保湿霜100ml'), ('20300085', '升效I号活化霜100ml-2018'), ('20300087', '升效II号活化霜200ml-2018'), ('20300089', '升效眼唇护理霜100ml-2018'), ('20300091', '更新焕肤面膜200ml-2018'), ('20300093', '紧密面霜Ⅲ号200ml-2018'), ('20300095', '紧致眼霜Ⅱ号100ml-2018'), ('20300096', '法儿曼紧致活肤套组'), ('20300097', '705005水润补湿露150ml'), ('20700331', '小公仔'), ('20700333', '黑皮笔记本'), ('20700335', '暖心抱枕-红心'), ('20700351', '尺式放大镜'), ('20900460', '普洱茶'), ('20900464', '2004年百年古树熟普'), ('21000253', '7天净化套盒'), ('21000255', '28天焕能保持套盒'), ('21000256', '35天减脂塑型套盒'), ('21000257', '26天减脂套盒升级版2019年'), ('21000258', '14天减脂套盒'), ('21500457', '单片-诗泽高水分修复面膜'), ('21500458', '诗泽高水份修复面膜 5贴/盒'), ('21800354', '西勒麒麟（红标）波尔多干红葡萄酒'), ('21800355', '雷沃堡之花干红葡萄酒'), ('21800356', '骑士琥珀啤酒'), ('21800357', '骑士珍贵IPA啤酒'), ('21800358', '安东尼庄园干白葡萄酒'), ('21800359', '碧霞谷欢乐烟花起泡葡萄酒'), ('21800360', '碧霞谷欢乐爱恋低醇起泡葡萄酒'), ('21800361', '菲斯特七世桃红葡萄酒'), ('21800362', '菲斯特七世干白葡萄酒'), ('21800363', '奔富麦克斯炫金干红葡萄酒（礼盒）750ml'), ('21800364', '麦格根黑牌珍藏西拉红葡萄酒'), ('22600001', '安娜平衡霜'), ('22700001', '寇瀛胶原蛋白肽饮料500ml'), ('22900001', '男士底裤'), ('22900002', '峰尚美内衣'), ('23000001', 'E1378肌透修护清洁啫喱125ml'), ('23000002', 'E1379肌透修护洁颜乳250ml'), ('23000003', 'E1380肌透修护洁肤水250ml'), ('23000004', 'E1381肌透修护精华30ml'), ('23000005', 'E1382肌透修护莹润霜50ml'), ('23000006', 'E1383肌透修护活力霜50ml'), ('23000007', 'E1384肌透修护盈润霜50ml'), ('23000008', 'E1385肌透修护面膜50ml'), ('23000009', 'E2113焕能紧肤卸妆乳250ml'), ('23000010', 'E2114焕能紧肤爽肤水250ml'), ('23000011', 'E2118紧肤弹嫩水滢霜50ml'), ('23000012', 'E2119焕能紧肤面霜50ml'), ('23000013', 'E2120焕能紧肤滋养霜50ml'), ('23000014', 'E232金水晶美目精华胶囊50粒/瓶'), ('23000015', '双效精华套盒2*20ml')], db_column='gcode', max_length=16, null=True, verbose_name='商品'),
        ),
    ]
