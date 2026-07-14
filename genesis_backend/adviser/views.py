#coding=utf-8

from __future__ import unicode_literals
import math
from datetime import datetime,timedelta
from decimal import Decimal
import traceback
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError
import uuid
#from pyecharts import Line3D
import json
import simplejson
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import  pagination,viewsets
from rest_framework.parsers import JSONParser
from django.db import connection
from django.db.models import Count, Q
import json
import pandas as pd
from pandas.io.json import json_normalize
import tablib
from django.core.serializers import serialize
# REMOTE_HOST = "https://pyecharts.github.io/assets/js"

from adviser.models import ExpvstollHung,ExpenseHung,Cardinfo,Bookingevent,Cardinfo,ShoppingCart
from adviser.serializers import BookingeventSerializer,CardinfoSerializer
from baseinfo.models import Serviece,Servieceprice,Goods,Srvtopty,Srvrptype,Goodsct,Vip,Cardtype,Cardsupertype,Empl,Paymode
from cashier.models import EarnestMoney, Expvstoll, Expense, Toll, Cardhistory
import common.constants
from common.models import Sequence


def safe_execute_sql(sql, params):
    """避开 pymysql mogrify 的 % 格式化问题，手动处理参数"""
    from django.db import connection
    escaped = []
    for p in params:
        if p is None:
            escaped.append("NULL")
        elif isinstance(p, str):
            escaped.append("'" + p.replace("'", "''") + "'")
        else:
            escaped.append(str(p))
    for ep in escaped:
        sql = sql.replace('%s', ep, 1)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        list_data = []
        desc = cursor.description
        if desc is None:
            return '[]'
        columns = [col[0] for col in desc]
        for row in cursor.fetchall():
            list_data.append(dict(zip(columns, row)))
        return json.dumps(list_data, cls=DjangoJSONEncoder)

def sql_to_json(sql,params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)

        list_data = []
        desc = cursor.description
        if desc == None:
            return []
        try:
            columns = [col[0] for col in desc]
            for row in cursor.fetchall():
                list_data.append(dict(zip(columns, row)))
            # return cardtypelist

            json_data = json.dumps(list_data,cls=DjangoJSONEncoder)
            # print('json_data',json_data)
            cursor.close()
            connection.close()
            return json_data
        except Exception as e:
            print('sql_to_json error',e)
        return []


def _shoppingcart_stypename(stype):
    if stype == 'P':
        return '赠送'
    if stype == 'E':
        return '定金'
    return '正常'


def _parse_request_param_json(request):
    p = request.GET.get('param') or request.POST.get('param')
    if p:
        return json.loads(p)
    body = getattr(request, 'body', None) or b''
    if isinstance(body, bytes):
        body = body.decode('utf-8', errors='replace')
    if body.strip().startswith('{'):
        return json.loads(body)
    raise ValueError('missing or invalid param')


def _parse_uuid_loose(s):
    if s is None or s == '':
        raise ValueError('empty uuid')
    t = str(s).strip().replace('-', '')
    if len(t) == 32:
        return uuid.UUID(hex=t)
    return uuid.UUID(str(s).strip())


def _serialize_shoppingcart_row(sc, include_depositeflag=False):
    st = sc.stype or 'N'
    row = {
        'ccode': sc.payccode,
        'itemcode': sc.itemcode,
        'itemname': sc.itemname,
        'qty': sc.qty,
        'price': sc.price,
        'secdisc': sc.secdisc,
        'mondisc': sc.mondisc,
        'amount': sc.amount,
        'pmcode': sc.pmcode,
        'seccode': sc.seccode,
        'thrcode': sc.thrcode,
        'promotionsid': sc.promotionsid,
        'uuid': str(sc.uuid),
        'ttype': sc.ttype,
        'stype': sc.stype,
        'stypename': _shoppingcart_stypename(st),
        'planqty': sc.planqty,
        'planamount': sc.planamount,
        'payedamount': sc.payedamount,
        'oweamount': sc.oweamount,
        'remark': sc.remark,
    }
    if include_depositeflag:
        row['depositeflag'] = sc.depositeflag
    return row


def json_to_excel(json_data,filename):
    print('filename',filename)
    df = pd.DataFrame()  # 最后转换得到的结果
    data = json.loads(json_data)

    # for line in data:
    #     # print('line',type(line),line)
    #     df = json_normalize(line)
    #     # for i in line:
    #     #     df1 = pd.DataFrame([i])
    #     #     df = df.append(df1)
    # print('df',df)

    df2 = pd.DataFrame()
    df2 = json_normalize(data)
    print('df2',df2)
    df2.to_excel(filename, 'sheet1')

    # with open(json_data, 'r', encoding='utf-8', errors='ignore') as f:
    #     rows = json.load(f)
    # # 将json中的key作为header, 也可以自定义header（列名）
    # header = tuple([i for i in rows[0].keys()])
    # data = []
    # # 循环里面的字典，将value作为数据写入进去
    # for row in rows:
    #     body = []
    #     for v in row.values():
    #         body.append(v)
    #     data.append(tuple(body))
    # # 将含标题和内容的数据放到data里
    # data = tablib.Dataset(*data, headers=header)
    # open(filename, 'wb').write(filename)

    return 0

def parse_ymd(s):
    split_s = s[4:5]
    print('split_s:',split_s,s)
    year_s, mon_s, day_s = s.split(split_s)
    mon_s = ('0' + mon_s)[-2:]
    day_s = ('0' + day_s)[-2:]
    print(year_s,mon_s,day_s)
    return year_s + mon_s + day_s

def getviplist(request):
    company=request.GET['company']
    storecode=request.GET['storecode']
    thisdate = datetime.strftime(datetime.now(),'%Y%m%d')
    print(thisdate)
    # vips= ExpvstollHung.objects.filter(company=company,vsdate_hung=thisdate).values('vipuuid')
    viplist= Vip.objects.filter(company=company,storecode=storecode).values('uuid','vcode','vname','viplevel')
    print('viplist',viplist)

    data = serializers.serialize('json', viplist,fields=('uuid','vcode','vname','viplevel',))
    print('date',data)

    return HttpResponse(data, content_type="application/json")

def get_VipList_ByVipTypeAndEcode(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        viptype = request.GET['viptype']
    except:
        viptype=''

    try:
        ecode=request.GET['ecode']
    except:
        ecode='%'

    sql = " select uuid,vcode, vname,mtcode,ecode,ecode2, viplevel,viptype,pinyin,GetVCODEdate(company,storecode,uuid,'lastindate') lastindate,GetVCODEdate(company,storecode,uuid,'INDATE') indate  " \
          " from vip " \
          " where 1=1 and flag='Y' " \
          " and company = %s and storecode =%s and ecode=%s and viptype =%s" \
          " order by vname"

    params = (company+'  '+ storecode +' ' + ecode  + ' '+viptype+' ').split()
    print(sql, params)
    json_data = sql_to_json(sql,params)

    return HttpResponse(json_data, content_type="application/json")

def get_VipList_ByLevel(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        rpttype = request.GET['rpttype']
    except:
        rpttype='in'

    try:
        ecode=request.GET['ecode']
    except:
        ecode='%'

    delta = timedelta(days=-90)
    print(delta)
    now = datetime.now()

    fromdate = datetime.strftime((now + delta),'%Y%m%d')
    todate = datetime.strftime( datetime.now()  ,'%Y%m%d')
    print(fromdate,todate,rpttype)

    if rpttype =='in':
        sql = " select uuid,vcode, vname,mtcode,ecode,ecode2, viplevel,viptype,pinyin,GetVCODEdate(company,storecode,uuid,'lastindate') lastindate,GetVCODEdate(company,storecode,uuid,'indate') indate " \
              " from vip " \
              " where 1=1 and flag='Y' " \
              " and company = %s and storecode =%s and ecode=%s" \
              " and uuid in ( select vipuuid from expvstoll" \
              "               where 1=1 and flag='Y' and valiflag='Y' and company=%s and storecode=%s " \
              "               and vsdate between %s and %s " \
              "             )" \
              " order by vname"

        params = (company+'  '+ storecode +' ' + ecode  + '  '+ company +'  '+storecode + '   '+ fromdate + '  ' + todate+ ' ').split()
        print(sql, params)
        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

    if rpttype == 'notin':
        sql = " select uuid,vcode, vname,mtcode,ecode,ecode2, viplevel,viptype,pinyin,GetVCODEdate(company,storecode,uuid,'lastindate') lastindate,GetVCODEdate(company,storecode,uuid,'indate') indate " \
              " from vip " \
              " where 1=1 and flag='Y' " \
              " and company = %s and storecode =%s and ecode=%s" \
              " and uuid not in ( select vipuuid from expvstoll" \
              "               where 1=1 and flag='Y' and valiflag='Y' and company=%s and storecode=%s " \
              "               and vsdate between %s and %s " \
              "             )" \
              " order by vname"

        params = (company+'  '+ storecode +' ' + ecode  + ' '+ company +' '+storecode+'  '+ fromdate +'  '+ todate).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)

        return HttpResponse(json_data, content_type="application/json")

def get_vip_cardlist(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    vipuuid=request.GET['vipuuid'].replace('-','')

    # vip = Vip.objects.get(uuid=request.GET['vipuuid'])
    # company=vip.company

    try:
        suptype = request.GET['suptype']
        sql = " select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price s_price, a.leftqty leftqty, a.promotionsid,b.suptype suptype, b.comptype comptype, a.status status, a.valdate valdate, (select coalesce(promotionsname,'') from promotions where company=a.company and promotionsid=a.promotionsid limit 1) as promotionname," \
              "  concat((case status when 'P' then '挂账-' else '已购-' end ),cardname,'(',trim(a.cardnote),')', a.leftqty,'*',a.s_price,'=',a.leftmoney) carddesc  " \
              " from cardinfo a, cardtype b " \
              " where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype " \
              " and a.status in ('O','P')" \
              " and a.vipuuid = %s and b.suptype=%s"

        params = (company, vipuuid, suptype)
        print('sql:', sql, 'params', params)
    except:
        # 默认查询：返回该会员所有卡片（无 suptype/comptype 筛选）
        sql = (
            "select a.uuid uuid, vcode,ccode,a.cardtype cardtype,cardname, "
            "a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney, "
            "a.s_price s_price, a.leftqty leftqty, "
            "a.promotionsid,b.suptype suptype, b.comptype comptype, a.status status, a.stype stype, a.valdate valdate, "
            "(select coalesce(promotionsname,'') from promotions where company=a.company and promotionsid=a.promotionsid limit 1) as promotionname, "
            "concat( "
            "(case a.status when 'P' then '挂账-' else '已购-' end ),"
            "(case a.stype when 'P' then '赠送' when 'N' then '正常' else '' end ),'-',"
            "cardname,'-结余:',coalesce(a.leftmoney,a.leftqty,0)) carddesc "
            "from cardinfo a, cardtype b "
            "where a.flag='Y' and b.flag='Y' "
            "and a.company=%s and a.company=b.company "
            "and a.cardtype=b.cardtype "
            "and a.status in ('O','P') "
            "and a.vipuuid=%s "
            "order by a.ccode"
        )
        params = (company, vipuuid)
        print('[default] sql:', sql, 'params:', params)

    try:
        comptype = request.GET['comptype']
        if comptype == 'amount':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, a.promotionsid,b.suptype suptype, b.comptype comptype, a.status status, a.valdate valdate, (select coalesce(promotionsname,'') from promotions where company=a.company and promotionsid=a.promotionsid limit 1) as promotionname," \
                  "  a.stype stype, concat((case a.status when 'P' then '挂账' else '已购' end ),'-',(case a.stype when 'P' then '赠送' when 'N' then '正常' else '' end ),'-' , cardname,'-结余:',a.leftmoney) carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s"

            params = (company, vipuuid, comptype)

        if comptype == 'times':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, a.promotionsid,b.suptype suptype, b.comptype comptype, a.status status, a.valdate valdate, (select coalesce(promotionsname,'') from promotions where company=a.company and promotionsid=a.promotionsid limit 1) as promotionname," \
                  "  a.stype stype,concat((case a.status when 'P' then '挂账' else '已购' end ),'-',(case a.stype when 'P' then '赠送' when 'N' then '正常' else '' end ),'-', cardname,'-',ifnull(a.cardnote,''),  '  结余:',a.leftqty,'次') carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype and a.leftqty >0 " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s" \
                  "  order by a.ccode"
            params = (company, vipuuid, comptype)

        if comptype == 'period':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, a.promotionsid,b.suptype suptype, b.comptype comptype, a.status status, a.valdate valdate, (select coalesce(promotionsname,'') from promotions where company=a.company and promotionsid=a.promotionsid limit 1) as promotionname," \
                  "  a.stype stype, concat((case a.status when 'P' then '挂账-' else '正常-' end ),'-',a.stype,'-', cardname, '-',ifnull(a.cardnote,'') , '  结余:',a.leftqty,'次') carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype and a.leftmoney >0 " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s " \
                  "  order by a.ccode"

            params = (company, vipuuid, comptype)

    except:
        pass

    json_data = safe_execute_sql(sql,params)
    print('sql:', sql, 'params', params)
    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_vip_itemlist(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        vipuuid=request.GET['vipuuid'].replace('-','')
    except:
        vipuuid=''

    try:
        ttype = request.GET['ttype']
    except:
        ttype ='S'

    if ttype=='S':
        # sql = "select uuid, svrcdoe itemcode,svrname itemname, price,brand,displayclass1,tags,'S' ttype, 'N' stype " \
        #       " from serviece " \
        #       " where 1=1 and flag='Y' and valiflag='Y' and saleflag='Y' " \
        #       " and company=%s and svrcdoe in ( " \
        #       "        select srvcode " \
        #       "        from expvstoll a, expense b " \
        #       "        where 1=1 and a.company=%s"\
        #       "        and a.uuid=b.transuuid " \
        #       "        and b.ttype in ('S') " \
        #       "        union all " \
        #       "       select svrcdoe from serviece where 1=1 and flag='Y' and saleflag='Y' and valiflag='Y' and company=%s" \
        #       "      ) " \
        #       " order by displayclass1 ,brand,svrcdoe" \
        #       " limit 50"

        sql = " select distinct a.uuid, a.itemcode,a.itemname,price, brand, displayclass1, tags,ttype,stype "\
              "  from "\
              "      ( " \
              "          select uuid, svrcdoe itemcode,svrname itemname, price,brand,displayclass1,tags,'S' ttype, 'N' stype  " \
              "          from serviece  where 1=1 and flag='Y' and valiflag='Y' and saleflag='Y'  "\
              "          and company=%s "\
              "      ) a left outer join "\
              "   (       "\
               "          select distinct srvcode    "\
              "          from expvstoll a, expense b"\
              "           where 1=1 and a.company=%s        and a.uuid=b.transuuid         and b.ttype in ('S')        " \
              "           union all        "\
              "           select svrcdoe "\
              "           from serviece where 1=1 and flag='Y' and saleflag='Y' and valiflag='Y' and company=%s  "\
              "  )  b"\
              "  on a.itemcode = b.srvcode "\
              "  order by displayclass1 ,brand,itemcode limit 50 "

        # params = (company + ' ' + vipuuid ).split()
        params = (company  +' ' +company +' ' +company).split()
        print('sql:', sql, 'params', params)

        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

    if ttype=='G':
        sql = " select g.uuid uuid, g.gcode itemcode,g.gname itemname, g.brand, g.displayclass1, g.price,g.goodsct, a.qty2,tags,'G' ttype, 'N' stype "\
              "  from goodstranslog a ,( "\
              "      select company , storecode, whcode, gcode, max(gtranukid) gtranukid "\
              "      from goodstranslog "\
              "     where 1=1 and saleatr='G' and company=%s "\
              "      and storecode=%s "\
              "      group by storecode, whcode, gcode  "\
             "      ) b, goods g "\
             "  where g.flag='Y' and g.valiflag='Y' and a.company=b.company  and a.company = g.company  and a.storecode=b.storecode "\
             "  and a.gcode = b.gcode  and a.gcode = g.gcode AND g.saleflag='Y' "\
             "  and a.gtranukid = b.gtranukid and a.qty2>0 " \
             "  order by displayclass1,brand,itemcode" \
             "  limit 50"

        # params = (company + ' ' + vipuuid ).split()
        params = (company +' ' +storecode ).split()
        print('goods sql:', sql, 'params', params)

        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

class BookingeventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    lookup_field = 'bookingeventid'
    queryset = Bookingevent.objects.all().order_by('bookingeventid','bookingstartdate','bookingstarttime')
    serializer_class = BookingeventSerializer

class CardinfoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Cardinfo.objects.filter(company=common.constants.COMPANYID).order_by('vcode')
    serializer_class = CardinfoSerializer

def GetSerno(company, storecode, tablecode):
    """
    按 company + storecode + tablecode 递增 common_sequence 表，生成 exptxserno 等流水后缀。
    若库中未迁移出 `sequence` 表（ProgrammingError），退化为时间戳+随机串，避免购物车/挂单接口 500。
    生产环境仍应执行：python manage.py migrate common
    """
    code = str(tablecode or '').strip()
    if code == '':
        code = 'hung'
    prefix = '{}_{}_{}_'.format(company, storecode, code)
    try:
        with transaction.atomic():
            row = (
                Sequence.objects.select_for_update()
                .filter(company=company, storecode=storecode, tablecode=tablecode)
                .order_by('uuid')
                .first()
            )
            if row is None:
                Sequence.objects.create(
                    company=company,
                    storecode=storecode,
                    tablecode=tablecode,
                    sequence=0,
                )
                row = (
                    Sequence.objects.select_for_update()
                    .filter(company=company, storecode=storecode, tablecode=tablecode)
                    .order_by('uuid')
                    .first()
                )
            next_val = int(row.sequence or 0) + 1
            row.sequence = next_val
            row.save(update_fields=['sequence'])
            print('GetSerno sequence row', row.uuid, '->', next_val)
            return prefix + str(next_val)
    except (ProgrammingError, OperationalError) as exc:
        # 例如：1146 Table 'youlan.sequence' doesn't exist
        print('GetSerno fallback (sequence table unavailable):', exc)
        import time

        suffix = str(int(time.time() * 1000)) + '_' + uuid.uuid4().hex[:8]
        return prefix + suffix

@csrf_exempt
@transaction.atomic
def NewCardHung(request):
    if request.method == 'POST':
        # print('request.body=', request.body)
        # try:
        #     with transaction.atomic():
                data= json.loads(request.GET['param'])
                company = data['company']
                storecode= data['storecode']
                ecode= data['ecode']
                vcode = data['vcode']
                vipuuid = data['vipuuid']
                payccode = data['payccode']
                stype =  data['stype']
                ttype = data['ttype']
                psstatus='10'
                # cardtype = data['cardtype']
                # cardtypeuuid = data['cardtypeuuid']
                newcardtype=data['newcardtype']
                qty = data['qty']
                price = data['price']
                secdisc = data['secdisc']
                mondisc = data['mondisc']
                amount=data['amount']
                leftmoney = data['leftmoney']
                # leftqty = data['leftqty']
                pmcode=data['pmcode']
                seccode=data['seccode']
                thrcode=data['thrcode']
                promotionsid=data['promotionsid']
                remark = data['remark']

                vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
                vstime = datetime.strftime(datetime.now(),'%H%M%S')
                exptxserno_hung = GetSerno(company,storecode,'hung')

                vip = Vip.objects.get(uuid=vipuuid)
                vcode=vip.vcode
                newccode= Vip.nextccode(vip)
                print('newcadtype',newcardtype)
                cardtypeuuids = Cardtype.objects.filter(company=company,flag='Y',cardtype=newcardtype)
                print('cardtypeuuid:',cardtypeuuids)

                if cardtypeuuids.exists() ==0 :
                    content = {
                        "statusCode": '400',
                        "error": True,
                        "msg": '销售卡卡类错误'
                    }
                    # return HttpResponse(content, content_type="application/json")
                    return JsonResponse(content, content_type="application/json")
                cardtypeuuid=cardtypeuuids.last()

                # cardinfo = Cardinfo.objects.get_or_create(
                #     company=company,storecode=storecode,ccode=newccode,vcode=vcode,cardtype=newcardtype,status='P',
                #     leftqty=qty, s_price=price,leftmoney=leftmoney,svalue=amount,stype=stype,
                #     suptype=cardtypeuuid.suptype,vipuuid=vip, cardtypeuuid=cardtypeuuid)[0]

                cardinfo = Cardinfo.objects.get_or_create(
                    company=company, storecode=storecode, ccode=newccode, vcode=vcode, cardtype=newcardtype, status='P',
                    leftqty=qty, s_price=price, leftmoney=leftmoney, svalue=amount)[0]
                cardinfo.stype=stype
                cardinfo.suptype = cardtypeuuid.suptype
                cardinfo.vipuuid = vip
                cardinfo.cardtypeuuid=cardtypeuuid
                cardinfo.promotionsid =promotionsid
                cardinfo.cardnote=remark
                cardinfo.save()

                paycardtype=''
                if len(payccode)>0:
                    try:
                        paycard=Cardinfo.objects.filter(company=company,status='O',ccode=payccode)[0]
                        paycardtype=paycard.cardtype
                    except:
                        paycardtype=''

                expvstollhung = ExpvstollHung.objects.create(
                    company = company,storecode=storecode,ecode_hung=ecode,valiflag_hung='Y',
                    exptxserno_hung=exptxserno_hung,
                    vipuuid=vip,
                    # vcode_hung=Vip.objects.get(uuid=vipuuid).vcode,
                    vcode_hung = vcode,
                    ccode_hung = payccode,
                    cardtype_hung = paycardtype,
                    vsdate_hung=vsdate,
                    vstime_hung=vstime,
                    ttype_hung=ttype,
                    psstatus_hung = psstatus,
                    totmount_hung = amount
                )

                hungserno = ''.join(str(expvstollhung.uuid).split('-'))
                print(hungserno)
                expensehung = ExpenseHung.objects.create(
                    exptxserno_hung =exptxserno_hung,
                    ditem_hung='001',
                    ttype_hung = ttype,
                    stype_hung = stype,
                    srvcode_hung = newccode,
                    s_qty_hung = qty,
                    s_price_hung = price,
                    company=company,storecode=storecode,
                    s_mount_hung = amount,
                    srvmondisc_hung=mondisc,
                    secdisc_hung=secdisc,
                    addvamoney_hung=leftmoney,
                    pmcode_hung = pmcode,
                    asscode1_hung = seccode,
                    asscode2_hung = thrcode,
                    newcardtype_hung = newcardtype,
                    hunguuid = expvstollhung,
                    dnote_hung=remark
                    # hunguuid = ''.join(str(expvstollhung.uuid).split('-')
                )
                # cardinfo.save()
                # expvstollhung.save()
                # expensehung.save()
        # except:
        #     return HttpResponse("501",content_type="application/json")

                content ={
                    "statusCode":'200',
                    "error":  False,
                    "msg": '开单完成'
                }
                # return HttpResponse(content, content_type="application/json")
                return JsonResponse(content, content_type="application/json")
    else:
        return HttpResponse("400", content_type="application/json")

@csrf_exempt
@transaction.atomic
def FillCardHung(request):
    if request.method == 'POST':
        data= json.loads(request.GET['param'])
        print(data)
        company = data['company']
        storecode= data['storecode']
        ecode= data['ecode']

        try:
            vipuuid = data['vipuuid']
        except:
            vipuuid=''

        try:
            payccode = data['payccode']
        except:
            payccode=''

        try:
            stype =  data['stype']
        except:
            stype='N'
        try:
            ttype =  data['ttype']
        except:
            ttype='I'
        psstatus='10'
        # cardtype = data['cardtype']
        # cardtypeuuid = data['cardtypeuuid']

        try:
            itemcode=data['itemcode']
        except:
            return HttpResponse("500 not itemcode", content_type="application/json")

        try:
            oldcardtype=data['oldcardtype']
        except:
            oldcardtype=''

        try:
            newcardtype=data['newcardtype']
        except:
            return HttpResponse("500 not newcardtype", content_type="application/json")
        try:
            qty = data['qty']
        except:
            qty = 0

        try:
            price = data['price']
        except:
            price=0

        try:
            secdisc = data['secdisc']
        except:
            secdisc=1

        try:
            mondisc = data['mondisc']
        except:
            mondisc=0

        try:
            amount=data['amount']
        except:
            amount=0

        try:
            leftmoney = data['leftmoney']
        except:
            leftmoney=0
        # leftqty = data['leftqty']



        try:
            pmcode=data['pmcode']
        except:
            pmcode=''

        try:
            seccode=data['seccode']
        except:
            seccode=''

        try:
            thrcode=data['thrcode']
        except:
            thrcode=''

        try:
            promotionsid=data['promotionsid']
        except:
            promotionsid='0'

        vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
        vstime = datetime.strftime(datetime.now(),'%H%M%S')
        exptxserno_hung = GetSerno(company,storecode,'hung')

        try:
            vip = Vip.objects.get(uuid=vipuuid)
        except:
            print('not find vip with uuid=',vipuuid)
            return HttpResponse("500 not vip", content_type="application/json")

        vcode=vip.vcode

        print('newcadtype',newcardtype)

        # try:
        #     cardtypeuuids = Cardtype.objects.get(company=company,flag='Y',cardtype=newcardtype)
        # except:
        #     print('not findnot cardtype with cardtype==',newcardtype)
        #     return HttpResponse("501 not cardtype with cardtype="+newcardtype, content_type="application/json")
        #     print('cardtypeuuid:',cardtypeuuids)
        #
        # if cardtypeuuids.exists() ==0 :
        #     content = {
        #         "statusCode": '400',
        #         "error": True,
        #         "msg": '销售卡卡类错误'
        #     }
        #     # return HttpResponse(content, content_type="application/json")
        #     return JsonResponse(content, content_type="application/json")
        # cardtypeuuid=cardtypeuuids.last()

        # cardinfo = Cardinfo.objects.get(
        #     company=company,storecode=storecode,ccode=newccode,vcode=vcode,cardtype=newcardtype,status='P',
        #     leftqty=qty, s_price=price,leftmoney=leftmoney,svalue=amount,
        #     suptype=cardtypeuuid.suptype,vipuuid=vip, cardtypeuuid=cardtypeuuid,promotionsid=promotionsid
        # )
        paycardtype=''
        if len(payccode)>0:
            try:
                paycard=Cardinfo.objects.get(company=company,creater=ecode,status='O',ccode=payccode)
                paycardtype=paycard.cardtype
            except:
                paycardtype=''

        expvstollhung = ExpvstollHung.objects.create(
            company = company,storecode=storecode,creater=ecode,ecode_hung=ecode,valiflag_hung='Y',
            exptxserno_hung=exptxserno_hung,
            vipuuid=vip,
            # vcode_hung=Vip.objects.get(uuid=vipuuid).vcode,
            vcode_hung = vcode,
            ccode_hung = payccode,
            cardtype_hung = paycardtype,
            vsdate_hung=vsdate,
            vstime_hung=vstime,
            ttype_hung=ttype,
            psstatus_hung = psstatus,
            totmount_hung = amount
        )

        hungserno = ''.join(str(expvstollhung.uuid).split('-'))
        print(hungserno)
        expensehung = ExpenseHung.objects.create(
            company=company,storecode=storecode,
            exptxserno_hung =exptxserno_hung,
            ditem_hung='001',
            ttype_hung = ttype,
            stype_hung = stype,
            srvcode_hung = itemcode,
            s_qty_hung = qty,
            s_price_hung = price,
            s_mount_hung = amount,
            srvmondisc_hung=mondisc,
            secdisc_hung=secdisc,
            addvamoney_hung=leftmoney,
            pmcode_hung = pmcode,
            asscode1_hung = seccode,
            asscode2_hung = thrcode,
            oldcardtype_hung=oldcardtype,
            newcardtype_hung=newcardtype,
            hunguuid = expvstollhung
        )
        # hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
        # cardinfo.save()
        expvstollhung.save()
        expensehung.save()

        content ={
            "statusCode":'200',
            "error":  False,
            "msg": '开单完成'
        }
        # return HttpResponse(content, content_type="application/json")
        return JsonResponse(content, content_type="application/json")
    else:
        return HttpResponse("400", content_type="application/json")


@csrf_exempt
def AddHung(request):

    if request.method == 'POST':
        # print('request.body=', request.body)
        data= json.loads(request.GET['param'])
        print('2',data)
        company = data['company']
        storecode= data['storecode']
        ecode= data['ecode']
        vcode = data['vcode']
        vipuuid = data['vipuuid']
        payccode = data['ccode']

        cardtype = data['cardtype']
        cardtypeuuid = data['cardtypeuuid']
        # s_qty = data['s_qty']
        # s_price = data['s_price']
        # secdisc = data['secdisc']
        # mondisc = data['mondisc']
        # s_amount=data['s_amount']
        leftmoney = data['leftmoney']
        promotionsid = data['promotionsid']
        leftqty = data['leftqty']
        totamount = data['consumeamount']

        vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
        vstime = datetime.strftime(datetime.now(),'%H%M%S')
        exptxserno_hung = GetSerno(company,storecode,'hung')

        hungs = data['hung']
        print('len(hungs)=',len(hungs),'itemcode=',hungs[0]['itemcode'],'vipuuid=',vipuuid,'vstime_hung',vstime)

        print(exptxserno_hung )

        expvstollhung = ExpvstollHung.objects.create(
            company = company,storecode=storecode,ecode_hung=ecode,psstatus_hung='10',valiflag_hung='Y',
            exptxserno_hung=exptxserno_hung,
            vcode_hung=Vip.objects.get(uuid=vipuuid).vcode,
            vipuuid=Vip.objects.get(uuid=vipuuid),
            ccode_hung = payccode,
            cardtype_hung = cardtype,
            vsdate_hung=vsdate,
            vstime_hung=vstime
        )
        print(expvstollhung)
        # if len(hungs) > 0 :
            # print('hungdetail',hungdetail,'vsdate=',vsdate,'vstime=',vstime,'hungdetail=',hungdetail)
        # try:
        #     print(expvstollhung)
        for hung in hungs:
            print(hung)
            stype = hung['stype']
            ttype = hung['ttype']
            itemcode = hung['itemcode']
            s_qty = hung['qty']
            s_price = hung['s_price']
            secdisc = hung['secdisc']
            mondisc = hung['mondisc']
            amount = hung['amount']
            pmcode = hung['pmcode']
            seccode = hung['seccode']
            thrcode = hung['thrcode']
            print(itemcode)
            expensehung = ExpenseHung.objects.create(
                exptxserno_hung =exptxserno_hung,
                ttype_hung = ttype,
                stype_hung = stype,
                srvcode_hung = itemcode,
                s_qty_hung = s_qty,
                s_price_hung = s_price,
                s_mount_hung = amount,
                pmcode_hung = pmcode,
                asscode1_hung = seccode,
                asscode2_hung = thrcode,
                hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
            )
        #
        # except:
        #     print('error')

    return HttpResponse('0', content_type="application/json")

@csrf_exempt
@transaction.atomic
def AddShoppingCart(request):
    if request.method == 'POST':
        data= json.loads(request.GET['param'])
        print('AddShoppingCart request param:',data)
        company = data['company']
        storecode= data['storecode']
        ecode= data['ecode']
        # vcode = data['vcode']
        vipuuid = uuid.UUID(data['vipuuid'])
        payccode = data['payccode']
        stype =  data['stype']
        ttype = data['ttype']
        psstatus='10'
        # cardtype = data['cardtype']
        # cardtypeuuid = data['cardtypeuuid']
        # newcardtype=data['newcardtype']
        itemcode=data['itemcode']
        qty = data['qty']
        price = data['price']
        secdisc = data['secdisc']
        mondisc = data['mondisc']
        amount=data['amount']
        try:
            depositeflag=data['depositeflag']
        except:
            depositeflag ='N'

        try:
            leftmoney = data['leftmoney']
        except:
            leftmoney=0

        # leftqty = data['leftqty']
        pmcode=data['pmcode']
        seccode=data['seccode']
        thrcode=data['thrcode']
        try:
            promotionsid=data['promotionsid']
        except:
            promotionsid='0'

        try:
            planqty=data['planqty']
        except:
            planqty=0

        try:
            planamount = data['planamount']
        except:
            planamount=0

        try:
            payedamount =data['payedamount']
        except:
            payedamount=0

        try:
            oweamount = data['oweamount']
        except:
            oweamount=0

        try:
            remark = data['remark']
        except Exception as e:
            print('remark error',e)
            remark=''

        print('remark',remark)

        vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
        vstime = datetime.strftime(datetime.now(),'%H%M%S')
        vip = Vip.objects.get(company=company,uuid=vipuuid)

        if len(payccode)>0:
            try:
                paycard=Cardinfo.objects.filter(company=company,status='O',ccode=payccode).filter()
                paycardtype=paycard.cardtype
            except:
                paycardtype=''
        else:
            payccode=''
            paycardtype=''

        if ttype=='S':
            item=Serviece.objects.filter(company=company,flag='Y',svrcdoe=itemcode).last()
            itemname=item.svrname
            print('ttype=',ttype)
        if ttype=='G':
            item=Goods.objects.filter(company=company,flag='Y',gcode=itemcode).last()
            itemname=item.gname

        if ttype=='I':
            cardinfo=Cardinfo.objects.filter(company=company,flag='Y', status__in=('P','O'),ccode=itemcode).last()
            cardtype=Cardtype.objects.filter(company=company,cardtype=cardinfo.cardtype,flag='Y').last()
            itemname=cardtype.cardname

        print('payccode2',payccode)

        shoppingcartitem = ShoppingCart.objects.create(
            company=company,
            storecode=storecode,
            creater=ecode,
            vipuuid=vip,
            vcode=vip.vcode,
            payccode=payccode,
            ttype = ttype,
            stype = stype,
            itemcode = itemcode,
            itemname=itemname,
            qty = qty,
            price = price,
            mondisc=mondisc,
            secdisc=secdisc,
            amount=amount,
            # addvamoney_hung=leftmoney,
            pmcode = pmcode,
            seccode = seccode,
            thrcode = thrcode,
            promotionsid=promotionsid,
            status='10',
            planqty= planqty ,
            planamount = planamount,
            payedamount = payedamount,
            oweamount = oweamount,
            remark = remark,
            depositeflag = depositeflag
        )

        shoppingcartitem.save()
        content ={
            "statusCode":'200',
            "error":  False,
            "msg": '已加入购物车'
        }
        # return HttpResponse(content, content_type="application/json")
        return JsonResponse(content, content_type="application/json")
    else:
        content={
            "statusCode": '400',
            "error": False,
            "msg": '加入购物车失败'
        }
        return HttpResponse("400", content_type="application/json")

@csrf_exempt
@transaction.atomic
def modify_ShoppingCartItem(request):
    if request.method=='POST':
        data = json.loads(request.GET['param'])
        print('request param:', data)
        oper=data['oper']
        company = data['company']
        storecode = data['storecode']
        ecode = data['ecode']
        print('data[uuid]=',data['uuid'])
        try:
            tmpuuid = data['uuid']
        except:
            tmpuuid = ''
            return HttpResponse('500', content_type="application/json")

        cartitemuuid = uuid.UUID(tmpuuid)
        print('cartitemuuid:',cartitemuuid)
        if oper=='delete':
            try:
                cartitem = ShoppingCart.objects.get(company=company,uuid=cartitemuuid)
                cartitem.flag='N'
                cartitem.save()
                return HttpResponse('200', content_type="application/json")
            except:
                print('delete, not this shoppingcart item,uuid=',cartitemuuid)
                return HttpResponse('501', content_type="application/json")

        if oper=='modify':
            print('modify',cartitemuuid)
            try:
                cartitem = ShoppingCart.objects.get(company=company,uuid=cartitemuuid)
                print('cartitem',cartitem.itemcode,cartitem)
                print('data',data)
                try:
                    payccode = data['payccode']
                except:
                    payccode=''

                try:
                    qty = data['qty']
                except:
                    qty=1

                try:
                    price = data['price']
                except:
                    price=0

                try:
                    secdisc = data['secdisc']
                except:
                    secdisc=1

                try:
                    mondisc = data['mondisc']
                except:
                    mondisc=0

                try:
                    amount = data['amount']
                except:
                    amount=0

                try:
                    stype = data['stype']
                except:
                    stype='N'

                try:
                    pmcode = data['pmcode']
                except:
                    pmcode=''

                try:
                    seccode = data['seccode']
                except:
                    seccode=''

                try:
                    thrcode = data['thrcode']
                except:
                    trhcode=''

                try:
                    promotionsid = data['promotionsid']
                except:
                    promotionsid='0'
                print('promotionsid',promotionsid)

                try:
                    planqty = data['planqty']
                except:
                    planqty = 0

                try:
                    planamount = data['planamount']
                except:
                    planamount = 0

                try:
                    payedamount = data['payedamount']
                except:
                    payedamount = 0

                try:
                    oweamount = data['oweamount']
                except:
                    oweamount = 0

                try:
                    remark = data['remark']
                except Exception as e:
                    print('remark error',e)
                    remark = ''
                print('remark',remark)

                try:
                    depositeflag = data['depositeflag']
                except:
                    depositeflag='N'

                # cartitem.last_modified = datetime.now()
                cartitem.creater = ecode
                cartitem.payccode = payccode
                cartitem.qty = qty
                cartitem.price = price
                cartitem.secdisc = secdisc
                cartitem.mondisc = mondisc
                cartitem.amount = amount
                cartitem.stype = stype
                cartitem.pmcode = pmcode
                cartitem.seccode = seccode
                cartitem.thrcode = thrcode
                cartitem.planqty = planqty
                cartitem.planamount = planamount
                cartitem.payedamount = payedamount
                cartitem.oweamount = oweamount
                cartitem.remark = remark
                # print(2,depositeflag,remark)
                cartitem.depositeflag = depositeflag
                # print(3,qty,price,secdisc,mondisc,amount,planqty,planamount,payedamount,'2',oweamount)
                # update_fields = ['creater','payccode','qty','price','secdisc','mondisc','amount','stype','pmcode','seccode','thrcode','planqty','planamount',
                #                  'payedamount','oweamount','remark','depositeflag']
                # cartitem.save(update_fields=update_fields)
                cartitem.save()
                # print(4)

                return HttpResponse('200', content_type="application/json")

            except:
                raise
                print('modify ,not this shoppingcart item,uuid=',cartitemuuid)
                return HttpResponse('502', content_type="application/json")

    return HttpResponse('200', content_type="application/json")

@csrf_exempt
@transaction.atomic
def get_ShoppingCart(request):
    """
    小程序购物车行列表。原实现依赖 MySQL 函数 F_Getnamebysrvcode，库中未必存在会导致 500；
    现改为 ORM，itemname 使用表中已存名称。
    """
    try:
        if request.method == 'POST':
            data = _parse_request_param_json(request)
        elif request.method == 'GET':
            data = {
                'company': request.GET.get('company', common.constants.COMPANYID),
                'storecode': request.GET.get('storecode', '88'),
                'ecode': request.GET.get('ecode', '888'),
                'vipuuid': request.GET.get('vipuuid', '123'),
                'ttype': request.GET.get('ttype', 'S'),
            }
        else:
            return HttpResponse('[]', content_type="application/json")
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print('get_ShoppingCart param error:', e)
        return HttpResponse('[]', content_type="application/json")

    company = data.get('company') or common.constants.COMPANYID
    storecode = data.get('storecode', '88')
    ttype = data.get('ttype', 'S')
    try:
        v_uuid = _parse_uuid_loose(data.get('vipuuid'))
    except (ValueError, TypeError, AttributeError) as e:
        print('get_ShoppingCart vipuuid:', e)
        return HttpResponse('[]', content_type="application/json")

    qs = (
        ShoppingCart.objects.filter(
            company=company,
            storecode=storecode,
            vipuuid=v_uuid,
            ttype=ttype,
            flag='Y',
            status='10',
        )
        .order_by('create_time', 'uuid')
    )
    out = [_serialize_shoppingcart_row(x) for x in qs]
    return HttpResponse(
        json.dumps(out, cls=DjangoJSONEncoder), content_type="application/json"
    )

@csrf_exempt
@transaction.atomic
def get_ShoppingCartItem(request):
    if request.method != 'POST':
        return HttpResponse('[]', content_type="application/json")
    try:
        data = _parse_request_param_json(request)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print('get_ShoppingCartItem param error:', e)
        return HttpResponse('[]', content_type="application/json")

    company = data.get('company') or common.constants.COMPANYID
    storecode = data.get('storecode', '88')
    line_id = data.get('uuid', '')
    try:
        v_uuid = _parse_uuid_loose(data.get('vipuuid'))
        line_uuid = _parse_uuid_loose(line_id)
    except (ValueError, TypeError) as e:
        print('get_ShoppingCartItem uuid:', e)
        return HttpResponse('[]', content_type="application/json")

    qs = ShoppingCart.objects.filter(
        company=company,
        storecode=storecode,
        vipuuid=v_uuid,
        uuid=line_uuid,
        flag='Y',
        status='10',
    )
    out = [_serialize_shoppingcart_row(x, include_depositeflag=True) for x in qs]
    return HttpResponse(
        json.dumps(out, cls=DjangoJSONEncoder), content_type="application/json"
    )

@csrf_exempt
# @transaction.atomic
def ShoppingCartHung(request):
    if request.method == 'POST':
        data= json.loads(request.GET['param'])
        print('ShoppingCartHung request param:',data)
        company = data['company']
        storecode= data['storecode']
        ecode= data['ecode']
        vipuuid = data['vipuuid']

        vsdate=''
        uuids = data['uuids']
        for uuid in uuids:
            if uuid is None:
                print('uuid is None,skipped!')
            else:
                print('uuid=',uuid)
                cartitem= ShoppingCart.objects.get(company=company,storecode=storecode,flag='Y',uuid=uuid)
                print('cartitem',cartitem, cartitem.payccode)

                if len(cartitem.payccode)>0:
                    payccode = cartitem.payccode
                    cardtype = Cardinfo.objects.filter(company=company,status__in=('O','P'),flag='Y',ccode=payccode).last().cardtype
                    print('have payccode',cardtype)
                else:
                    payccode=''
                    cardtype=''

                vsdate = datetime.now().strftime("%Y%m%d")
                vstime = datetime.now().strftime('%H%M%S')
                ttype = cartitem.ttype
                vip = Vip.objects.get(company=company,uuid=vipuuid)
                psstatus='10'

                # hungitems = ExpenseHung.objects.filter(company=company, storecode=storecode, ttype_hung=ttype,
                #                                            stype_hung=cartitem.stype,
                #                                            hunguuid__valiflag_hung='Y',
                #                                            hunguuid__vsdate_hung=vsdate, hunguuid__vipuuid=vip,
                #                                            hunguuid__psstatus_hung=psstatus,
                #                                            hunguuid__ccode_hung=payccode, hunguuid__ttype_hung=ttype)
                # if len(hungitems)>0:
                #     expvstollhung = hungitems[0].transuuid
                # print('expvstollhung exists_2', expvstollhung.exptxserno_hung, expvstollhung.ttype_hung, cartitem.stype)

                # 赠送和正常的单子，分别挂在不同的单子上
                try:
                    expvstollhung = ExpenseHung.objects.filter(company=company, storecode=storecode, ttype_hung=ttype,
                                                           stype_hung=cartitem.stype,
                                                           hunguuid__valiflag_hung='Y',
                                                           hunguuid__vsdate_hung=vsdate, hunguuid__vipuuid=vip,
                                                           hunguuid__psstatus_hung =psstatus,
                                                           hunguuid__ccode_hung=payccode, hunguuid__ttype_hung=ttype)[0].hunguuid
                    print('expvstollhung exists',expvstollhung.exptxserno_hung, expvstollhung.ttype_hung, cartitem.stype)
                except:
                    expvstollhung = ExpvstollHung.objects.create(company=company, storecode=storecode, creater=ecode,
                                                        valiflag_hung='Y',
                                                        vsdate_hung=vsdate, vipuuid=vip, vcode_hung=vip.vcode,
                                                        ccode_hung=payccode,
                                                        cardtype_hung=cardtype, ttype_hung=ttype, psstatus_hung='10')
                    print('expvstollhung new',  expvstollhung.ttype_hung,cartitem.stype)
                # 赠送和正常的单子，合并在一个挂账单上
                # expvstollhung = ExpvstollHung.objects.get_or_create(company=company,storecode=storecode,creater=ecode,valiflag_hung='Y',
                #                                                     vsdate_hung=vsdate,vipuuid=vip,vcode_hung=vip.vcode,ccode_hung=payccode,
                #                                                     cardtype_hung=cardtype,ttype_hung=ttype,psstatus_hung='10')[0]

                if expvstollhung.exptxserno_hung==None:
                    exptxserno_hung =  GetSerno(company, storecode, 'hung')
                    expvstollhung.exptxserno_hung=exptxserno_hung
                else:
                    exptxserno_hung = expvstollhung.exptxserno_hung

                # hunguuid=str(expvstollhung.uuid).replace('-','')
                hunguuid = expvstollhung
                print('hunguuid=',hunguuid.uuid)
                if expvstollhung.totmount_hung==None:
                    totamount=0
                else:
                    totamount=expvstollhung.totmount_hung

                exists_items = ExpenseHung.objects.filter(company=company,storecode=storecode,exptxserno_hung=exptxserno_hung).order_by('-ditem_hung')
                if exists_items.count()>0:
                    # print('exists_ditems',exists_items)
                    last_item = exists_items[0]
                    print('last_item.ditem_hung',last_item.ditem_hung)
                    ditem=('0000'+str(int(last_item.ditem_hung)+1))[-4:]
                else:
                    ditem='0001'
                print('exptxserno=',exptxserno_hung,'ditem=',ditem,'srvcode=',cartitem.itemcode)

                expensehung = ExpenseHung.objects.create(company=company,storecode=storecode,creater=ecode,ttype_hung=cartitem.ttype,stype_hung=cartitem.stype,
                                                          hunguuid=hunguuid,exptxserno_hung=exptxserno_hung, ditem_hung=ditem,srvcode_hung=cartitem.itemcode,
                                                          s_qty_hung=cartitem.qty, s_price_hung=cartitem.price,secdisc_hung=cartitem.secdisc,
                                                          srvmondisc_hung=cartitem.mondisc,s_mount_hung=cartitem.amount,
                                                          pmcode_hung=cartitem.pmcode,asscode1_hung=cartitem.seccode,asscode2_hung=cartitem.thrcode,
                                                         dnote_hung=cartitem.remark)
                print(expensehung.srvcode_hung)
                expensehung.save()

                # 还欠处理
                if cartitem.stype =='E':
                    print('cartitem:',cartitem.uuid,cartitem.itemcode,cartitem.price, cartitem.planqty, cartitem.planamount, cartitem.payedamount,cartitem.oweamount,ecode)
                    earnestmoney = EarnestMoney.objects.create(company=company, storecode=storecode, creater=ecode, ttype=cartitem.ttype, itemcode=cartitem.itemcode,
                                                               hunguuid = expvstollhung,
                                                               price=cartitem.price,planqty=cartitem.planqty,planamount=cartitem.planamount,payedamount = cartitem.payedamount,
                                                               oweamount=cartitem.oweamount, remark=cartitem.remark,
                                                               ecode=ecode,status='10'
                                                               )
                    # earnestmoney.price = cartitem.price
                    # earnestmoney.planqty=cartitem.planqty
                    # earnestmoney.planamount=cartitem.planamount
                    # earnestmoney.payedamount = cartitem.payedamount
                    # earnestmoney.oweamount = cartitem.oweamount
                    # print('earnestmoney.uuid:',earnestmoney.uuid)
                    earnestmoney.save()

                totamount=totamount + expensehung.s_mount_hung
                expvstollhung.vstime_hung=vstime
                expvstollhung.totmount_hung=totamount
                expvstollhung.vcode_hung=vip.vcode
                expvstollhung.save()

                cartitem.status='20'
                cartitem.save()

        content = {
            "statusCode": '200',
            "error": False,
            "msg": '开单完成'
        }
        # return HttpResponse(content, content_type="application/json")

    return HttpResponse(content, content_type="application/json")

@csrf_exempt
@transaction.atomic
def ServieceHung(request):
    if request.method == 'POST':
        data= json.loads(request.GET['param'])
        print('request param:',data)
        company = data['company']
        storecode= data['storecode']
        ecode= data['ecode']
        # vcode = data['vcode']
        vipuuid = uuid.UUID(data['vipuuid'])
        payccode = data['payccode']
        stype =  data['stype']
        ttype = data['ttype']
        psstatus='10'
        # cardtype = data['cardtype']
        # cardtypeuuid = data['cardtypeuuid']
        # newcardtype=data['newcardtype']
        itemcode=data['itemcode']
        qty = data['qty']
        price = data['price']
        secdisc = data['secdisc']
        mondisc = data['mondisc']
        amount=data['amount']
        try:
            leftmoney = data['leftmoney']
        except:
            leftmoney=0

        # leftqty = data['leftqty']
        pmcode=data['pmcode']
        seccode=data['seccode']
        thrcode=data['thrcode']
        try:
            promotionsid=data['promotionsid']
        except:
            promotionsid='0'

        vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
        vstime = datetime.strftime(datetime.now(),'%H%M%S')
        vip = Vip.objects.get(uuid=vipuuid)

        if len(payccode)>0:
            try:
                paycard=Cardinfo.objects.filter(company=company,status='O',ccode=payccode).filter()
                paycardtype=paycard.cardtype
            except:
                paycardtype=''
        else:
            payccode=''
            paycardtype=''

        print('expvstoll_hung info:',company,storecode,vsdate,vip.uuid,vip.vcode,psstatus,payccode,ttype,itemcode)
        try:
            # 赠送和正常的单子，分别挂在不同的单子上
            expvstollhung = ExpenseHung.objects.filter(company=company,storecode=storecode,ttype_hung=ttype, stype_hung=stype,transuuid__valiflag_hung='Y',
                                                            transuuid__vsdate_hung=vsdate,transuuid__vipuuid=vip, transuuid__psstatus_hung=psstatus,
                                                            transuuid__ccode_hung=payccode,transuuid__ttype_hung=ttype)[0].transuuid
            # 赠送和正常的单子，合并在一个挂账单上
            # expvstollhung = ExpvstollHung.objects.filter(company=company,storecode=storecode,valiflag_hung='Y',
            #                                                 vsdate_hung=vsdate,vipuuid=vip, psstatus_hung=psstatus,ccode_hung=payccode,ttype_hung=ttype)[0]
            print('expvstollhung',expvstollhung.ttype_hung,expvstollhung.ccode_hung)
            if expvstollhung.exptxserno_hung==None:
                exptxserno_hung =  GetSerno(company, storecode, 'hung')
                expvstollhung.exptxserno_hung=exptxserno_hung
            else:
                exptxserno_hung = expvstollhung.exptxserno_hung
            print('get exptxserno_hung', exptxserno_hung,expvstollhung)
        except:
            expvstollhung = ExpvstollHung.objects.create(company=company,storecode=storecode,valiflag_hung='Y',
                                                            vsdate_hung=vsdate,vipuuid=vip, psstatus_hung=psstatus,ccode_hung=payccode,ttype_hung=ttype)
            exptxserno_hung = GetSerno(company, storecode, 'hung')
            print('create exptxserno_hung',exptxserno_hung)
            expvstollhung.vstime_hung=vstime
            expvstollhung.exptxserno_hung=exptxserno_hung
            expvstollhung.vcode_hung=vip.vcode
            expvstollhung.cardtype_hung=paycardtype

        print('exptxserno_hung',exptxserno_hung,expvstollhung)

        hungserno = ''.join(str(expvstollhung.uuid).split('-'))
        print('hunguuid:',hungserno)
        try:
            hungitems=ExpenseHung.objects.filter(company=company,hunguuid=expvstollhung.uuid).order_by(-'ditem_hung')
            ditem = ('0000'+ str(int( hungitems.ditem_hung ) + 1))[:4]
        except:
            ditem='0001'
        print(ditem)
        expensehung = ExpenseHung.objects.create(
            company=company,storecode=storecode,
            exptxserno_hung =exptxserno_hung,
            ditem_hung=ditem,
            ttype_hung = ttype,
            stype_hung = stype,
            srvcode_hung = itemcode,
            s_qty_hung = qty,
            s_price_hung = price,
            s_mount_hung = amount,
            srvmondisc_hung=mondisc,
            secdisc_hung=secdisc,
            # addvamoney_hung=leftmoney,
            pmcode_hung = pmcode,
            asscode1_hung = seccode,
            asscode2_hung = thrcode,
            hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
        )

        if expvstollhung.totmount_hung==None:
            expvstollhung.totmount_hung=0

        if amount==None:
            amount=0

        expvstollhung.totmount_hung = expvstollhung.totmount_hung + amount
        expvstollhung.save()
        expensehung.save()

        content ={
            "statusCode":'200',
            "error":  False,
            "msg": '开单完成'
        }
        # return HttpResponse(content, content_type="application/json")
        return JsonResponse(content, content_type="application/json")
    else:
        return HttpResponse("400", content_type="application/json")

@csrf_exempt
@transaction.atomic
def goodsHung(request):
    if request.method == 'POST':
                data= json.loads(request.GET['param'])
                company = data['company']
                storecode= data['storecode']
                ecode= data['ecode']
                vcode = data['vcode']
                vipuuid = data['vipuuid']
                payccode = data['payccode']
                stype =  data['stype']
                ttype = data['ttype']
                psstatus='10'
                # cardtype = data['cardtype']
                # cardtypeuuid = data['cardtypeuuid']
                # newcardtype=data['newcardtype']
                itemcode=data['itemcode']
                qty = data['qty']
                price = data['price']
                secdisc = data['secdisc']
                mondisc = data['mondisc']
                amount=data['amount']
                leftmoney = data['leftmoney']
                # leftqty = data['leftqty']
                pmcode=data['pmcode']
                seccode=data['seccode']
                thrcode=data['thrcode']
                promotionsid=data['promotionsid']

                vsdate = datetime.strftime(datetime.now(), '%Y%m%d')
                vstime = datetime.strftime(datetime.now(),'%H%M%S')
                exptxserno_hung = GetSerno(company,storecode,'hung')

                vip = Vip.objects.get(uuid=vipuuid)

                paycardtype=''
                if len(payccode)>0:
                    try:
                        paycard=Cardinfo.objects.filter(company=company,status='O',ccode=payccode).filter()
                        paycardtype=paycard.cardtype
                    except:
                        paycardtype=''


                expvstollhung = ExpvstollHung.objects.get_or_create(company=company,storecode=storecode,
                                                                    vsdate_hung=vsdate,vipuuid=vip, psstatus=psstatus,ccode_hung=payccode,ttype_hung=ttype)[0]
                expvstollhung.vstime_hung=vstime
                expvstollhung.exptxserno_hung=expvstollhung.exptxserno_hung
                expvstollhung.vcode_hung=vcode
                expvstollhung.cardtype_hung=paycardtype


                hungserno = ''.join(str(expvstollhung.uuid).split('-'))
                print(hungserno)
                try:
                    hungitems=ExpenseHung.objects.filter(company=company,hunguuid=expvstollhung.uuid).order_by(-'ditem_hung')
                    ditem = ('0000'+ str(int( hungitems.ditem_hung ) + 1))[:4]
                except:
                    ditem='0001'
                print(ditem)
                expensehung = ExpenseHung.objects.create(
                    company=company,storecode=storecode,
                    exptxserno_hung =exptxserno_hung,
                    ditem_hung=ditem,
                    ttype_hung = ttype,
                    stype_hung = stype,
                    srvcode_hung = itemcode,
                    s_qty_hung = qty,
                    s_price_hung = price,
                    s_mount_hung = amount,
                    srvmondisc_hung=mondisc,
                    secdisc_hung=secdisc,
                    # addvamoney_hung=leftmoney,
                    pmcode_hung = pmcode,
                    asscode1_hung = seccode,
                    asscode2_hung = thrcode,
                    hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
                )

                expvstollhung.save()
                expensehung.save()
        # except:
        #     return HttpResponse("501",content_type="application/json")

    # return $this->ajaxReturn(array('error' = > true, 'msg' = > '学号重复'));
                content ={
                    "statusCode":'200',
                    "error":  False,
                    "msg": '开单完成'
                }
                # return HttpResponse(content, content_type="application/json")
                return JsonResponse(content, content_type="application/json")
    else:
        return HttpResponse("400", content_type="application/json")


def _hung_line_ttypename(ttype):
    return {'S': '服务', 'G': '商品', 'C': '售卡', 'I': '充值'}.get((ttype or '').strip(), '')


def _hung_line_stypename(stype):
    st = (stype or '').strip()
    if st == 'N':
        return '正常'
    if st == 'P':
        return '赠送'
    return ''


def _paymode_pname_by_pcode(company, pcode):
    """按付款方式编码查中文名称，多档兜底。"""
    pcode = (pcode or '').strip()
    if not pcode:
        return ''
    qs_chain = (
        Paymode.objects.filter(company=company, pcode=pcode, flag='Y'),
        Paymode.objects.filter(company=company, pcode=pcode),
        Paymode.objects.filter(pcode=pcode),
    )
    for qs in qs_chain:
        pm = qs.values_list('pname', flat=True).first()
        if pm:
            return str(pm).strip()
    return ''


def _cardsupertype_resolve_paytype(company, cs, stype_hung):
    """
    cardsupertype → paytype / paytypename：
    仅 stype_hung=='P' 用 present_pcode；=='N' 用 normal_pcode。
    二者任一为空或长度为 0 时用 pcode；最后按 paytype 查 paymode.pname。
    其它 stype 仅用 pcode。
    """
    if not cs:
        return '', ''
    st = (stype_hung or '').strip()
    fallback = (getattr(cs, 'pcode', None) or '').strip()
    cand = ''
    if st == 'P':
        cand = (getattr(cs, 'present_pcode', None) or '').strip()
    elif st == 'N':
        cand = (getattr(cs, 'normal_pcode', None) or '').strip()
    paytype = cand if len(cand) > 0 else fallback
    paytypename = _paymode_pname_by_pcode(company, paytype)
    return paytype, paytypename


def _cardtype_from_cardinfo(company, ci):
    """
    优先 cardinfo.cardtype 编码 → cardtype 表（再取 suptype），避免仅依赖 FK 与字段不一致。
    """
    if not ci:
        return None, ''
    ctype_code = (getattr(ci, 'cardtype', None) or '').strip()
    ct = None
    if ctype_code:
        ct = (
            Cardtype.objects.filter(company=company, cardtype=ctype_code)
            .order_by('-last_modified')
            .first()
        )
        if not ct:
            ct = (
                Cardtype.objects.filter(company=ci.company, cardtype=ctype_code)
                .order_by('-last_modified')
                .first()
            )
    if not ct and getattr(ci, 'cardtypeuuid_id', None):
        ct = ci.cardtypeuuid
        if ct and not ctype_code:
            ctype_code = (getattr(ct, 'cardtype', None) or '').strip()
    return ct, ctype_code


def _cardsupertype_by_suptype(company, suptype_key, card_company=None):
    """
    用 cardtype.suptype 与 cardsupertype.code 严格一致匹配（仅 strip 首尾空白，不做编码变形）。
    同一 code 可能分属不同 company，依次尝试请求 company、卡所属 company、默认公司等。
    """
    sk = (suptype_key or '').strip()
    if not sk:
        return None
    co_list = []
    for c in (company, card_company, common.constants.COMPANYID):
        if c and c not in co_list:
            co_list.append(c)
    try:
        demo = getattr(common.constants, 'DEMO_COMPANY', None)
        if demo and demo not in co_list:
            co_list.append(demo)
    except Exception:
        pass
    for co in co_list:
        for kw in (
            {'company': co, 'flag': 'Y', 'code': sk},
            {'company': co, 'code': sk},
        ):
            cs = Cardsupertype.objects.filter(**kw).first()
            if cs:
                return cs
    for kw in (
        {'flag': 'Y', 'code': sk},
        {'code': sk},
    ):
        cs = Cardsupertype.objects.filter(**kw).first()
        if cs:
            return cs
    return None


def _resolve_paycard_plan_info(company, payccode, cardtype_hung, stype_hung):
    ccode = (payccode or '').strip()
    cardtype_code = ''
    cardtype_name = ''
    paytype = ''
    paytypename = ''
    try:
        ct = None
        ci = None
        if ccode:
            ci = (
                Cardinfo.objects.filter(company=company, ccode=ccode, flag='Y')
                .select_related('cardtypeuuid')
                .order_by('-last_modified')
                .first()
            )
            if not ci:
                ci = (
                    Cardinfo.objects.filter(company=company, ccode=ccode)
                    .select_related('cardtypeuuid')
                    .order_by('-last_modified')
                    .first()
                )
            if not ci:
                ci = (
                    Cardinfo.objects.filter(ccode=ccode)
                    .select_related('cardtypeuuid')
                    .order_by('-last_modified')
                    .first()
                )
            if ci:
                ct, cardtype_code = _cardtype_from_cardinfo(company, ci)
                if ct:
                    cardtype_name = (getattr(ct, 'cardname', None) or '').strip()
        hung_ctype = (cardtype_hung or '').strip()
        if not cardtype_code and hung_ctype:
            cardtype_code = hung_ctype
        if hung_ctype and not ct:
            ct_fb = (
                Cardtype.objects.filter(company=company, cardtype=hung_ctype)
                .order_by('-last_modified')
                .first()
            )
            if ct_fb:
                ct = ct_fb
                if not cardtype_name:
                    cardtype_name = (ct_fb.cardname or '').strip()
        elif not cardtype_name and hung_ctype:
            nm = (
                Cardtype.objects.filter(company=company, cardtype=hung_ctype)
                .values_list('cardname', flat=True)
                .first()
            )
            if nm:
                cardtype_name = str(nm).strip()
        if ct:
            suptype_key = (ct.suptype or '').strip()
            card_co = None
            if ci:
                card_co = getattr(ci, 'company', None) or None
            if not card_co:
                card_co = getattr(ct, 'company', None) or None
            cs = _cardsupertype_by_suptype(company, suptype_key, card_company=card_co)
            if cs:
                paytype, paytypename = _cardsupertype_resolve_paytype(company, cs, stype_hung)
    except Exception:
        pass
    return {
        'paycardtype': cardtype_code or (cardtype_hung or ''),
        'paycardtypename': cardtype_name or cardtype_code or (cardtype_hung or ''),
        'paytype': paytype,
        'paytypename': paytypename,
    }


def _resolve_hung_itemname(company, ttype, itemcode):
    """与库函数 F_Getnamebysrvcode 一致：按类别解析服务/商品/卡名称。"""
    ic = (itemcode or '').strip()
    if not ic:
        return ''
    t = (ttype or '').strip()
    try:
        if t == 'S':
            name = (
                Serviece.objects.filter(company=company, flag='Y', svrcdoe=ic)
                .values_list('svrname', flat=True)
                .first()
            )
            return (name or ic or '').strip() or ic
        if t == 'G':
            name = (
                Goods.objects.filter(company=company, flag='Y', gcode=ic)
                .values_list('gname', flat=True)
                .first()
            )
            return (name or ic or '').strip() or ic
        if t in ('C', 'I'):
            ct = (
                Cardtype.objects.filter(company=company, flag='Y', cardtype=ic)
                .values_list('cardname', flat=True)
                .first()
            )
            if ct:
                return ct.strip()
            ci = (
                Cardinfo.objects.filter(company=company, flag='Y', ccode=ic)
                .select_related('cardtypeuuid')
                .first()
            )
            if ci and ci.cardtypeuuid_id and ci.cardtypeuuid:
                cn = ci.cardtypeuuid.cardname
                if cn:
                    return cn.strip()
    except Exception:
        pass
    return ic


@csrf_exempt
def get_hung_byvipuuid(request):
    """
    某会员未完成挂单明细。原 SQL 依赖 F_Getnamebysrvcode，现改为 ORM + 本地解析名称。
    """
    company = request.GET.get('company', common.constants.COMPANYID)
    storecode = request.GET.get('storecode', '88')
    vipuuid = request.GET.get('vipuuid', '')
    try:
        v_uuid = _parse_uuid_loose(vipuuid)
    except (ValueError, TypeError, AttributeError):
        return HttpResponse(
            json.dumps([], cls=DjangoJSONEncoder), content_type='application/json'
        )

    open_status = ('10', '20', '30', '40', '50')
    hung_list = (
        ExpvstollHung.objects.filter(
            company=company,
            storecode=storecode,
            flag='Y',
            valiflag_hung='Y',
            vipuuid=v_uuid,
            psstatus_hung__in=open_status,
        ).order_by('-vsdate_hung', '-vstime_hung', '-create_time', '-exptxserno_hung')
    )

    rows = []
    for a in hung_list:
        for b in (
            ExpenseHung.objects.filter(hunguuid=a.uuid, flag='Y').order_by('ditem_hung')
        ):
            ttype = b.ttype_hung or ''
            icode = b.srvcode_hung or ''
            rows.append(
                {
                    'exptxserno': a.exptxserno_hung or '',
                    'hunguuid': str(a.uuid),
                    'psstatus': a.psstatus_hung or '',
                    'vsdate': a.vsdate_hung or '',
                    # 计划付款信息：优先直接取挂单头 ExpvstollHung
                    'payccode': a.ccode_hung or '',
                    **_resolve_paycard_plan_info(
                        company, a.ccode_hung, a.cardtype_hung, b.stype_hung
                    ),
                    'itemuuid': str(b.uuid),
                    'item': b.ditem_hung or '',
                    'ttype': ttype,
                    'stype': b.stype_hung or '',
                    'ttypename': _hung_line_ttypename(ttype),
                    'stypename': _hung_line_stypename(b.stype_hung),
                    'itemcode': icode,
                    'itemname': _resolve_hung_itemname(company, ttype, icode),
                    'price': b.s_price_hung,
                    'qty': b.s_qty_hung,
                    'secdisc': b.secdisc_hung,
                    'mondisc': b.srvmondisc_hung,
                    'amount': b.s_mount_hung,
                    'payamount': b.s_mount_hung,
                    'payqty': b.s_qty_hung,
                    'pmcode': b.pmcode_hung,
                    'seccode': b.asscode1_hung,
                    'thrcode': b.asscode2_hung,
                    'remark': b.dnote_hung,
                }
            )

    return HttpResponse(
        json.dumps(rows, cls=DjangoJSONEncoder), content_type='application/json'
    )

def _format_hung_order_time(h):
    """expvstoll_hung 开单时间：业务日期+时间，否则用 create_time。"""
    vd = (h.vsdate_hung or '').strip()
    vt = (h.vstime_hung or '').strip()
    if len(vd) == 8 and vt:
        vt_norm = vt.ljust(6, '0')[:6]
        try:
            dt = datetime.strptime(vd + vt_norm, '%Y%m%d%H%M%S')
            return dt.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            try:
                dt = datetime.strptime(vd + vt_norm[:4] + '00', '%Y%m%d%H%M')
                return dt.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                pass
    if getattr(h, 'create_time', None):
        return h.create_time.strftime('%Y-%m-%d %H:%M')
    return vd or ''


@csrf_exempt
def get_instore_vips(request):
    """
    未结账客人：已开单（有效挂单）且尚未结账（psstatus_hung 未到 70）的列表。
    与 get_hung_byvipuuid 中未完成单状态一致：10~50；另含 60 挂账（仍未结清）。
    附加：项目条数、开单时间、开单员工（ecode_hung 对应 empl 姓名）。
    """
    try:
        company = request.GET['company']
    except Exception:
        company = common.constants.COMPANYID
    try:
        storecode = request.GET['storecode']
    except Exception:
        storecode = '88'
    open_status = ('10', '20', '30', '40', '50', '60')
    qs = (
        ExpvstollHung.objects.filter(
            company=company,
            storecode=storecode,
            flag='Y',
            valiflag_hung='Y',
            psstatus_hung__in=open_status,
        )
        .select_related('vipuuid')
        .annotate(
            item_count=Count('expensehung', filter=Q(expensehung__flag='Y'))
        )
        .order_by('-create_time')
    )

    ecodes = []
    for h in qs:
        e = (h.ecode_hung or '').strip()
        if e:
            ecodes.append(e)
    empl_by_ecode = {}
    if ecodes:
        for em in Empl.objects.filter(company=company, ecode__in=list(set(ecodes))).only(
            'ecode', 'ename', 'cname'
        ):
            empl_by_ecode[em.ecode] = (em.ename or em.cname or em.ecode or '').strip()

    rows = []
    for h in qs:
        vip = h.vipuuid
        tm = h.totmount_hung
        try:
            tot = float(tm) if tm is not None else 0
        except (TypeError, ValueError):
            tot = 0
        ecode = (h.ecode_hung or '').strip()
        empl_name = empl_by_ecode.get(ecode) if ecode else ''
        if ecode and not empl_name:
            empl_name = ecode
        ic = getattr(h, 'item_count', 0) or 0
        rows.append({
            'hunguuid': str(h.uuid),
            'exptxserno': h.exptxserno_hung or '',
            'psstatus': h.psstatus_hung or '',
            'vsdate': h.vsdate_hung or '',
            'totmount': tot,
            'ttype': h.ttype_hung or '',
            'vipuuid': str(vip.uuid) if vip else '',
            'vname': (vip.vname if vip else '') or '',
            'vcode': (vip.vcode if vip else '') or '',
            'mtcode': (vip.mtcode if vip else '') or '',
            'item_count': int(ic),
            'order_time': _format_hung_order_time(h),
            'ecode_hung': ecode,
            'order_empl': empl_name,
        })
    return JsonResponse(rows, safe=False)

@csrf_exempt
def get_hungitem(request):
    company = request.GET.get('company', common.constants.COMPANYID)
    storecode = request.GET.get('storecode', '88')
    item_uuid_raw = request.GET.get('uuid', '')

    try:
        item_uuid = _parse_uuid_loose(item_uuid_raw)
    except Exception:
        return JsonResponse([], safe=False)

    b = (
        ExpenseHung.objects.filter(
            company=company,
            storecode=storecode,
            flag='Y',
            uuid=item_uuid,
        )
        .select_related('hunguuid')
        .first()
    )
    if not b or not b.hunguuid:
        return JsonResponse([], safe=False)
    a = b.hunguuid
    ttype = b.ttype_hung or ''
    icode = b.srvcode_hung or ''
    row = {
        'exptxserno': b.exptxserno_hung or '',
        'itemuuid': str(b.uuid),
        'item': b.ditem_hung or '',
        'ttype': ttype,
        'stype': b.stype_hung or '',
        'ttypename': _hung_line_ttypename(ttype),
        'stypename': _hung_line_stypename(b.stype_hung),
        'itemcode': icode,
        'itemname': _resolve_hung_itemname(company, ttype, icode),
        'price': b.s_price_hung,
        'qty': b.s_qty_hung,
        'secdisc': b.secdisc_hung,
        'mondisc': b.srvmondisc_hung,
        'amount': b.s_mount_hung,
        "payccode": a.ccode_hung or "",
        "paycardtype": a.cardtype_hung or "",
        "paycardtypename": _resolve_hung_itemname(company, "C", a.cardtype_hung or "") if a.cardtype_hung else "",
        "paytype": "",
        "paytypename": "",
        'pmcode': b.pmcode_hung,
        'seccode': b.asscode1_hung,
        'thrcode': b.asscode2_hung,
        'psstatus': a.psstatus_hung or '',
        'remark': b.dnote_hung,
    }
    return JsonResponse([row], safe=False)

@csrf_exempt
def update_hungitem(request):
    try:
        company=request.GET['company']
    except:
        company='yfy'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='88'

    try:
        uuid = request.GET['uuid']
    except:
        uuid=''
    print('expense uuid:',uuid)

    hungitem = ExpenseHung.objects.get(company=company,storecode=storecode,uuid=uuid)
    hunguuid = hungitem.hunguuid

    try:
        qty = request.GET['qty']
    except:
        qty = hungitem.s_qty_hung

    hungitem.s_qty_hung=qty


    try:
        price = request.GET['price']
    except:
        price = hungitem.s_price_hung
    hungitem.s_price_hung=price

    try:
        secdisc = request.GET['secdisc']
    except:
        secdisc=hungitem.secdisc_hung
    hungitem.secdisc_hung=secdisc

    try:
        mondisc = request.GET['mondisc']
    except:
        mondisc=hungitem.srvmondisc_hung
    hungitem.srvmondisc_hung=mondisc

    try:
        amount = request.GET['amount']
    except:
        amount=hungitem.s_mount_hung
    hungitem.s_mount_hung=amount

    try:
        pmcode = request.GET['pmcode']
    except:
        pmcode=hungitem.pmcode_hung
    hungitem.pmcode_hung=pmcode

    try:
        seccode = request.GET['seccode']
    except:
        seccode=hungitem.asscode1_hung
    hungitem.asscode1_hung=seccode

    try:
        thrcode = request.GET['thrcode']
    except:
        thrcode=hungitem.asscode2_hung
    hungitem.asscode2_hung=thrcode

    try:
        stype = request.GET['stype']
    except:
        stype=hungitem.stype_hung
    hungitem.stype_hung=stype

    try:
        flag = request.GET['flag']
    except:
        flag=hungitem.flag
    hungitem.flag=flag

    try:
        ttype=request.GET['ttype']
    except:
        ttype='S'
    hungitem.save()

    try:
        remark = request.GET['remark']
    except:
        remark=''
    hungitem.dnote_hung=remark
    hungitem.save()


    if ttype=='C' and  flag=='N':
        print('in ')
        try:
            cardinfo=Cardinfo.objects.get(company=company,ccode=hungitem.srvcode_hung,status='P')
            cardinfo.status='C'
            cardinfo.save()
            hunguuid.valiflag_hung='N'
            hunguuid.save()
        except Exception as e:
            print('void cardinfo',hungitem.srvcode_hung,e)

    hungitems = ExpenseHung.objects.filter(company=company,hunguuid=hunguuid,flag='Y')
    if len(hungitems)==0:
        hunguuid.valiflag_hung='N'
        hunguuid.save()


    return HttpResponse('200', content_type="application/json")

def update_hung_byuuid(request):
    try:
        company=request.GET['company']
    except:
        company='yfy'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='88'

    try:
        hunguuid = request.GET['hunguuid']

    except:
        hunguuid = ''

    try:
        itemuuid = request.GET['itemuuid']
    except:
        itemuuid =''

    if len(hunguuid)>0:
        hungs = ExpvstollHung.objects.get(company=company,storecode=storecode,uuid=hunguuid)
        try:
            psstatus = request.GET['psstatus']
            hungs.psstatus_hung=psstatus
            hungs.save()
            return HttpResponse('200', content_type="application/json")
        except:
            psstatus= hungs.psstatus_hung


        if len(itemuuid)>0:
            hungitems = ExpenseHung.objects.get(company=company,storecode=storecode,hunguuid=hunguuid,uuid=itemuuid)


@csrf_exempt
@transaction.atomic
def checkout_hungs(request):
    """
    会员挂单结账：
    - 仅允许结算未完成挂单（10~60）
    - 计次卡：余次充足才可结账，按选中挂单总次数扣减 leftqty
    - 计费卡：余额充足才可结账，按选中挂单总金额扣减 leftmoney
    """
    try:
        payload = _parse_request_param_json(request)
    except Exception:
        return JsonResponse({'ok': False, 'message': '参数格式错误'}, status=400)

    company = payload.get('company') or request.GET.get('company') or common.constants.COMPANYID
    storecode = payload.get('storecode') or request.GET.get('storecode') or '88'
    vipuuid_raw = payload.get('vipuuid') or request.GET.get('vipuuid') or ''
    hunguuids_raw = payload.get('hunguuids') or []
    extra_payments = payload.get('extra_payments') or []
    extra_paymode = (payload.get('extra_paymode') or '').strip()
    try:
        extra_pay_amount = Decimal(str(payload.get('extra_pay_amount') or '0'))
    except Exception:
        extra_pay_amount = Decimal('0')
    if extra_pay_amount < 0:
        extra_pay_amount = Decimal('0')
    if not isinstance(extra_payments, list):
        extra_payments = []

    if not vipuuid_raw:
        return JsonResponse({'ok': False, 'message': '缺少会员参数'}, status=400)
    if not isinstance(hunguuids_raw, list) or len(hunguuids_raw) == 0:
        return JsonResponse({'ok': False, 'message': '请至少选择一笔开单'}, status=400)

    try:
        vipuuid = _parse_uuid_loose(vipuuid_raw)
    except Exception:
        return JsonResponse({'ok': False, 'message': '会员参数无效'}, status=400)

    hunguuids = []
    for h in hunguuids_raw:
        try:
            hunguuids.append(_parse_uuid_loose(h))
        except Exception:
            continue
    if not hunguuids:
        return JsonResponse({'ok': False, 'message': '结账单据参数无效'}, status=400)

    open_status = ('10', '20', '30', '40', '50', '60')
    try:
        hungs = list(
            ExpvstollHung.objects.select_for_update().filter(
                company=company,
                storecode=storecode,
                flag='Y',
                valiflag_hung='Y',
                vipuuid=vipuuid,
                psstatus_hung__in=open_status,
                uuid__in=hunguuids,
            )
        )
        if len(hungs) != len(hunguuids):
            return JsonResponse({'ok': False, 'message': '部分开单已失效或不可结账'}, status=400)

        grouped = {}
        total_amount = Decimal('0')
        total_qty = Decimal('0')
        h_stype_map = {}
        for eh in ExpenseHung.objects.filter(company=company, hunguuid__in=hunguuids, flag='Y').only('hunguuid', 'stype_hung', 'ditem_hung').order_by('ditem_hung'):
            k = str(eh.hunguuid_id)
            if k not in h_stype_map:
                h_stype_map[k] = eh.stype_hung
        for h in hungs:
            ccode = (h.ccode_hung or '').strip()
            h_stype = h_stype_map.get(str(h.uuid), 'N')
            payinfo = _resolve_paycard_plan_info(company, ccode, h.cardtype_hung, h_stype)
            pcode = (payinfo.get('paytype') or '').strip()
            p_iscash = ''
            if pcode:
                pm = (
                    Paymode.objects.filter(company=company, pcode=pcode)
                    .values_list('iscash', flat=True)
                    .first()
                )
                p_iscash = (pm or '').strip()
            if not p_iscash:
                # 无法映射付款方式时按非卡付类处理，避免误走卡号校验导致 400
                p_iscash = '1'
            grp_key = ccode + '|' + pcode + '|' + p_iscash
            if grp_key not in grouped:
                grouped[grp_key] = {
                    'ccode': ccode,
                    'pcode': pcode,
                    'iscash': p_iscash,
                    'amount': Decimal('0'),
                    'qty': Decimal('0'),
                    'hungs': [],
                }
            grouped[grp_key]['amount'] += Decimal(h.sumamount or 0)
            grouped[grp_key]['qty'] += Decimal(h.sumqty or 0)
            grouped[grp_key]['hungs'].append(h)
            total_amount += Decimal(h.sumamount or 0)
            total_qty += Decimal(h.sumqty or 0)

        amount_deductions = []
        total_extra_due = Decimal('0')
        noncard_due = Decimal('0')
        h_card_alloc = {}
        h_noncard_need = {}
        h_paymeta = {}
        for _, bucket in grouped.items():
            ccode = bucket['ccode']
            pcode = bucket['pcode']
            iscash = bucket['iscash']
            for hh in bucket['hungs']:
                h_paymeta[str(hh.uuid)] = {'ccode': ccode, 'pcode': pcode, 'iscash': iscash}
            # 非卡付类（iscash=1/2）不校验卡号和卡余额
            if iscash in ('1', '2'):
                noncard_due += bucket['amount']
                for hh in bucket['hungs']:
                    h_noncard_need[str(hh.uuid)] = Decimal(hh.sumamount or 0)
                continue
            # 卡付类（iscash=0 或未知）才走卡号/余额校验
            if not ccode:
                return JsonResponse({'ok': False, 'message': '卡付类结账存在未设置付款卡号的开单'}, status=400)
            paycard = (
                Cardinfo.objects.select_for_update()
                .select_related('cardtypeuuid')
                .filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            if not paycard:
                return JsonResponse({'ok': False, 'message': '付款卡不存在或不属于该客人：' + ccode}, status=400)

            comptype = ''
            if paycard.cardtypeuuid and paycard.cardtypeuuid.comptype:
                comptype = paycard.cardtypeuuid.comptype
            if comptype not in ('times', 'amount'):
                return JsonResponse({'ok': False, 'message': '付款卡不支持结账：' + ccode}, status=400)

            if comptype == 'times':
                leftqty = Decimal(paycard.leftqty or 0)
                need_qty = bucket['qty']
                if leftqty < need_qty:
                    lack = need_qty - leftqty
                    return JsonResponse(
                        {
                            'ok': False,
                            'code': 'INSUFFICIENT_TIMES',
                            'message': '付款卡余次不足，无法结账：' + ccode,
                            'payccode': ccode,
                            'need_qty': float(lack),
                            'left_qty': float(leftqty),
                            'total_qty': float(need_qty),
                        },
                        status=400,
                    )
                paycard.leftqty = leftqty - need_qty
                paycard.save(update_fields=['leftqty'])
                for hh in bucket['hungs']:
                    h_amt = Decimal(hh.sumamount or 0)
                    h_card_alloc[str(hh.uuid)] = h_amt
                    h_noncard_need[str(hh.uuid)] = Decimal('0')
            else:
                leftmoney = Decimal(paycard.leftmoney or 0)
                need_amount = bucket['amount']
                if leftmoney < need_amount:
                    lack = need_amount - leftmoney
                    total_extra_due += lack
                    amount_deductions.append((paycard, leftmoney))
                    remain = leftmoney
                    for hh in bucket['hungs']:
                        h_amt = Decimal(hh.sumamount or 0)
                        card_part = h_amt if remain >= h_amt else remain
                        if card_part < 0:
                            card_part = Decimal('0')
                        remain = remain - card_part
                        h_card_alloc[str(hh.uuid)] = card_part
                        h_noncard_need[str(hh.uuid)] = h_amt - card_part
                else:
                    amount_deductions.append((paycard, need_amount))
                    for hh in bucket['hungs']:
                        h_amt = Decimal(hh.sumamount or 0)
                        h_card_alloc[str(hh.uuid)] = h_amt
                        h_noncard_need[str(hh.uuid)] = Decimal('0')

        declared_total = Decimal('0')
        for ep in extra_payments:
            pcode = str(ep.get('pcode') or '').strip()
            if not pcode:
                continue
            try:
                amt = Decimal(str(ep.get('amount') or '0'))
            except Exception:
                amt = Decimal('0')
            if amt <= 0:
                continue
            pm = (
                Paymode.objects.filter(company=company, flag='Y', visibleflag='Y', pcode=pcode)
                .exclude(iscash='0')
                .first()
            )
            if pm:
                declared_total += amt

        # 兼容旧参数
        if declared_total <= 0 and extra_pay_amount > 0 and extra_paymode:
            pm = (
                Paymode.objects.filter(company=company, flag='Y', visibleflag='Y', pcode=extra_paymode)
                .exclude(iscash='0')
                .first()
            )
            if pm:
                declared_total = extra_pay_amount

        required_noncard = noncard_due + total_extra_due
        auto_added_amount = Decimal('0')
        auto_added_pcode = ''
        if required_noncard > 0:
            if declared_total < required_noncard:
                # 第一种付款方式不足时，自动补第二种默认付款方式（现金优先）
                auto_added_amount = required_noncard - declared_total
                dpm = (
                    Paymode.objects.filter(company=company, flag='Y', visibleflag='Y')
                    .exclude(iscash='0')
                    .order_by('pcode')
                    .first()
                )
                if dpm:
                    auto_added_pcode = dpm.pcode or ''
                declared_total = required_noncard

        for paycard, deduct_amount in amount_deductions:
            leftmoney = Decimal(paycard.leftmoney or 0)
            real_deduct = deduct_amount if deduct_amount <= leftmoney else leftmoney
            paycard.leftmoney = leftmoney - real_deduct
            paycard.save(update_fields=['leftmoney'])

        # 组装非卡付款池（支持最多两种，第二种可自动补齐）
        extra_pool = []
        for ep in extra_payments:
            pcode = str(ep.get('pcode') or '').strip()
            try:
                amt = Decimal(str(ep.get('amount') or '0'))
            except Exception:
                amt = Decimal('0')
            if pcode and amt > 0:
                extra_pool.append({'pcode': pcode, 'amount': amt})
        if auto_added_amount > 0:
            extra_pool.append({'pcode': auto_added_pcode or extra_paymode or common.constants.DEFAULT_NORMAL_PCODE, 'amount': auto_added_amount})

        now = datetime.now()
        vsdate_now = now.strftime('%Y%m%d')
        vstime_now = now.strftime('%H%M%S')
        created_exptxsernos = []
        created_toll_count = 0
        created_cardhistory_count = 0

        # 落库：expvstoll / expense / toll
        for h in hungs:
            h_id = str(h.uuid)
            card_out_changes = {}
            exptxserno = GetSerno(company, storecode, 'EXPVSTOLL')
            created_exptxsernos.append(exptxserno)
            trans = Expvstoll.objects.create(
                company=company,
                storecode=storecode,
                vipuuid=h.vipuuid,
                vcode=h.vcode_hung or '',
                ccode=h.ccode_hung or '',
                cardtype=h.cardtype_hung or '',
                exptxserno=exptxserno,
                vsdate=vsdate_now,
                vstime=vstime_now,
                valiflag='Y',
                ttype=h.ttype_hung or '',
                hungserno=h.exptxserno_hung or '',
                totmount=Decimal(h.sumamount or 0),
                mondisc=h.mondisc_hung,
                sumdisc=h.sumdisc_hung,
                ecode=h.ecode_hung or '',
                pmcode=h.pmcode_hung or '',
                asscode1=h.asscode1_hung or '',
                asscode2=h.asscode2_hung or '',
                promotionsid=h.promotionsid or '',
                bookingeventid=h.bookingeventid,
            )

            lines = list(ExpenseHung.objects.filter(company=company, hunguuid=h.uuid, flag='Y').order_by('ditem_hung'))
            created_expenses = []
            for ln in lines:
                exp_row = Expense.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    ditem=ln.ditem_hung or '0001',
                    ttype=ln.ttype_hung or '',
                    stype=ln.stype_hung or '',
                    srvcode=ln.srvcode_hung or '',
                    s_qty=ln.s_qty_hung,
                    s_price=ln.s_price_hung,
                    s_mount=ln.s_mount_hung,
                    secdisc=ln.secdisc_hung,
                    srvmondisc=ln.srvmondisc_hung,
                    pmcode=ln.pmcode_hung or '',
                    asscode1=ln.asscode1_hung or '',
                    asscode2=ln.asscode2_hung or '',
                    dnote=ln.dnote_hung or '',
                    oldcardtype=ln.oldcardtype_hung or '',
                    newcardtype=ln.newcardtype_hung or '',
                    addvamoney=ln.addvamoney_hung,
                )
                created_expenses.append(exp_row)
                # 商品结账同步写入商品进出记录（仓库取门店销售仓：storeinfo.salewhcode）
                if (exp_row.ttype or '') == 'G':
                    exp_row.set_goodstranslog()

            paymeta = h_paymeta.get(h_id, {})
            pcode = (paymeta.get('pcode') or common.constants.DEFAULT_NORMAL_PCODE)
            iscash = (paymeta.get('iscash') or '1')
            expvssvern_no = 1

            # 卡付部分
            card_amt = Decimal(h_card_alloc.get(h_id, Decimal('0')))
            if card_amt > 0 and iscash == '0':
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=pcode,
                    totmount=card_amt,
                    qty=Decimal(h.sumqty or 0),
                    currency='RMB',
                    custperc=1,
                    ccode=paymeta.get('ccode') or '',
                )
                created_toll_count += 1
                ccode_key = paymeta.get('ccode') or ''
                if ccode_key:
                    card_out_changes[ccode_key] = card_out_changes.get(ccode_key, Decimal('0')) + card_amt
                expvssvern_no += 1

            # 非卡部分（含本身非卡交易 + 卡不足补差）
            noncard_amt = Decimal(h_noncard_need.get(h_id, Decimal('0')))
            while noncard_amt > 0 and len(extra_pool) > 0:
                ep = extra_pool[0]
                use_amt = ep['amount'] if ep['amount'] <= noncard_amt else noncard_amt
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=ep['pcode'],
                    totmount=use_amt,
                    qty=1,
                    currency='RMB',
                    custperc=1,
                    ccode='',
                )
                created_toll_count += 1
                expvssvern_no += 1
                noncard_amt -= use_amt
                ep['amount'] -= use_amt
                if ep['amount'] <= 0:
                    extra_pool.pop(0)

            # 兜底：若仍有未分配金额，挂默认现金类
            if noncard_amt > 0:
                fallback_pcode = auto_added_pcode or extra_paymode or common.constants.DEFAULT_NORMAL_PCODE
                Toll.objects.create(
                    company=company,
                    storecode=storecode,
                    transuuid=trans,
                    exptxserno=exptxserno,
                    expvssvern=str(expvssvern_no),
                    pcode=fallback_pcode,
                    totmount=noncard_amt,
                    qty=1,
                    currency='RMB',
                    custperc=1,
                    ccode='',
                )
                created_toll_count += 1

            # 售卡交易：挂账售卡阶段卡状态为 P，结账后转 O，并同步卡类
            for exp_row in created_expenses:
                if (exp_row.ttype or '') == 'C':
                    sold_ccode = (exp_row.srvcode or '').strip()
                    if not sold_ccode:
                        continue
                    sold_card = (
                        Cardinfo.objects.filter(company=company, ccode=sold_ccode)
                        .order_by('-create_time')
                        .first()
                    )
                    if not sold_card:
                        continue
                    changed_fields = []
                    if sold_card.status == 'P':
                        sold_card.status = 'O'
                        changed_fields.append('status')
                    if exp_row.newcardtype and sold_card.cardtype != exp_row.newcardtype:
                        sold_card.cardtype = exp_row.newcardtype
                        changed_fields.append('cardtype')
                    if changed_fields:
                        sold_card.save(update_fields=changed_fields)

            # 卡余额变更日志（cardhistory）
            # 1) 支付卡扣减（outamount）
            for ccode_key, out_amt in card_out_changes.items():
                if out_amt <= 0:
                    continue
                pay_card = (
                    Cardinfo.objects.filter(company=company, ccode=ccode_key)
                    .select_related('cardtypeuuid')
                    .order_by('-create_time')
                    .first()
                )
                if not pay_card:
                    continue
                ch, ch_created = Cardhistory.objects.get_or_create(
                    company=company,
                    storecode=storecode,
                    vsdate=vsdate_now,
                    ccode=ccode_key,
                    exptxserno=exptxserno,
                )
                if ch_created:
                    created_cardhistory_count += 1
                ch.outamount = out_amt
                ch.inamount = ch.inamount or Decimal('0')
                ch.vipuuid = trans.vipuuid
                ch.cardinfouuid = pay_card
                ch.cardtypeuuid = pay_card.cardtypeuuid
                if pay_card.cardtypeuuid_id and pay_card.cardtypeuuid:
                    ch.comptype = pay_card.cardtypeuuid.comptype
                    ch.suptype = pay_card.cardtypeuuid.suptype
                ch.transuuid = trans
                ch.save()
                try:
                    ch.recalamount()
                except Exception:
                    pass

            # 2) 售卡/充值入账（inamount）
            for exp_row in created_expenses:
                if (exp_row.ttype or '') not in ('C', 'I'):
                    continue
                sold_ccode = (exp_row.srvcode or '').strip()
                if not sold_ccode:
                    continue
                sold_card = (
                    Cardinfo.objects.filter(company=company, ccode=sold_ccode)
                    .select_related('cardtypeuuid')
                    .order_by('-create_time')
                    .first()
                )
                if not sold_card:
                    continue
                in_amt = Decimal(exp_row.addvamoney or 0)
                if in_amt <= 0:
                    in_amt = Decimal(exp_row.s_mount or 0)
                ch, ch_created = Cardhistory.objects.get_or_create(
                    company=company,
                    storecode=storecode,
                    vsdate=vsdate_now,
                    ccode=sold_ccode,
                    exptxserno=exptxserno,
                )
                if ch_created:
                    created_cardhistory_count += 1
                ch.inamount = in_amt
                ch.outamount = ch.outamount or Decimal('0')
                ch.vipuuid = trans.vipuuid
                ch.cardinfouuid = sold_card
                ch.cardtypeuuid = sold_card.cardtypeuuid
                if sold_card.cardtypeuuid_id and sold_card.cardtypeuuid:
                    ch.comptype = sold_card.cardtypeuuid.comptype
                    ch.suptype = sold_card.cardtypeuuid.suptype
                ch.transuuid = trans
                ch.save()
                try:
                    ch.recalamount()
                except Exception:
                    pass

        for _, bucket in grouped.items():
            ccode = bucket['ccode']
            paycard = (
                Cardinfo.objects.filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            for h in bucket['hungs']:
                h.cardtype_hung = paycard.cardtype if paycard else (h.cardtype_hung or '')
                h.ccode_hung = ccode
                h.psstatus_hung = '70'
                h.save(update_fields=['psstatus_hung', 'ccode_hung', 'cardtype_hung'])

        settled = len(hungs)

        return JsonResponse(
            {
                'ok': True,
                'message': '结账成功',
                'settled_count': settled,
                'total_amount': float(total_amount),
                'total_qty': float(total_qty),
                'total_extra_due': float(total_extra_due),
                'noncard_due': float(noncard_due),
                'required_noncard': float(required_noncard),
                'extra_paymode': extra_paymode,
                'extra_pay_amount': float(extra_pay_amount),
                'auto_added_pcode': auto_added_pcode,
                'auto_added_amount': float(auto_added_amount),
                'exptxsernos': created_exptxsernos,
                'toll_count': created_toll_count,
                'cardhistory_count': created_cardhistory_count,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                'ok': False,
                'code': 'CHECKOUT_SERVER_ERROR',
                'message': '结账落库异常',
                'detail': str(e),
                'trace': traceback.format_exc().splitlines()[-1] if traceback.format_exc() else '',
            },
            status=400,
        )




@csrf_exempt
def get_completed_hungs(request):
    """
    已完成开单列表（psstatus_hung='70'）。
    支持：分页、日期范围、VIP 关键词搜索。
    """
    try:
        company = request.GET.get('company', '')
        storecode = request.GET.get('storecode', '')
        page = int(request.GET.get('page', '1'))
        page_size = int(request.GET.get('page_size', '20'))
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        keyword = request.GET.get('keyword', '').strip()
    except Exception:
        return JsonResponse({'ok': False, 'message': '\u53c2\u6570\u683c\u5f0f\u9519\u8bef'})

    if not company:
        return JsonResponse({'ok': False, 'message': '\u7f3a\u5c11 company'})

    qs = ExpvstollHung.objects.filter(
        company=company,
        flag='Y',
        valiflag_hung='Y',
        psstatus_hung='70',
    ).select_related('vipuuid')

    if storecode:
        qs = qs.filter(storecode=storecode)
    if date_from:
        qs = qs.filter(vsdate_hung__gte=date_from)
    if date_to:
        qs = qs.filter(vsdate_hung__lte=date_to)
    if keyword:
        vip_ids = Vip.objects.filter(
            models.Q(vname__icontains=keyword) |
            models.Q(mtcode__icontains=keyword) |
            models.Q(vcode__icontains=keyword)
        ).values_list('uuid', flat=True)
        qs = qs.filter(vipuuid__in=vip_ids)

    qs = qs.order_by('-vsdate_hung', '-vstime_hung', '-create_time')

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    page_qs = qs[start:end]

    rows = []
    for h in page_qs:
        vip = h.vipuuid
        expense_items = ExpenseHung.objects.filter(company=company, hunguuid=h.uuid, flag='Y')
        item_count = expense_items.count()
        totmount = float(h.totmount_hung or 0)
        rows.append({
            'hunguuid': str(h.uuid),
            'exptxserno': h.exptxserno_hung or '',
            'vsdate': h.vsdate_hung or '',
            'vstime': h.vstime_hung or '',
            'order_time': _format_hung_order_time(h),
            'vipuuid': str(vip.uuid) if vip else '',
            'vname': (vip.vname if vip else '') or '',
            'vcode': (vip.vcode if vip else '') or '',
            'mtcode': (vip.mtcode if vip else '') or '',
            'totmount': totmount,
            'item_count': item_count,
            'ecode_hung': h.ecode_hung or '',
            'ttype': h.ttype_hung or '',
        })

    return JsonResponse({
        'ok': True,
        'total': total,
        'page': page,
        'page_size': page_size,
        'rows': rows,
    })


@csrf_exempt
def get_completed_order_detail(request):
    """
    \u5df2\u5b8c\u6210\u5f00\u5355\u8be6\u60c5\uff1aheader + line items
    """
    try:
        company = request.GET.get('company', '')
        hunguuid = request.GET.get('hunguuid', '')
    except Exception:
        return JsonResponse({'ok': False, 'message': '\u53c2\u6570\u683c\u5f0f\u9519\u8bef'})

    if not company or not hunguuid:
        return JsonResponse({'ok': False, 'message': '\u7f3a\u5c11\u5fc5\u8981\u53c2\u6570'})

    try:
        h_uuid = _parse_uuid_loose(hunguuid)
    except Exception:
        return JsonResponse({'ok': False, 'message': 'hunguuid \u53c2\u6570\u65e0\u6548'})

    try:
        hung = ExpvstollHung.objects.select_related('vipuuid').get(
            company=company, uuid=h_uuid, flag='Y', valiflag_hung='Y'
        )
    except ExpvstollHung.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '\u5f00\u5355\u4e0d\u5b58\u5728'})

    vip = hung.vipuuid

    items = []
    for line in ExpenseHung.objects.filter(company=company, hunguuid=hung.uuid, flag='Y').order_by('ditem_hung'):
        icode = line.srvcode_hung or ''
        items.append({
            'itemuuid': str(line.uuid),
            'ditem': line.ditem_hung or '',
            'ttype': line.ttype_hung or '',
            'stype': line.stype_hung or '',
            'ttypename': _hung_line_ttypename(line.ttype_hung),
            'stypename': _hung_line_stypename(line.stype_hung),
            'itemcode': icode,
            'itemname': _resolve_hung_itemname(company, line.ttype_hung, icode),
            'price': float(line.s_price_hung or 0),
            'qty': float(line.s_qty_hung or 0),
            'secdisc': float(line.secdisc_hung or 1),
            'srvmondisc': float(line.srvmondisc_hung or 0),
            'amount': float(line.s_mount_hung or 0),
            'pmcode': line.pmcode_hung or '',
            'seccode': line.asscode1_hung or '',
            'thrcode': line.asscode2_hung or '',
            'remark': line.dnote_hung or '',
        })

    return JsonResponse({
        'ok': True,
        'hung': {
            'hunguuid': str(hung.uuid),
            'exptxserno': hung.exptxserno_hung or '',
            'vsdate': hung.vsdate_hung or '',
            'vstime': hung.vstime_hung or '',
            'order_time': _format_hung_order_time(hung),
            'psstatus': hung.psstatus_hung or '',
            'totmount': float(hung.totmount_hung or 0),
            'ttype': hung.ttype_hung or '',
            'remark': hung.remark_hung or '',
            'ecode_hung': hung.ecode_hung or '',
            'vipuuid': str(vip.uuid) if vip else '',
            'vname': (vip.vname if vip else '') or '',
            'vcode': (vip.vcode if vip else '') or '',
            'mtcode': (vip.mtcode if vip else '') or '',
        },
        'items': items,
    })


@csrf_exempt
def get_checkout_shortfall(request):
    company = request.GET.get('company', common.constants.COMPANYID)
    storecode = request.GET.get('storecode', '88')
    vipuuid_raw = request.GET.get('vipuuid', '')
    hraw = request.GET.get('hunguuids', '[]')
    try:
        hlist = json.loads(hraw) if isinstance(hraw, str) else []
    except Exception:
        hlist = []
    if not isinstance(hlist, list):
        hlist = []
    try:
        vipuuid = _parse_uuid_loose(vipuuid_raw)
    except Exception:
        vipuuid = None
    hunguuids = []
    for h in hlist:
        try:
            hunguuids.append(_parse_uuid_loose(h))
        except Exception:
            continue
    total_extra_due = Decimal('0')
    noncard_due = Decimal('0')
    total_selected_amount = Decimal('0')
    if vipuuid and hunguuids:
        open_status = ('10', '20', '30', '40', '50', '60')
        hungs = list(
            ExpvstollHung.objects.filter(
                company=company,
                storecode=storecode,
                flag='Y',
                valiflag_hung='Y',
                vipuuid=vipuuid,
                psstatus_hung__in=open_status,
                uuid__in=hunguuids,
            )
        )
        grouped = {}
        h_stype_map = {}
        for eh in ExpenseHung.objects.filter(company=company, hunguuid__in=hunguuids, flag='Y').only('hunguuid', 'stype_hung', 'ditem_hung').order_by('ditem_hung'):
            k = str(eh.hunguuid_id)
            if k not in h_stype_map:
                h_stype_map[k] = eh.stype_hung
        for h in hungs:
            total_selected_amount += Decimal(h.sumamount or 0)
            ccode = (h.ccode_hung or '').strip()
            h_stype = h_stype_map.get(str(h.uuid), 'N')
            payinfo = _resolve_paycard_plan_info(company, ccode, h.cardtype_hung, h_stype)
            pcode = (payinfo.get('paytype') or '').strip()
            p_iscash = ''
            if pcode:
                p_iscash = (
                    Paymode.objects.filter(company=company, pcode=pcode)
                    .values_list('iscash', flat=True)
                    .first()
                    or ''
                )
            grp_key = ccode + '|' + pcode + '|' + p_iscash
            grouped[grp_key] = grouped.get(grp_key, Decimal('0')) + Decimal(h.sumamount or 0)
        for grp_key, need_amount in grouped.items():
            parts = grp_key.split('|')
            ccode = parts[0] if len(parts) > 0 else ''
            iscash = parts[2] if len(parts) > 2 else ''
            if iscash in ('1', '2'):
                noncard_due += need_amount
                continue
            paycard = (
                Cardinfo.objects.filter(
                    company=company,
                    flag='Y',
                    status__in=('O', 'P'),
                    vipuuid=vipuuid,
                    ccode=ccode,
                )
                .first()
            )
            leftmoney = Decimal(paycard.leftmoney or 0) if paycard else Decimal('0')
            if leftmoney < need_amount:
                total_extra_due += need_amount - leftmoney

    paymodes = list(
        Paymode.objects.filter(company=company, flag='Y', visibleflag='Y')
        .exclude(iscash='0')
        .values('pcode', 'pname', 'iscash')
        .order_by('pcode')
    )
    return JsonResponse(
        {
            'ok': True,
            'total_extra_due': float(total_extra_due),
            'noncard_due': float(noncard_due),
            'required_noncard': float(total_extra_due + noncard_due),
            'card_paid_amount': float(max(total_selected_amount - (total_extra_due + noncard_due), Decimal('0'))),
            'paymodes': paymodes,
        }
    )


def get_bookingable_empllist(request):
    company = request.GET['company']
    storecode = request.GET['storecode']

    sql = " select ecode,ename, emplpwd,position, b.positiondesc,a.uuid uuid" \
          " from  empl a, position b" \
          " where 1=1 and a.company = b.company" \
          " and a.company=%s and a.storecode =%s and a.POSITION = b.positioncode" \
          " and  b.bookingflag='Y'"

    print(sql)

    params = (company+' '+ storecode ).split()
    print(params)

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_bookinglist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID
    storecode = request.GET['storecode']

    bookingstartdate = request.GET['bookingdate']
    bookingdate = parse_ymd(bookingstartdate)

    sql = " select bookingeventid,companyid,storecode, vipuuid, vcode, vname, mtcode, ecode, bookingstartdate, bookingstarttime, bookingendtime, " \
          "  roomid, roomstarttime, roomendtime,instrumentid,instrumentstarttime, instrumentendtime, bookingstatus, bookingdetail,operecode,bookingflag," \
          " getbaseinfo(a.companyid,a.storecode,'empl',a.ecode,'ename') ename, " \
          " getbaseinfo(a.companyid,a.storecode,'room',a.roomid,'roomname') roomname " \
          " from  bookingevent a" \
          " where 1=1 " \
          " and companyid=%s and storecode =%s and date(bookingstartdate)=date(%s) and bookingstatus <>'390' " \
          " and  a.bookingflag='Y'"

    print(sql)
    params = (company+' '+ storecode +' ' + bookingdate).split()
    print(params)

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_nextccode(request):
    company = request.GET['company']
    storecode= request.GET['storecode']
    vcode = request.GET['vcode']
    prefix = storecode
    codelength=4

    cardinfo = Cardinfo.objects.filter(company=company,storecode=storecode, vcode=vcode).order_by('-ccode')
    # print(cardinfo)
    if len(cardinfo)==0 :
        print('len(cardinfo)=0')
        nextcode='00000001'[-codelength]
    else:
        print(cardinfo[0].ccode)
    # print(cardinfo,cardinfo[0].vcode,'len(storecode)=', len(storecode), 'len(vip[0].ccode) - len(storecode)=',len(cardinfo[0].ccode) - len(storecode)+4 )
        nextcode = cardinfo[0].ccode[len(vcode):len(cardinfo[0].vcode)]
    print('nextcode=',nextcode)
    nextccode= vcode +'-'+ ('000000'+ str(int(nextcode)+1))[-codelength:]
    print('nextccode=',nextccode)
    return HttpResponse(nextccode, content_type="application/json")

@csrf_exempt
def get_bookingEvent(request):
    if request.method == 'GET':
        try:
            company=request.GET['company']
        except:
            company=common.constants.COMPANYID

        try:
            bookingeventid = request.GET['bookingeventid']
            print('bookingeventid:',bookingeventid)
            sql = " select bookingeventid, bookingdetail,bookingstartdate,bookingstarttime, bookingendtime,vcode,vname,mtcode,ecode,emplstarttime, emplendtime,roomid,roomstarttime,roomendtime," \
                  " instrumentid,instrumentbookingstarttime,instrumentendtime, vipuuid" \
                  " from bookingevent where companyid=%s and bookingeventid=%s"
            params = (company+' '+ bookingeventid ).split()
            print(sql)

            json_data = sql_to_json(sql,params)
            print(json_data)

            # bookingevent = Bookingevent.objects.filter(bookingeventid=bookingeventid).values_list('bookingeventid','bookingstartdate','bookingstarttime','bookingendtime')
            # print('bookingevent:',bookingevent)
            # json_data = serialize('json', bookingevent)  # str
            # print('after serialize',json_data)
            # json_data = json.loads(json_data)
            # print('after loads',json_data)

            # return JsonResponse(json_data)
            return HttpResponse(json_data, content_type="application/json")
        except:
            bookingeventid = -1
            json_data = {
                'code':500,
            }
            print(json_data)
            return JsonResponse(json_data)


@csrf_exempt
@transaction.atomic
def add_BookingEvent(request):
    if request.method=='POST':
        data = json.loads(request.GET['param'])
        print('request param:', data)
        company = data['company']
        storecode = data['storecode']

        bookingstartdate=data['bookingstartdate']
        bookingstarttime=data['bookingstarttime']
        bookingendtime=data['bookingendtime']
        vcode = data['vcode']
        vname=data['vname']
        mtcode=data['mtcode']
        ecode = data['ecode']
        roomid = data['roomid']
        roomstarttime = data['roomstarttime']
        roomendtime = data['roomendtime']
        instrumentid=data['instrumentid']
        instrumentstarttime=data['instrumentstarttime']
        instrumentendtime=data['instrumentendtime']
        bookingdetail=data['bookingdetail']
        bookingstatus=data['bookingstatus']
        operecode=data['operecode']
        bookingflag=data['bookingflag']
        vipuuid = data['vipuuid']

        try:
            vip = Vip.objects.get(company=company,uuid=vipuuid)
        except:
            vip = Vip.objects.get_or_create(company=company,storecode=storecode,vname=vname,mtcode=mtcode,viptype='30')[0]

        bookingevent = Bookingevent.objects.get_or_create(companyid=company,storecode=storecode,vipuuid=vip,
                                                          bookingstartdate=bookingstartdate,ecode=ecode,bookingstarttime=bookingstarttime,bookingendtime=bookingendtime,
                                                          vcode=vcode,vname=vname,mtcode=mtcode,roomid=roomid,roomstarttime=roomstarttime,roomendtime=roomendtime,
                                                          instrumentid=instrumentid,instrumentstarttime=instrumentstarttime,instrumentendtime=instrumentendtime,
                                                          bookingdetail=bookingdetail,bookingstatus=bookingstatus,operecode=operecode,bookingflag=bookingflag)[0]
        # sql = " select ccode, itemcode,itemname, qty, price,secdisc,mondisc,amount,pmcode,seccode,thrcode,promotionsid,uuid,ttype, stype, " \
        #       " ( case stype when 'P' then '赠送' else '正常' end) stypename,F_Getnamebysrvcode(itemcode,ttype,company) itemname" \
        #       " from  shoppingcart " \
        #       " where 1=1 and flag='Y' and status='10'" \
        #       " and company=%s and storecode =%s and vipuuid = %s AND ttype=%s" \
        #
        # params = (company+' '+ storecode+ ' '+ vipuuid + ' '+ttype ).split()
        #
        # json_data = sql_to_json(sql,params)
        # return HttpResponse(json_data, content_type="application/json")

        return HttpResponse(200, content_type="application/json")

@csrf_exempt
@transaction.atomic
def update_BookingEvent(request):
    if request.method=='POST':
        data = json.loads(request.GET['param'])
        print('request param:', data)

        company = data['companyid']
        storecode = data['storecode']

        bookingeventid = data['bookingeventid']

        bookingstartdate=data['bookingstartdate']
        bookingstarttime=data['bookingstarttime']
        bookingendtime=data['bookingendtime']
        vcode = data['vcode']
        vname=data['vname']
        mtcode=data['mtcode']
        ecode = data['ecode']
        roomid = data['roomid']
        roomstarttime = data['roomstarttime']
        roomendtime = data['roomendtime']
        instrumentid=data['instrumentid']
        instrumentstarttime=data['instrumentstarttime']
        instrumentendtime=data['instrumentendtime']
        bookingdetail=data['bookingdetail']
        bookingstatus=data['bookingstatus']
        operecode=data['operecode']
        bookingflag=data['bookingflag']
        vipuuid = data['vipuuid']
        try:
            vip = Vip.objects.get(comany=company,uuid=vipuuid)
        except:
            vip = Vip.objects.get_or_create(company=company,storecode=storecode,creater=ecode,vname=vname,mtcode=mtcode,viptype='30')[0]

        try:
            print('bookingeventid',bookingeventid)
            bookingevent = Bookingevent.objects.get(companyid=company,bookingeventid=bookingeventid)
            print('get bookingevent bookingeventid=',bookingeventid)
            bookingevent.storecode=storecode

            bookingevent.bookingstartdate = bookingstartdate
            bookingevent.bookingstarttime=bookingstarttime
            bookingevent.bookingendtime=bookingendtime
            bookingevent.vcode=vcode
            bookingevent.vname=vname
            bookingevent.mtcode=mtcode
            bookingevent.ecode=ecode
            bookingevent.roomid=roomid
            bookingevent.roomstarttime=roomstarttime
            bookingevent.roomendtime=roomendtime
            bookingevent.instrumentid=instrumentid
            bookingevent.instrumentstarttime=instrumentstarttime
            bookingevent.instrumentendtime=instrumentendtime
            bookingevent.bookingdetail=bookingdetail
            bookingevent.bookingstatus=bookingstatus
            bookingevent.operecode=operecode
            bookingevent.bookingflag=bookingflag
            bookingevent.vipuuid=vip
            bookingevent.save()
        except:
            print('not get bookingeventid=',bookingeventid)
            bookingevent = Bookingevent.objects.create(companyid=company,storecode=storecode,bookingeventid=bookingeventid,vipuuid=vip,
                                                          bookingstartdate=bookingstartdate,bookingstarttime=bookingstarttime,bookingendtime=bookingendtime,
                                                          vcode=vcode,vname=vname,mtcode=mtcode,roomid=roomid,roomstarttime=roomstarttime,roomendtime=roomendtime,
                                                          instrumentid=instrumentid,instrumentstarttime=instrumentstarttime,instrumentendtime=instrumentendtime,
                                                          bookingdetail=bookingdetail,bookingstatus=bookingstatus,operecode=operecode,bookingflag=bookingflag)[0]
        # sql = " select ccode, itemcode,itemname, qty, price,secdisc,mondisc,amount,pmcode,seccode,thrcode,promotionsid,uuid,ttype, stype, " \
        #       " ( case stype when 'P' then '赠送' else '正常' end) stypename,F_Getnamebysrvcode(itemcode,ttype,company) itemname" \
        #       " from  shoppingcart " \
        #       " where 1=1 and flag='Y' and status='10'" \
        #       " and company=%s and storecode =%s and vipuuid = %s AND ttype=%s" \
        #
        # params = (company+' '+ storecode+ ' '+ vipuuid + ' '+ttype ).split()
        #
        # json_data = sql_to_json(sql,params)
        # return HttpResponse(json_data, content_type="application/json")

        return HttpResponse(200, content_type="application/json")


# ---- 开单挂账（从 cashier/views.py 迁入） ----

def getserno(company,storecode, tablecode):
    try:
        sequence = Sequence.objects.get(company=company, storecode=storecode, tablecode=tablecode)
    except:
        sequence = Sequence.objects.create(company=company, storecode=storecode, tablecode=tablecode, sequence=0)
    print('sequence', sequence)
    sequence.sequence = sequence.sequence + 1
    sequence.save()
    return sequence.sequence

    return company  + storecode +'_'+ tablecode+'_' + str(sequence.sequence)


@csrf_exempt
def cardtype_service_items(request):
    '''获取卡类关联的服务项目'''
    company = request.GET.get('company', '')
    cardtypeuuid = request.GET.get('cardtypeuuid', '')
    cardtype_code = request.GET.get('cardtype', '')
    if not company or not cardtypeuuid:
        # 无 UUID 时按编码查询
        if cardtype_code:
            try:
                cardtype = Cardtype.objects.get(company=company, cardtype=cardtype_code)
            except Cardtype.DoesNotExist:
                return JsonResponse([], safe=False)
        else:
            return JsonResponse([], safe=False)
    else:
        try:
            cardtype = Cardtype.objects.get(company=company, uuid=cardtypeuuid)
        except Cardtype.DoesNotExist:
            # UUID 未匹配时回退到按编码查询
            if cardtype_code:
                try:
                    cardtype = Cardtype.objects.get(company=company, cardtype=cardtype_code)
                except Cardtype.DoesNotExist:
                    return JsonResponse([], safe=False)
            else:
                return JsonResponse([], safe=False)
    ct_code = cardtype.cardtype
    tt = getattr(cardtype, 'ttype', '') or ''
    if tt == 'S':
        try:
            svc = Serviece.objects.get(company=company, flag='Y', svrcdoe=ct_code)
            data = [{'code': svc.svrcdoe, 'name': svc.svrname, 'price': float(svc.price or 0), 'ttype': 'S'}]
        except Serviece.DoesNotExist:
            data = []
    elif tt == 'G':
        try:
            gd = Goods.objects.get(company=company, flag='Y', gcode=ct_code)
            data = [{'code': gd.gcode, 'name': gd.gname, 'price': float(gd.price or 0), 'ttype': 'G'}]
        except Goods.DoesNotExist:
            data = []
    else:
        # ttype 为空或未知：回退到同时尝试两种查找
        try:
            svc = Serviece.objects.get(company=company, flag='Y', svrcdoe=ct_code)
            data = [{'code': svc.svrcdoe, 'name': svc.svrname, 'price': float(svc.price or 0), 'ttype': 'S'}]
        except Serviece.DoesNotExist:
            try:
                gd = Goods.objects.get(company=company, flag='Y', gcode=ct_code)
                data = [{'code': gd.gcode, 'name': gd.gname, 'price': float(gd.price or 0), 'ttype': 'G'}]
            except Goods.DoesNotExist:
                data = []
    return JsonResponse(data, safe=False)


@csrf_exempt
def save_hung_order(request):
    '''保存挂账单'''
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    
    company = data.get('company', '')
    storecode = data.get('storecode', '01')
    vipuuid = data.get('vipuuid', '')
    items = data.get('items', [])
    if not company or not vipuuid or not items:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'})
    
    try:
        with transaction.atomic():
            today = datetime.now().strftime('%Y%m%d')
            serno = getserno(company, storecode, 'EXP')
            exptxserno = f'{company}{storecode}_hung_{serno}'
            # 查找 VIP 编码
            try:
                vip_obj = Vip.objects.get(uuid=vipuuid)
                vip_code = vip_obj.vcode
            except Vip.DoesNotExist:
                vip_code = ''
            
            hung = ExpvstollHung.objects.create(
                company=company, storecode=storecode,
                ccode_hung=next((item.get('card_ccode', '') or item.get('srvcode', '') for item in items if item.get('card_ccode', '') or item.get('ttype') == 'I'), ''),
                cardtype_hung=next((item.get('cardtype', '') for item in items if item.get('cardtype', '')), ''),
                exptxserno_hung=exptxserno,
                vsdate_hung=today,
                vstime_hung=datetime.now().strftime('%H%M%S'),
                vipuuid_id=vipuuid,
                vcode_hung=vip_code,
                vipcode=vip_code,
                totmount_hung=sum(float(item.get('s_price', 0)) * int(item.get('s_qty', 1)) for item in items),
                psstatus_hung='10',
                ttype_hung='S',
                valiflag_hung='Y',
            )
            
            for idx, item in enumerate(items):
                ttype = item.get('ttype', 'S')
                srvcode = item.get('srvcode', '')
                s_qty = int(item.get('s_qty', 1))
                s_price = float(item.get('s_price', 0))
                secdisc = float(item.get('secdisc', 1))
                srvmondisc = float(item.get('srvmondisc', 0))
                s_mount = s_qty * s_price * secdisc - srvmondisc
                stype = item.get('stype', 'N')
                card_ccode = item.get('card_ccode', '')
                pmcode = item.get('pmcode', '') or ''
                asscode1 = item.get('asscode1', '') or ''
                asscode2 = item.get('asscode2', '') or ''
                
                ExpenseHung.objects.create(
                    company=company,
                    storecode=storecode,
                    hunguuid=hung,
                    exptxserno_hung=exptxserno,
                    ditem_hung=f'{idx+1:04d}',
                    ttype_hung=ttype,
                    stype_hung=stype,
                    srvcode_hung=srvcode,
                    s_qty_hung=s_qty,
                    s_price_hung=s_price,
                    secdisc_hung=secdisc,
                    srvmondisc_hung=srvmondisc,
                    s_mount_hung=s_mount,
                    srvactmount_hung=s_mount,
                    pmcode_hung=pmcode,
                    asscode1_hung=asscode1,
                    asscode2_hung=asscode2,
                    depositeflag='N',
                    otherserno_hung=card_ccode or '',
                    flag='Y',
                )
                
                # 充值：更新卡余额
                if ttype == 'I' and srvcode:
                    try:
                        card = Cardinfo.objects.select_related('cardtypeuuid').get(company=company, ccode=srvcode)
                        if card.cardtypeuuid and card.cardtypeuuid.comptype == 'times':
                            card.leftqty = (card.leftqty or Decimal('0')) + Decimal(str(s_price))
                        else:
                            card.leftmoney = (card.leftmoney or Decimal('0')) + Decimal(str(s_price))
                        card.save()
                    except Cardinfo.DoesNotExist:
                        pass
                    # 充值记录写入 cardtype_hung（复用 cardtype 字段）
                    try:
                        rc = card
                        recharge_cardtype = rc.cardtype
                    except Cardinfo.DoesNotExist:
                        recharge_cardtype = ''
                # 售卡：创建 cardinfo 挂账卡
                if ttype == 'C' and srvcode:
                    new_ccode = ''
                    card_leftqty = 0
                    card_leftmoney = 0
                    try:
                        ct = Cardtype.objects.filter(company=company, flag='Y', cardtype=srvcode).first()
                        if ct:
                            if ct.comptype == 'times':
                                card_leftqty = int(item.get('s_qty', 1))
                            elif ct.comptype == 'amount':
                                card_leftmoney = s_price
                    except Exception:
                        pass
                    try:
                        vip_obj = Vip.objects.get(uuid=vipuuid)
                        new_ccode = vip_obj.nextccode()
                    except (Vip.DoesNotExist, Exception):
                        new_ccode = getserno(company, storecode, 'CARD')
                    Cardinfo.objects.create(
                        company=company, storecode=storecode,
                        ccode=new_ccode,
                        cardtype=srvcode,
                        status='P',
                        flag='Y',
                        isic='0',
                        stype=stype,
                        promotionsid='0',
                        s_price=s_price,
                        leftmoney=card_leftmoney,
                        leftqty=card_leftqty,
                        vcode=vip_code,
                        vipuuid_id=vipuuid,
                        cardtypeuuid=Cardtype.objects.filter(company=company, flag='Y', cardtype=srvcode).first(),
                    )
            
            return JsonResponse({'ok': True, 'exptxserno': exptxserno})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})

@csrf_exempt
def cardtype_prices(request):
    '''获取卡类关联的疗程价格选项'''
    company = request.GET.get('company', '')
    cardtype = request.GET.get('cardtype', '')
    if not company or not cardtype:
        return JsonResponse([], safe=False)
    try:
        prices = Servieceprice.objects.filter(
            company=company, flag='Y', srvcode=cardtype, saleflag='Y'
        ).values('qty', 'price', 'amount').order_by('qty')
        data = [{'qty': int(r['qty'] or 1), 'price': float(r['price'] or 0), 'amount': float(r['amount'] or 0)} for r in prices]
        if not data:
            ct = Cardtype.objects.filter(company=company, flag='Y', cardtype=cardtype).first()
            if ct:
                data = [{'qty': 1, 'price': float(ct.price or 0), 'amount': float(ct.price or 0)}]
    except Exception:
        data = []
    return JsonResponse(data, safe=False)

@csrf_exempt
def get_hung_list(request):
    '''获取挂单列表（未结账，或按会员筛选）'''
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '88')
    vipuuid = request.GET.get('vipuuid', '')

    if not company:
        return JsonResponse([], safe=False)

    qs = ExpvstollHung.objects.filter(
        company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
    )

    if vipuuid:
        try:
            v_uuid = _parse_uuid_loose(vipuuid)
            qs = qs.filter(vipuuid=v_uuid)
        except Exception:
            pass
    else:
        open_status = ('10', '20', '30', '40', '50', '60')
        qs = qs.filter(psstatus_hung__in=open_status)

    qs = qs.order_by('-vsdate_hung', '-vstime_hung')[:100]

    data = []
    for h in qs:
        data.append({
            'uuid': str(h.uuid),
            'exptxserno': h.exptxserno_hung or '',
            'vcode': h.vcode_hung or '',
            'vipuuid': str(h.vipuuid_id) if h.vipuuid_id else '',
            'vsdate': h.vsdate_hung or '',
            'vstime': h.vstime_hung or '',
            'totmount': float(h.totmount_hung or 0),
            'psstatus': h.psstatus_hung or '',
            'paycode': h.ccode_hung or '',
            'cardtype': h.cardtype_hung or '',
            'itemcount': ExpenseHung.objects.filter(hunguuid=h.uuid, flag='Y').count(),
        })

    return JsonResponse(data, safe=False)
