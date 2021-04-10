

# 指定日期到店客人
CRM_SQL101 =    " SELECT uuid,viptype, viplevel, vcode,vname,mtcode,pinyin,birth, ecode,ecode2,source,tags,GetVCODEdate(company,storecode,uuid,'lastindate') lastindate,GetVCODEdate(company,storecode,uuid,'INDATE') indate "\
                " FROM VIP "\
                " WHERE uuid IN ( "\
                "    SELECT VIPUUID "\
                "    FROM expvstoll a "\
                "    where 1=1 and a.flag='Y' and a.valiflag='Y' "\
                "    and a.company=%s and a.storecode in ( %s ) "\
                "    and a.vsdate >= %s "\
                "    and a.vsdate <= %s "\
                "    ) "\
                " and ecode = %s " \
                " order by lastindate desc, vname"

# 指定日期未到店客人
CRM_SQL102 =    " SELECT uuid,viptype, viplevel, vcode,vname,mtcode,pinyin,birth, ecode,ecode2,source,tags ,GetVCODEdate(company,storecode,uuid,'lastindate') lastindate,GetVCODEdate(company,storecode,uuid,'INDATE') indate"\
                " FROM VIP "\
                " WHERE uuid not IN ( "\
                "    SELECT DISTINCT VIPUUID "\
                "    FROM expvstoll a "\
                "    where 1=1 and a.flag='Y' and a.valiflag='Y' "\
                "    and a.company=%s and a.storecode in ( %s ) "\
                "    and a.vsdate >= %s "\
                "    and a.vsdate <= %s "\
                "    ) "\
                " and ecode = %s " \
                " order by lastindate desc,vname"

 # 应到到店客人
CRM_SQL103 = "   select distinct v.uuid,viptype, viplevel, v.vcode,vname,mtcode,pinyin,birth, v.ecode,v.ecode2,source,tags ,GetVCODEdate(v.company,v.storecode,v.uuid,'lastindate') lastindate,GetVCODEdate(v.company,v.storecode,v.uuid,'INDATE') indate "\
             "   from expvstoll a, expense b, vip v "\
             "   where 1=1 "\
             "   and a.flag='Y' and b.flag='Y' and v.flag='Y' and a.valiflag='Y' and v.valiflag='Y' "\
             "   and a.company=b.company "\
             "   and a.uuid = b.transuuid "\
             "   and a.vipuuid = v.uuid "\
             "   and a.company=%s and v.storecode in ( %s ) "\
             "   and b.ttype in ('S') "\
             "   and (date_add(date(a.vsdate), INTERVAL 10 day) between date(%s) and date(%s) )" \
             "   and v.ecode = %s " \
             "   order by lastindate desc,vname"

 # 应补货客人
CRM_SQL104 = "   select distinct v.uuid,viptype, viplevel, v.vcode,vname,mtcode,pinyin,birth, v.ecode,v.ecode2,source,tags ,GetVCODEdate(v.company,v.storecode,v.uuid,'lastindate') lastindate,GetVCODEdate(v.company,v.storecode,v.uuid,'INDATE') indate "\
             "   from expvstoll a, expense b, vip v "\
             "   where 1=1 "\
             "   and a.flag='Y' and b.flag='Y' and v.flag='Y' and a.valiflag='Y' and v.valiflag='Y' "\
             "   and a.company=b.company "\
             "   and a.uuid = b.transuuid "\
             "   and a.vipuuid = v.uuid "\
             "   and a.company=%s and v.storecode in ( %s ) "\
             "   and b.ttype in ('G') "\
             "   and (date_add(date(a.vsdate), INTERVAL 45 day) between date(%s) and date(%s) )" \
             "   and v.ecode = %s " \
             "   order by lastindate desc,vname"

# 卡余额
CRM_SQL105 = "  SELECT a.uuid,viptype, viplevel, a.vcode,vname,mtcode,pinyin,birth, a.ecode,a.ecode2,source,a.tags , " \
             "  GetVCODEdate(a.company,a.storecode,a.uuid,'lastindate') lastindate,GetVCODEdate(a.company,a.storecode,a.uuid,'INDATE') indate, b.leftmoney" \
             "  FROM VIP a, cardinfo b, cardtype d" \
             "  where 1=1 "\
             "   and a.flag='Y' and b.flag='Y' and d.flag='Y' and a.valiflag='Y' "\
             "   and a.company=b.company and a.company=d.company"\
             "   and a.uuid=b.vipuuid"\
             "   and a.company=%s and a.storecode in ( %s ) "\
             "   and b.cardtype=d.cardtype "\
             "   and b.stype='N' "\
             "   and d.suptype between '10' and '19'"\
             "   and b.leftmoney >=%s and b.leftmoney<=%s " \
             "   and a.ecode = %s " \
             "   order by a.vcode "


CRM_SQL108 = "  SELECT a.uuid,viptype, viplevel, a.vcode,vname,mtcode,pinyin,birth, a.ecode,a.ecode2,source,a.tags ,"\
             "        GetVCODEdate(a.company,a.storecode,a.uuid,'lastindate') lastindate,GetVCODEdate(a.company,a.storecode,a.uuid,'INDATE') indate"\
             "   FROM VIP a"\
             "   where 1=1"\
             "   and a.flag='Y'  and a.valiflag='Y' "\
             "   and a.company=%s and a.storecode in ( %s ) "\
             "   and substr(birth,5,4) between substr(%s,5,4) and substr(%s,5,4)" \
             "   and a.ecode = %s " \
             "   order by a.vcode"

CRM_SQL109 = " SELECT v.uuid,v.viptype, viplevel, v.vcode,vname,mtcode,pinyin,birth, v.ecode,v.ecode2,source,v.tags ,"\
             "       GetVCODEdate(v.company,v.storecode,v.uuid,'lastindate') lastindate,GetVCODEdate(v.company,v.storecode,v.uuid,'INDATE') indate"\
             "   FROM VIP v , expvstoll a, toll c, paymode p"\
             "   where 1=1"\
             "   and a.flag='Y' and c.flag='Y'  and a.valiflag='Y' and v.valiflag='Y' and p.flag='Y'"\
             "   and a.company=c.company and a.company=v.company and a.company=p.company"\
             "   and a.uuid=c.transuuid"\
             "   and a.vipuuid = v.uuid"\
             "   and c.pcode =p.pcode"\
             "   and date(v.create_time) = date(a.vsdate)"\
             "   and a.company=%s and a.storecode=%s"\
             "   and (a.vsdate between %s and %s )"\
             "   and p.iscash='1'"\
             "   and c.TOTMOUNT>0" \
             "   and v.ecode = %s " \
             "   order by a.vcode"