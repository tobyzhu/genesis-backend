

reportsql1= " select b.storecode '门店', b.vcode '会员号', b.vname '姓名', b.mtcode '手机', b.viptype '客户类型', b.viplevel '会员级别',b.indate '入会日期', b.birth '生日', "\
            "     max(cardname) '卡项',GetVCODEdate(b.company,b.storecode,b.uuid,'lastindate') '最后到店日期',sum(Intimes) '进店次数', "\
            "     getemplinfo(b.company,b.ecode,'ename') '专属顾问',  getemplinfo(b.company,b.ecode2,'ename') '专属护理师', "\
            "     a.class1 '分类1', a.class2 '分类2', sum(consumeqty) '消费次数', sum(consumeamount) '消费金额', sum(gconsumeamount) '商品金额',  "\
            "     sum(leftqty) '疗程剩余次数', sum(timesleftmoney) '疗程剩余金额', sum(amountleftmoney) '储值剩余金额', sum(cashamount) '现金类支付' "\
            " from ( "\
            "     select a.vipuuid, count(distinct vsdate) intimes, '' cardname, "\
            "         GetAppoptionValue(b.company,'displayclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass1',b.company)) class1,  "\
            "         GetAppoptionValue(b.company,'displayclass2',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass2',b.company)) class2,  "\
            "         sum(b.s_qty) consumeqty, sum(b.s_mount *(b.cardratio+b.cashratio)) consumeamount,  "\
            "         0 gconsumeamount,  "\
            "         0 leftqty, 0 timesleftmoney, 0 amountleftmoney, 0 cashamount "\
            "     from expvstoll a, expense b "\
            "     where 1=1 "\
            "     and a.flag='Y' and b.flag='Y'  and a.valiflag='Y' "\
            "    and a.company=b.company  "\
            "    and a.company='yiren' "\
            "    and a.uuid=b.transuuid  "\
            "    and a.vsdate >='20191022' "\
            "	and a.vsdate <='20191130' "\
            "    and b.ttype in ('S') "\
            "    group by a.vipuuid    "\
            "    union all    "\
            "    select a.vipuuid, count(distinct vsdate) intimes,'' cardname, "\
            "        GetAppoptionValue(b.company,'displayclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass1',b.company)) class1,  "\
            "        GetAppoptionValue(b.company,'displayclass2',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass2',b.company)) class2,  "\
            "        0 consumeqty, sum(b.s_mount *(b.cardratio+b.cashratio)) consumeamount,  "\
            "         sum(b.s_mount *(b.cardratio+b.cashratio)) gconsumeamount, "\
            "        0 leftqty, 0 timesleftmoney, 0 amountleftmoney, 0 cashamount "\
            "    from expvstoll a, expense b "\
            "    where 1=1 "\
            "    and a.flag='Y' and b.flag='Y'  and a.valiflag='Y' "\
            "    and a.company=b.company "\
            "    and a.company='yiren' "\
            "    and a.uuid=b.transuuid  "\
            "    and a.vsdate >='20191022' "\
            "	and a.vsdate <='20191130' "\
            "    and b.ttype in ('G') "\
            "    group by a.vipuuid "\
            "    union all "\
            "    select a.vipuuid, 0 intimes,'' cardname, "\
            "        GetAppoptionValue(b.company,'displayclass1',b.displayclass1) class1,  "\
            "        GetAppoptionValue(b.company,'displayclass2', b.displayclass2) class2,  "\
            "        0 consumeqty, 0 consumeamount,        0 gconsumeamount,  "\
            "        sum(a.leftqty) leftqty, sum(a.leftmoney) timesleftmoney, 0 amountleftmoney, 0 cashamount "\
            "    from cardinfo a ,cardtype b "\
            "    where 1=1 "\
            "    and a.flag='Y' and b.flag='Y'  "\
            "    and a.company=b.company  "\
            "    and a.company='yiren' "\
            "    and a.cardtype=b.cardtype "\
            "    and b.suptype in ('20','25') "\
            "    and b.comptype='times' "\
            "    group by a.vipuuid "\
            "    union all "\
            "    select a.vipuuid, 0 intimes, b.cardname , "\
            "        GetAppoptionValue(b.company,'displayclass1',b.displayclass1) class1,  "\
            "        GetAppoptionValue(b.company,'displayclass2', b.displayclass2) class2,  "\
            "        0 consumeqty, 0 consumeamount,        0 gconsumeamount,  "\
            "        0 leftqty,  0 timesleftmoney, sum(a.leftmoney) amountleftmoney , 0 cashamount "\
            "    from cardinfo a ,cardtype b "\
            "    where 1=1 "\
            "    and a.flag='Y' and b.flag='Y'  "\
            "    and a.company=b.company  "\
            "    and a.company='yiren' "\
            "    and a.cardtype=b.cardtype "\
            "    and b.suptype ='10' "\
            "    and b.comptype='amount' "\
            "    group by a.vipuuid    "\
            "    union all "\
            "    select a.vipuuid, 0 intimes,'' cardname, "\
            "        '现金' class1,  "\
            "        '现金' class2,  "\
            "        0 consumeqty, 0 consumeamount,        0 gconsumeamount,  0 leftqty, 0 timesleftmoney, 0 amountleftmoney, sum(b.TOTMOUNT) cashamount "\
            "    from expvstoll a, toll b , paymode p "\
            "    where 1=1 "\
            "    and a.flag='Y' and b.flag='Y' and p.flag='Y' and a.valiflag='Y' "\
            "    and a.company=b.company and a.company=p.company "\
            "    and a.company='yiren' "\
            "    and a.uuid=b.transuuid  "\
            "    and b.pcode=p.pcode "\
            "    and p.iscash ='1' "\
            "    and a.vsdate >='20191022' "\
            "	and a.vsdate <='20191130' "\
            "    group by a.vipuuid       "\
            "   ) a, vip b "\
            " where 1=1 "\
            " and a.vipuuid = b.uuid "\
            " group by b.storecode, b.vcode, b.vname, b.mtcode, b.viptype, b.viplevel, b.indate, b.birth "

#
# select b.storecode '门店', b.vcode '会员号', b.vname '姓名', b.mtcode '手机号', b.viptype '客户类型',
# 	b.viplevel '会员级别', b.indate '入会日期',  b.birth '生日',GetVCODEdate(b.company,b.storecode,b.vcode,'lastindate') '最后到店日期',
# 	b.ecode '负责顾问', getemplinfo(b.company,b.ecode,'ename') '顾问姓名', b.ecode2 '美容师', getemplinfo(b.company,b.ecode2,'ename') '美容师姓名',
#     a.class1 , a.class2, sum(consumeqty) '消费次数', sum(consumeamount) '消费金额',
# 	sum(leftqty) '疗程剩余次数', sum(timesleftmoney) '疗程剩余金额', sum(amountleftmoney) '储值剩余金额'
# from (
#
# 	select a.vipuuid,
# 		GetAppoptionValue(b.company,'displayclass1',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass1',b.company)) class1,
# 		GetAppoptionValue(b.company,'displayclass2',F_GetItemInfobysrvcode(b.srvcode,b.ttype,'displayclass2',b.company)) class2,
# 		sum(b.s_qty) consumeqty, sum((case b.stype when 'N' then b.s_mount else 0 end )) consumeamount, 0 leftqty, 0 timesleftmoney, 0 amountleftmoney
# 	from expvstoll a, expense b
# 	where 1=1
# 	and a.flag='Y' and b.flag='Y'  and a.valiflag='Y'
# 	and a.company=b.company
# 	and a.company='yfy'
# 	and a.uuid=b.transuuid
# 	and a.vsdate >='20190610'
# 	and a.vsdate <='20191210'
# 	and b.ttype in ('S','G')
# 	group by a.vipuuid
#
# 	union all
#
# 	select a.vipuuid,
# 		GetAppoptionValue(b.company,'displayclass1',b.displayclass1) class1,
# 		GetAppoptionValue(b.company,'displayclass2', b.displayclass2) class2,
# 		0 consumeqty, 0 consumeamount,
# 		sum(a.leftqty) leftqty, sum(a.leftmoney) timesleftmoney, 0 amountleftmoney
# 	from cardinfo a ,cardtype b
# 	where 1=1
# 	and a.flag='Y' and b.flag='Y'
# 	and a.company=b.company
# 	and a.company='yfy'
# 	and a.cardtype=b.cardtype
# 	and b.suptype in ('20','25')
# 	and b.comptype='times'
# 	group by a.vipuuid
#
# 	union all
#
# 	select a.vipuuid,
# 		GetAppoptionValue(b.company,'displayclass1',b.displayclass1) class1,
# 		GetAppoptionValue(b.company,'displayclass2', b.displayclass2) class2,
# 		0 consumeqty, 0 consumeamount,
# 		0 leftqty,  0 timesleftmoney, sum(a.leftmoney) amountleftmoney
# 	from cardinfo a ,cardtype b
# 	where 1=1
# 	and a.flag='Y' and b.flag='Y'
# 	and a.company=b.company
# 	and a.company='yfy'
# 	and a.cardtype=b.cardtype
# 	and b.suptype ='10'
# 	and b.comptype='amount'
#
# 	group by a.vipuuid
# ) a, vip b
# where 1=1
# and a.vipuuid = b.uuid
# group by b.storecode, b.vcode, b.vname, b.mtcode, b.viptype, b.viplevel, b.indate, b.birth,a.class1, a.class2


# SELECT b.storecode '店铺', b.vcode '会员号',b.vname '姓名', b.mtcode '手机',
#  getemplinfo(b.company,b.ecode,'ename') '专属顾问',  getemplinfo(b.company,b.ecode2,'ename') '专属护理师',
#  a.lastindate '最后一次到店日期',
#  GetVCODELEFTMONEY1(b.company,b.storecode, b.vcode,'10')    '主卡余额',GetVCODELEFTMONEY1(b.company,b.storecode, b.vcode,'20')    '附卡余额'
# FROM youlan.yirenvipdate_before20191022 a, vip b
# #update youlan.yirenvipdate_before20191022 a, vip b set a.vipuuid=b.uuid,a.storecode=b.storecode
# where b.company='yiren'
# and trim(a.vipuuid) = trim(b.uuid)
# and a.vipuuid not in (
# 	select vipuuid from expvstoll where 1=1 and valiflag='Y' and company='yiren' and vsdate>='20191022'
#     and ttype in ('G','S')
#     )
# and a.lastindate >='20171215'
#
# union all
#
# select b.storecode, b.vcode,b.vname, b.mtcode,
#  getemplinfo(b.company,b.ecode,'ename') '专属顾问',  getemplinfo(b.company,b.ecode2,'ename') '专属护理师',
#  GetVCODEdate(b.company,b.storecode,b.uuid,'lastindate') lastindate,
#  GetVCODELEFTMONEY1(b.company,b.storecode, b.vcode,'10')    '主卡余额',GetVCODELEFTMONEY1(b.company,b.storecode, b.vcode,'20')    '附卡余额'
#  #sum(if(c.suptype='10',a.leftmoney,0)) leftmoney
# from vip b
# where 1=1
# #and a.company=b.company and a.company=c.company
# #and b.uuid = a.vipuuid and a.cardtype = c.cardtype
# and b.company='yiren'
# and b.uuid in (
# 	select distinct vipuuid from expvstoll where 1=1 and valiflag='Y' and company='yiren' and vsdate>='20191022'
#     and ttype in ('G','S') )
# group by b.storecode,b.uuid


# 新客数据
# select  a.storecode '门店', GetAppoptionValue(a.company,'source',a.source) '来店渠道', a.vsdate '首次到店日期',
# 	a.vcode '会员号',a.vname '姓名', a.viptype '客户类型', a.cashamount '现金额',
# 	b.cardname '卡类',date_format(b.create_time,'%Y%m%d') '售卡日期',  b.leftmoney '余额', b.leftqty '余次', pmname '销售顾问', secname '第二销售人'
# from (
# 	select a.company, a.storecode, a.vipuuid, v.source, a.vsdate, v.vcode,v.vname, v.viptype, sum(b.S_MOUNT*b.cashratio) cashamount,
# 		Getemplinfo(b.company,b.PMCODE,'ename') pmname,		Getemplinfo(b.company,b.assCODE1,'ename') secname
# 	from expvstoll a, expense b, vip v
# 	where 1=1
# 	and a.valiflag='Y' and a.oldcustflag='1'
# 	and a.company='yiren'
# 	and a.vsdate>='20191022'
# 	and a.vsdate<='20191130'
# 	and a.company=b.company  and a.company=v.company
# 	and a.uuid=b.transuuid and a.vipuuid=v.uuid
# 	group by a.vipuuid ) a right outer join
#     (
# 		select c.vipuuid, c.create_time, d.cardname, c.leftmoney, c.leftqty
# 	from  cardinfo c, cardtype d, vip v
# 	where 1=1
# 	and v.company='yiren' and c.stype='N'
# 	and v.create_time>='2019-10-22'
# 	and v.create_time<='2019-11-30'
# 	and v.company=c.company  and v.company=d.company
# 	and v.uuid=c.vipuuid and c.cardtype = d.cardtype
#
#     ) b
# on a.vipuuid = b.vipuuid

# yiren ribao
# select a.storecode, '1-当天实耗' itemname, sum((case b.ttype when 'S' then b.s_mount when 'G' then b.s_mount else 0 end )*(b.cashratio+b.cardratio)) amount
# from expvstoll a, expense b
# where 1=1
# and a.flag='Y' and b.flag='Y' and a.valiflag='Y'
# and a.company=b.company
# and a.uuid =b.transuuid
# and a.company='yiren'
# and a.vsdate ='20191222'
# group by a.storecode
#
# union all
# select a.storecode, '1-当月实耗累计' itemname, sum((case b.ttype when 'S' then b.s_mount when 'G' then b.s_mount else 0 end )*(b.cashratio+b.cardratio)) amount
# from expvstoll a, expense b
# where 1=1
# and a.flag='Y' and b.flag='Y' and a.valiflag='Y'
# and a.company=b.company
# and a.uuid =b.transuuid
# and a.company='yiren'
# and a.vsdate like '201912%'
# group by a.storecode
#
# union all
#
# select a.storecode, '1-当天资金收入' itemname, sum( b.s_mount*b.cashratio) amount
# from expvstoll a, expense b
# where 1=1
# and a.flag='Y' and b.flag='Y' and a.valiflag='Y'
# and a.company=b.company
# and a.uuid =b.transuuid
# and a.company='yiren'
# and a.vsdate ='20191222'
# group by a.storecode
#
# union all
#
# select a.storecode, '1-当月资金收入' itemname, sum( b.s_mount*b.cashratio) amount
# from expvstoll a, expense b
# where 1=1
# and a.flag='Y' and b.flag='Y' and a.valiflag='Y'
# and a.company=b.company
# and a.uuid =b.transuuid
# and a.company='yiren'
# and a.vsdate like '201912%'
# group by a.storecode
#
# union all
#
# select a.storecode, '1-当天到店客数' itemname, sum(a.vipqty + a.friendqty) amount
# from dailyreportvip a
# where 1=1
# and a.flag='Y'
# and a.company='yiren'
# and a.vsdate ='20191222'
# group by a.storecode
#
# union all
#
# select a.storecode, '1-当月到店客数' itemname, sum(a.vipqty + a.friendqty) amount
# from dailyreportvip a
# where 1=1
# and a.flag='Y'
# and a.company='yiren'
# and a.vsdate like '201912%'
# group by a.storecode
#

# union
#
# select a.storecode,'当日新会员',count(distinct a.vipuuid)
# #select a.ccode, b.vcode, b.vname, a.*
# from cardinfo a, vip b, expense c, toll d, paymode p
# where 1=1
# and a.company=b.company and a.company=c.company and a.company =d.company and a.company=p.company
# and a.vipuuid=b.uuid and a.ccode=c.srvcode and c.transuuid =d.transuuid and d.pcode=p.pcode
# and c.ttype ='C' and p.iscash ='1'
# and a.company='yiren'
# and a.storecode='02'
# and date_format(a.create_time,'%Y%m')='20191222'
# and a.ccode like '%-0001'
# and a.vipuuid = b.uuid
# and a.status='O'
# and a.stype ='N'
# and a.leftmoney >00
#
# union
#
# select a.storecode,'当月新会员',count(distinct a.vipuuid)
# #select a.ccode, b.vcode, b.vname, a.*
# from cardinfo a, vip b, expense c, toll d, paymode p
# where 1=1
# and a.company=b.company and a.company=c.company and a.company =d.company and a.company=p.company
# and a.vipuuid=b.uuid and a.ccode=c.srvcode and c.transuuid =d.transuuid and d.pcode=p.pcode
# and c.ttype ='C' and p.iscash ='1'
# and a.company='yiren'
# and a.storecode='02'
# and date_format(a.create_time,'%Y%m')='201912'
# and a.ccode like '%-0001'
# and a.vipuuid = b.uuid
# and a.status='O'
# and a.stype ='N'
# and a.leftmoney >00

# 伊人美容师负责客人消费情况
# SELECT e.storecode, e.ecode, e.ename, e.POSITION, a.total_vipcnt, b.invipcnt, b.inviptimes,
# 	c.self_invipcnt, c.self_inviptimes,b.cashamount, b.samount, b.gamount, b.camount, c.self_samount
# FROM (
# 	select ecode2 ,count(uuid) total_vipcnt
# 	from vip v
# 	where v.company='yiren'
# 	and storecode in ('01','02','03','04')
# 	group by  ecode2
# ) a,
# (
# 	SELECT v.ecode2, count(distinct a.vipuuid ) invipcnt, count(distinct a.vsdate,a.vipuuid) inviptimes,
# 		sum(b.S_MOUNT*b.cashratio) cashamount,
# 		sum(if(b.ttype='S',b.S_MOUNT*(b.cardratio+b.cashratio),0)) samount,
# 		sum(if(b.ttype='G',b.S_MOUNT*(b.cardratio+b.cashratio),0)) gamount,
# 		sum(if( (b.ttype in ('C','I') and getcardsuptype(getcardtype(b.srvcode,b.company),b.company)='20'),b.S_MOUNT*(b.cardratio+b.cashratio),0)) camount
# 	FROM youlan.expvstoll a,expense b, vip v
# 	where 1=1
# 	and a.flag='Y' and b.flag='Y' and v.flag='Y'
# 	and a.valiflag='Y'
# 	and a.company =b.company and a.company=v.company
# 	and a.uuid = b.transuuid
#     and a.company='yiren'
#     and a.storecode in ('01','02','03','04')
# 	and a.vipuuid = v.uuid
# 	and a.vsdate >='20191022'
# 	and a.vsdate <='20200123'
# 	group by v.ecode2
# ) b,
# (
# 	SELECT v.ecode2, count(distinct a.vipuuid ) self_invipcnt, count(distinct a.vsdate, a.vipuuid) self_inviptimes,
# 		sum(if(b.ttype='S',b.S_MOUNT*(b.cardratio+b.cashratio),0)) self_samount
# 	FROM youlan.expvstoll a,expense b, vip v
# 	where 1=1
# 	and a.flag='Y' and b.flag='Y' and v.flag='Y'
# 	and a.valiflag='Y'
# 	and a.company =b.company and a.company=v.company
# 	and a.uuid = b.transuuid
# 	and a.company='yiren'
#     and a.storecode in ('01','02','03','04')
# 	and a.vipuuid = v.uuid
# 	and a.vsdate >='20191022'
# 	and a.vsdate <='20200123'
# 	and ( b.ASSCODE1 = v.ecode2 or b.ASSCODE2 = v.ecode2 )
# 	group by  v.ecode2
# ) c, empl e
# where 1=1
# and a.ecode2 = b.ecode2 and a.ecode2 = c.ecode2 and a.ecode2 = e.ecode
# and e.company='yiren'
# and e.storecode in ('01','02','03','04')
# order by e.storecode, e.ecode


# 伊人 客户分配时使用的数据
# select b.storecode, a.ecode, getemplinfo('yiren', a.ecode, 'ename') ename, a.ecodevcodecnt '该员工服务过的客户数',c.s_amount '服务流水', c.g_amount '商品流水', c.cash_amount '现金流水',
# a.empl_cashamount '该客户员工资金业绩', a.empl_s_normal_amount '该客户员工服务流水(非赠送)', a.empl_s_send_amount
# '该客户员工服务流水(非赠送)', a.empl_g_normal_amount
# '该客户员工商品流水(非赠送)',
# a.empl_g_send_amount
# '该客户员工商品流水(赠送)',
# a.vcode, a.vname, b.ecodecnt
# '服务过的员工数',
# b.normal_s_amount
# '服务非赠送', b.send_s_amount
# '服务赠送', b.normal_g_amount
# '商品非赠送', b.send_g_amount
# '商品赠送', b.cash_amount
# '资金',
# b.pmcode, b.pmname, b.seccode, b.secname
# from
#
# (
#     SELECT
# b.pmcode
# ecode, a.vipuuid, v.vcode, v.vname, count(distinct
# vsdate) ecodevcodecnt,
#         sum(b.S_MOUNT * b.cashratio)
# empl_cashamount,
# sum(case
# b.ttype
# when
# 'S'
# then
# b.S_MOUNT * (b.cardratio + b.cashratio) else 0
# end ) empl_s_normal_amount,
#       sum(case
# b.ttype
# when
# 'S'
# then
# b.S_MOUNT * b.sendratio else 0
# end ) empl_s_send_amount,
#       sum(case
# b.ttype
# when
# 'G'
# then
# b.S_MOUNT * (b.cardratio + b.cashratio) else 0
# end ) empl_g_normal_amount,
#       sum(case
# b.ttype
# when
# 'G'
# then
# b.S_MOUNT * b.sendratio else 0
# end ) empl_g_send_amount
# FROM
# youlan.expvstoll
# a, expense
# b, vip
# v
# where
# 1 = 1
#     and a.valiflag = 'Y'
#                      and a.uuid = b.transuuid
#                                   and a.company = 'yiren'
#                                                   and a.vipuuid = v.uuid
#                                                                   and a.storecode in ('01', '02', '03', '04')
#                                                                   and a.vsdate >= '20191022'
#                                                                   and a.vsdate <= '20200719'
#                                                                   and b.ttype = 'S'
#                                                                                 and length(b.pmcode) > 0
# group
# by
# b.pmcode, a.vipuuid, v.vcode, v.vname
# ) a,
# (
#     SELECT
# v.storecode, a.vipuuid, v.vname, count(distinct if (b.ttype = 'S', b.pmcode, '')) ecodecnt,
#                                                                                   sum( if (
#                                                                                   b.ttype = 'S', b.s_mount, 0)*(
# b.cardratio + b.cashratio)) normal_s_amount,
#                             sum( if (b.ttype = 'S', b.s_mount, 0)*b.sendratio) send_s_amount,
#                                                                                sum( if (b.ttype = 'G', b.s_mount, 0)*(
# b.cardratio + b.cashratio)) normal_g_amount,
#                             sum( if (b.ttype = 'G', b.s_mount, 0)*b.sendratio) send_g_amount,
#                                                                                sum(b.s_mount * b.cardratio)
# cash_amount,
# v.ecode
# pmcode, getemplinfo(v.company, v.ecode, 'ename')
# pmname,
# v.ecode2
# seccode, getemplinfo(v.company, v.ecode2, 'ename')
# secname
# FROM
# youlan.expvstoll
# a, expense
# b, vip
# v
# where
# 1 = 1
#     and a.valiflag = 'Y'
#                      and a.uuid = b.transuuid
#                                   and a.company = 'yiren'
#                                                   and a.vipuuid = v.uuid
#                                                                   and a.storecode in ('01', '02', '03', '04')
#                                                                   and a.vsdate >= '20191022'
#                                                                   and a.vsdate <= '20200719'
#                                                                   and length(b.pmcode) > 0
# group
# by
# v.storecode, a.vipuuid, v.vname
# ) b,
# (
#     SELECT
# b.pmcode
# ecode,
# sum( if (b.ttype = 'S', b.s_mount, 0)) s_amount,
#                                        sum( if (b.ttype = 'G', b.s_mount, 0)) g_amount,
#                                                                               sum(b.s_mount * b.cashratio)
# cash_amount
#
# FROM
# youlan.expvstoll
# a, expense
# b
# where
# 1 = 1
#     and a.valiflag = 'Y'
#                      and a.uuid = b.transuuid
#                                   and a.company = 'yiren'
#                                                   and a.storecode in ('01', '02', '03', '04')
#                                                   and a.vsdate >= '20191022'
#                                                   and a.vsdate <= '20200719'
#                                                   and b.ttype = 'S'
#                                                                 and length(b.pmcode) > 0
# group
# by
# b.pmcode
# ) c
# where
# a.vipuuid = b.vipuuid
# and a.ecode = c.ecode
# order
# by
# b.storecode, a.vcode, a.ecode
#
# ;

