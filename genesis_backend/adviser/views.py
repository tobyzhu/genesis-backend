#coding=utf-8

from __future__ import unicode_literals
import math
from collections import defaultdict
from datetime import datetime,timedelta
from decimal import Decimal
import traceback
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError
from django.db import models
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
from baseinfo.models import Serviece,Servieceprice,Goods,Srvtopty,Srvrptype,Goodsct,Vip,Cardtype,Cardsupertype,Empl,Paymode,Appoption,Promotions,Promotionsdetail,Promotionsgroup,Promotionsgroupdetail
from cashier.models import EarnestMoney, Expvstoll, Expense, Toll, Cardhistory
import common.constants
from common.models import Sequence
from common.views import getserno
from common.views import _resolve_hung_itemname


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
    """按 company + storecode + tablecode 递增流水号，转调 common.views.getserno。"""
    return getserno(company, storecode, tablecode)

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
def group_items_by_card(company, items):
    """按付款卡号分组开单明细
    储值卡同一组(现金归入缺口最大的), 计次卡独立成组, 全现金单独成组
    售卡(C)和充值(I)单独挂账, 不混入服务/商品组"""
    sg_items = [it for it in items if it.get('ttype') in ('S', 'G')]
    card_sale_items = [it for it in items if it.get('ttype') == 'C']
    recharge_items = [it for it in items if it.get('ttype') == 'I']
    result = {}

    # S/G 按卡号分组(原逻辑)
    if sg_items:
        all_ccodes = {it.get('card_ccode','') for it in sg_items if it.get('card_ccode','')}
        card_info = {}
        if all_ccodes:
            cards = Cardinfo.objects.filter(company=company, ccode__in=all_ccodes, flag='Y')\
                .select_related('cardtypeuuid')\
                .values('ccode', 'cardtypeuuid__comptype', 'leftmoney')
            for c in cards:
                card_info[c['ccode']] = {
                    'comptype': c['cardtypeuuid__comptype'],
                    'balance': float(c['leftmoney'] or 0),
                }
        amount_groups = defaultdict(list)
        times_groups = defaultdict(list)
        cash_items = []
        for it in sg_items:
            card = it.get('card_ccode', '') or ''
            if not card:
                cash_items.append(it)
            elif card_info.get(card, {}).get('comptype') == 'times':
                times_groups[card].append(it)
            else:
                amount_groups[card].append(it)
        deficits = {}
        for ccode, citems in amount_groups.items():
            total = sum(int(it.get('s_qty',1)) * float(it.get('s_price',0)) for it in citems)
            bal = card_info.get(ccode, {}).get('balance', 0)
            deficits[ccode] = total - bal
        if cash_items:
            needy = {c: d for c, d in deficits.items() if d > 0}
            if needy:
                target = max(needy, key=lambda c: needy[c])
                amount_groups[target].extend(cash_items)
            elif amount_groups:
                amount_groups['__cash__'] = cash_items
            else:
                amount_groups['__cash__'] = cash_items
        result.update(dict(amount_groups))
        result.update(times_groups)

    # 售卡: 每张独立成组
    for idx, it in enumerate(card_sale_items):
        result[f'__C_{idx}__'] = [it]

    # 充值: 每笔独立成组
    for idx, it in enumerate(recharge_items):
        result[f'__I_{idx}__'] = [it]

    return result
@csrf_exempt
def save_hung_order(request):
    """保存挂账单(按付款卡号拆分)"""
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

    # 校验活动一致性
    promo_ids = set(str(it.get('promotionsid', '') or '') for it in items if it.get('promotionsid'))
    if len(promo_ids) > 1:
        return JsonResponse({'ok': False, 'message': '不同活动的项目不能挂在同一张单上'})

    try:
        with transaction.atomic():
            today = datetime.now().strftime('%Y%m%d')
            base_exptxserno = getserno(company, storecode, 'hung')

            try:
                vip_obj = Vip.objects.get(uuid=vipuuid)
                vip_code = vip_obj.vcode
            except Vip.DoesNotExist:
                vip_code = ''

            order_promotionsid = next((it.get('promotionsid', '') for it in items if it.get('promotionsid', '')), '')

            # 按卡号分组
            groups = group_items_by_card(company, items)
            group_items_list = list(groups.items())

            exptxsernos = []
            for gidx, (card_key, card_items) in enumerate(group_items_list):
                if len(group_items_list) == 1:
                    exptxserno = base_exptxserno
                else:
                    exptxserno = f'{base_exptxserno}-{gidx+1}'

                if card_key.startswith('__C_') or card_key.startswith('__I_'):
                    ccode_hung_val = card_items[0].get('card_ccode', '') or ''
                elif card_key == '__cash__':
                    ccode_hung_val = ''
                else:
                    ccode_hung_val = card_key

                group_total = sum(
                    int(it.get('s_qty', 1)) * float(it.get('s_price', 0)) * float(it.get('secdisc', 1)) - float(it.get('srvmondisc', 0))
                    for it in card_items
                )

                # 从明细项推断挂单类型
                group_ttype = 'S'
                for it in card_items:
                    it_t = it.get('ttype', '')
                    if it_t in ('C', 'I', 'G'):
                        group_ttype = it_t
                        break

                hung = ExpvstollHung.objects.create(
                    company=company, storecode=storecode,
                    ccode_hung=ccode_hung_val,
                    cardtype_hung='',
                    exptxserno_hung=exptxserno,
                    vsdate_hung=today,
                    vstime_hung=datetime.now().strftime('%H%M%S'),
                    vipuuid_id=vipuuid,
                    vcode_hung=vip_code,
                    vipcode=vip_code,
                    totmount_hung=group_total,
                    psstatus_hung='10',
                    ttype_hung=group_ttype,
                    valiflag_hung='Y',
                    promotionsid=order_promotionsid,
                )

                for idx, item in enumerate(card_items):
                    ttype = item.get('ttype', 'S')
                    srvcode = item.get('srvcode', '')
                    s_qty = int(item.get('s_qty', 1))
                    s_price = float(item.get('s_price', 0))
                    if s_price < 0:
                        return JsonResponse({'ok': False, 'message': f'单价不能为负数: {item.get("srvcode", "?")}'})
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
                        addvamoney_hung=s_mount,
                        otherserno_hung=card_ccode or '',
                        flag='Y',
                    )

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
                            promotionsid=order_promotionsid or '0',
                            s_price=s_price,
                            leftmoney=card_leftmoney,
                            leftqty=card_leftqty,
                            vcode=vip_code,
                            vipuuid_id=vipuuid,
                            cardtypeuuid=Cardtype.objects.filter(company=company, flag='Y', cardtype=srvcode).first(),
                        )
                        # 记录新卡号到 dnote_hung，供作废时追溯
                        ExpenseHung.objects.filter(
                            company=company, hunguuid=hung, ditem_hung=f'{idx+1:04d}'
                        ).update(srvcode_hung=new_ccode, dnote_hung=new_ccode)

                exptxsernos.append(exptxserno)

            return JsonResponse({'ok': True, 'count': len(exptxsernos), 'exptxsernos': exptxsernos})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})
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
    psstatus = request.GET.get('psstatus', '')
    vsdate_from = request.GET.get('vsdate_from', '')
    vsdate_to = request.GET.get('vsdate_to', '')
    hdsysuserid = request.GET.get('hdsysuserid', '')

    # report_fromdate 约束：开始日期不能早于用户的可查最早日期
    if hdsysuserid and vsdate_from:
        try:
            hd = Hdsysuser.objects.filter(company=company, sys_userid=hdsysuserid).first()
            if hd and hd.report_fromdate and vsdate_from < hd.report_fromdate:
                vsdate_from = hd.report_fromdate
        except Exception:
            pass

    if not company:
        return JsonResponse([], safe=False)

    if psstatus == '__void__':
        qs = ExpvstollHung.objects.filter(
            company=company, storecode=storecode, flag='Y', valiflag_hung='N',
        )
    else:
        qs = ExpvstollHung.objects.filter(
            company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
        )

    if vipuuid:
        try:
            v_uuid = _parse_uuid_loose(vipuuid)
            qs = qs.filter(vipuuid=v_uuid)
            checkout_mode = request.GET.get('checkout_mode', '')
            if checkout_mode:
                qs = qs.filter(psstatus_hung__in=('10', '20', '30', '40', '50', '60'))
        except Exception:
            pass
    elif psstatus and psstatus != '__void__':
        qs = qs.filter(psstatus_hung=psstatus)
    else:
        open_status = ('10', '20', '30', '40', '50', '60')
        qs = qs.filter(psstatus_hung__in=open_status)

    if vsdate_from:
        qs = qs.filter(vsdate_hung__gte=vsdate_from)
    if vsdate_to:
        qs = qs.filter(vsdate_hung__lte=vsdate_to)

    # 先查会员姓名（用独立 qs，避免切片后再过滤）
    if psstatus == '__void__':
        vip_qs = ExpvstollHung.objects.filter(
            company=company, storecode=storecode, flag='Y', valiflag_hung='N',
        )
    else:
        if psstatus == '__void__':
            vip_qs = ExpvstollHung.objects.filter(
                company=company, storecode=storecode, flag='Y', valiflag_hung='N',
            )
        else:
            vip_qs = ExpvstollHung.objects.filter(
                company=company, storecode=storecode, flag='Y', valiflag_hung='Y',
            )
    if psstatus and psstatus != '__void__':
        vip_qs = vip_qs.filter(psstatus_hung=psstatus)
    elif not vipuuid:
        open_status = ('10', '20', '30', '40', '50', '60')
        vip_qs = vip_qs.filter(psstatus_hung__in=open_status)
    if vsdate_from:
        vip_qs = vip_qs.filter(vsdate_hung__gte=vsdate_from)
    if vsdate_to:
        vip_qs = vip_qs.filter(vsdate_hung__lte=vsdate_to)
    vip_ids = list(vip_qs.exclude(vipuuid_id=None).values_list('vipuuid_id', flat=True).distinct())[:200]
    vip_name_map = {}
    if vip_ids:
        for v in Vip.objects.filter(uuid__in=vip_ids).only('uuid', 'vname'):
            key = str(v.uuid).replace('-', '')
            if key not in vip_name_map:
                vip_name_map[key] = v.vname

    qs = qs.order_by('-vsdate_hung', 'exptxserno_hung')[:100]

    data = []
    hung_list = list(qs)
    # 批量统计项目数，避免 N+1 查询
    uuid_list = [h.uuid for h in hung_list]
    count_map = {}
    if uuid_list:
        q_counts = ExpenseHung.objects.filter(hunguuid__in=uuid_list, flag='Y').values('hunguuid').annotate(cnt=Count('uuid'))
        for c in q_counts:
            count_map[c['hunguuid']] = c['cnt']
    for h in hung_list:
        uuid_key = str(h.vipuuid_id) if h.vipuuid_id else ''
        vname = vip_name_map.get(uuid_key, vip_name_map.get(uuid_key.replace('-', ''), '')) if uuid_key else ''
        data.append({
            'uuid': str(h.uuid),
            'exptxserno': h.exptxserno_hung or '',
            'vcode': h.vcode_hung or '',
            'vname': vname,
            'vipuuid': str(h.vipuuid_id) if h.vipuuid_id else '',
            'vsdate': h.vsdate_hung or '',
            'vstime': h.vstime_hung or '',
            'totmount': float(h.totmount_hung or 0),
            'psstatus': h.psstatus_hung or '',
            'paycode': h.ccode_hung or '',
            'cardtype': h.cardtype_hung or '',
            'ttype': h.ttype_hung or '',
            'valiflag': h.valiflag_hung or '',
            'itemcount': count_map.get(h.uuid, 0),
        })

    # 批量查询明细项目名称和 stype
    if data:
        uuid_list = [d['uuid'] for d in data]
        uuid_objs = [_parse_uuid_loose(u) for u in uuid_list if u]
        if uuid_objs:
            item_lines = ExpenseHung.objects.filter(
                hunguuid__in=uuid_objs, flag='Y'
            ).values('hunguuid_id', 'ttype_hung', 'srvcode_hung', 'stype_hung',
                     's_qty_hung', 's_price_hung', 's_mount_hung',
                     'pmcode_hung', 'asscode1_hung', 'asscode2_hung',
                     'otherserno_hung').order_by('ditem_hung')
            stype_map = {}
            item_map = {}
            item_details_map = {}
            for ln in item_lines:
                key = str(ln['hunguuid_id']) if ln['hunguuid_id'] else ''
                if not key:
                    continue
                if key not in stype_map:
                    stype_map[key] = []
                stype_map[key].append(ln['stype_hung'] or 'N')
                if key not in item_map:
                    item_map[key] = []
                name = _resolve_hung_itemname(company, ln['ttype_hung'] or '', ln['srvcode_hung'] or '')
                if name:
                    item_map[key].append(name)
                if key not in item_details_map:
                    item_details_map[key] = []
                ttype_val = ln['ttype_hung'] or ''
                item_details_map[key].append({
                    'name': name or ln['srvcode_hung'] or '',
                    'qty': float(ln['s_qty_hung'] or 0),
                    'price': float(ln['s_price_hung'] or 0),
                    'subtotal': float(ln['s_mount_hung'] or 0),
                    'ttypename': _hung_line_ttypename(ttype_val),
                    'stypename': _hung_line_stypename(ln['stype_hung']),
                    'pmcode': ln['pmcode_hung'] or '',
                    'asscode1': ln['asscode1_hung'] or '',
                    'asscode2': ln['asscode2_hung'] or '',
                    'ccode': ln['otherserno_hung'] or '',
                })
            for d in data:
                d['items'] = item_map.get(d['uuid'], [])
                d['item_details'] = item_details_map.get(d['uuid'], [])
                stypes = stype_map.get(d['uuid'], [])
                if stypes and all(s == 'P' for s in stypes):
                    d['stype_summary'] = 'all_gift'
                elif stypes and any(s == 'P' for s in stypes):
                    d['stype_summary'] = 'mixed'
                else:
                    d['stype_summary'] = 'all_normal'
                if d.get('paycode'):
                    _payinfo = _resolve_paycard_plan_info(
                        company, d.get('paycode', ''), d.get('cardtype', ''),
                        stypes[0] if stypes else 'N'
                    )
                    d['paytype'] = _payinfo.get('paytype', '')
                    d['paytypename'] = _payinfo.get('paytypename', '')
                    d['cardtypename'] = _payinfo.get('cardtypename', '')
                else:
                    d['paytype'] = ''
                    d['paytypename'] = ''
                    d['cardtypename'] = ''
        else:
            for d in data:
                d['items'] = []
                d['item_details'] = []
                d['stype_summary'] = 'all_normal'
                if d.get('paycode'):
                    _payinfo = _resolve_paycard_plan_info(
                        company, d.get('paycode', ''), d.get('cardtype', ''), 'N'
                    )
                    d['paytype'] = _payinfo.get('paytype', '')
                    d['paytypename'] = _payinfo.get('paytypename', '')
                    d['cardtypename'] = _payinfo.get('cardtypename', '')
                else:
                    d['paytype'] = ''
                    d['paytypename'] = ''
                    d['cardtypename'] = ''
    else:
        for d in data:
            d['items'] = []
            d['item_details'] = []
            d['stype_summary'] = 'all_normal'

    if psstatus == '70':
        hungs_list = [d['exptxserno'] for d in data if d.get('exptxserno')]
        if hungs_list:
            serno_map = dict(Expvstoll.objects.filter(
                company=company, hungserno__in=hungs_list
            ).values_list('hungserno', 'exptxserno'))
            for d in data:
                co = serno_map.get(d.get('exptxserno', ''), '')
                if co:
                    d['exptxserno'] = co

    return JsonResponse(data, safe=False)

@csrf_exempt
def get_hung_detail(request):
    '''获取挂单的项目明细'''
    hunguuid = request.GET.get('hunguuid', '')
    company = request.GET.get('company', '')
    if not hunguuid:
        return JsonResponse([], safe=False)
    try:
        uuid_obj = _parse_uuid_loose(hunguuid)
    except:
        return JsonResponse([], safe=False)

    items = ExpenseHung.objects.filter(hunguuid=uuid_obj, flag='Y').order_by('ditem_hung')
    ecodes = set()
    for it in items:
        if it.pmcode_hung: ecodes.add(it.pmcode_hung)
        if it.asscode1_hung: ecodes.add(it.asscode1_hung)
        if it.asscode2_hung: ecodes.add(it.asscode2_hung)
    emp_map = {}
    if ecodes:
        for em in Empl.objects.filter(company=company, ecode__in=list(ecodes)).only('ecode', 'ename'):
            emp_map[em.ecode] = em.ename

    data = []
    for item in items:
        ttype = item.ttype_hung or ''
        icode = item.srvcode_hung or ''
        data.append({
            'ditem': item.ditem_hung or '',
            'ttype': ttype,
            'ttypename': _hung_line_ttypename(ttype),
            'srvcode': icode,
            'itemname': _resolve_hung_itemname(company, ttype, icode),
            'price': float(item.s_price_hung or 0),
            'qty': float(item.s_qty_hung or 0),
            'mount': float(item.s_mount_hung or 0),
            'stype': item.stype_hung or '',
            'stypename': _hung_line_stypename(item.stype_hung),
            'pmname': emp_map.get(item.pmcode_hung, ''),
            'assname1': emp_map.get(item.asscode1_hung, ''),
            'assname2': emp_map.get(item.asscode2_hung, ''),
            'paycardno': item.otherserno_hung or '',
            'pmcode': item.pmcode_hung or '',
            'asscode1': item.asscode1_hung or '',
            'asscode2': item.asscode2_hung or '',
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@csrf_exempt
def search_vip(request):
    """搜索会员：按会员号、姓名、手机号模糊匹配"""
    if request.method != 'GET':
        return JsonResponse({'ok': False, 'message': '仅支持GET请求'})
    company = request.GET.get('company', '')
    keyword = request.GET.get('keyword', '').strip()
    if not company or not keyword:
        return JsonResponse([])
    try:
        qs = Vip.objects.filter(
            company=company,
            valiflag='Y',
        ).filter(
            models.Q(vcode__icontains=keyword) |
            models.Q(vname__icontains=keyword) |
            models.Q(mtcode__icontains=keyword)
        ).order_by('vcode')[:20]
        data = [{'uuid': str(v.uuid), 'vname': v.vname or '', 'vcode': v.vcode or '', 'mtcode': v.mtcode or ''} for v in qs]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})

@csrf_exempt
def update_hung_item_employees(request):
    '''更新挂单明细的员工信息'''
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    ditem = data.get('ditem', '')
    hunguuid = data.get('hunguuid', '')
    company = data.get('company', '')
    pmcode = data.get('pmcode', '') or ''
    asscode1 = data.get('asscode1', '') or ''
    asscode2 = data.get('asscode2', '') or ''
    if not ditem or not hunguuid:
        return JsonResponse({'ok': False, 'message': '缺少参数'})
    try:
        uuid_obj = _parse_uuid_loose(hunguuid)
        ExpenseHung.objects.filter(
            company=company, hunguuid=uuid_obj, ditem_hung=ditem, flag='Y'
        ).update(
            pmcode_hung=pmcode,
            asscode1_hung=asscode1,
            asscode2_hung=asscode2,
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})





@csrf_exempt
def void_hung_order(request):
    '''作废挂账单：标记 valiflag_hung=N, 售卡创建的卡片 status=C'''
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    hunguuid = data.get('hunguuid', '')
    company = data.get('company', '')
    if not hunguuid:
        return JsonResponse({'ok': False, 'message': '缺少 hunguuid'})
    try:
        uuid_obj = _parse_uuid_loose(hunguuid)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 hunguuid'})
    try:
        with transaction.atomic():
            hung = ExpvstollHung.objects.get(uuid=uuid_obj, company=company, flag='Y')
            hung.valiflag_hung = 'N'
            hung.save()
            # 作废售卡生成的卡片
            for item in ExpenseHung.objects.filter(company=company, hunguuid=hung, ttype_hung='C', flag='Y'):
                ccode = item.dnote_hung or ''
                if ccode:
                    Cardinfo.objects.filter(company=company, ccode=ccode, status='P').update(status='C')
            return JsonResponse({'ok': True})
    except ExpvstollHung.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '挂账单不存在'})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})

@csrf_exempt
def categorized_items(request):
    """获取可售项目的分类树和项目列表（树 + 搜索用）"""
    company = request.GET.get('company', '')
    ttype = request.GET.get('ttype', 'S')
    if not company:
        return JsonResponse({'categories': [], 'items': []})

    categories = []
    items = []

    if ttype == 'S':
        cat_qs = Appoption.objects.filter(company=company, flag='Y', seg='srvdisplayclass1').values('itemname', 'itemvalues')
        categories = [{'code': c['itemname'], 'name': c['itemvalues'], 'children': []} for c in cat_qs]
        item_qs = Serviece.objects.filter(company=company, flag='Y').values('svrcdoe', 'svrname', 'price', 'displayclass1')
        items = [{'code': r['svrcdoe'], 'name': r['svrname'], 'price': float(r['price'] or 0), 'ttype': 'S', 'category': r['displayclass1'] or ''} for r in item_qs]
    elif ttype == 'G':
        cat_qs = Appoption.objects.filter(company=company, flag='Y', seg='goodsdisplayclass1').values('itemname', 'itemvalues')
        categories = [{'code': c['itemname'], 'name': c['itemvalues'], 'children': []} for c in cat_qs]
        item_qs = Goods.objects.filter(company=company, flag='Y').values('gcode', 'gname', 'price', 'displayclass1')
        items = [{'code': r['gcode'], 'name': r['gname'], 'price': float(r['price'] or 0), 'ttype': 'G', 'category': r['displayclass1'] or ''} for r in item_qs]
    elif ttype == 'C':
        item_qs = Cardtype.objects.filter(company=company, flag='Y').values('cardtype', 'cardname', 'price', 'suptype', 'comptype', 'brand')
        # 用品牌（brand）分类——不按公司过滤，brand 是全局配置
        cat_qs = Appoption.objects.filter(company=company, flag='Y', seg='brand').values('itemname', 'itemvalues')
        print(f'[Debug] C-categories company={company} brand_count={cat_qs.count()}')
        for _bc in cat_qs:
            print(f'[Debug]   brand: {_bc}')
        cat_list = list(cat_qs)
        categories = [{'code': c['itemname'], 'name': c['itemvalues'], 'children': []} for c in cat_list]
        # 无品牌数据时后备用 comptype
        if not categories:
            categories = [
                {'code': 'amount', 'name': '储值卡', 'children': []},
                {'code': 'times', 'name': '疗程卡', 'children': []},
            ]
        else:
            categories.append({'code': '__other__', 'name': '其他', 'children': []})
        items = [{
            'code': r['cardtype'], 'name': r['cardname'],
            'price': float(r['price'] or 0), 'ttype': 'C',
            'comptype': r['comptype'] or '', 'suptype': r['suptype'] or '',
            'category': r['brand'] or '__other__',
        } for r in item_qs]

    return JsonResponse({'categories': categories, 'items': items})


@csrf_exempt
def active_promotions(request):
    """获取营销活动。无 uuid 参数则只返回列表，有 uuid 返回该活动完整明细"""
    company = request.GET.get('company', '')
    uuid_param = request.GET.get('uuid', '')
    if not company:
        return JsonResponse([], safe=False)

    MAINTTYPE_NAMES = {'10': '特价活动', '20': '特殊折扣活动', '30': '组合销售活动'}

    if uuid_param:
        try:
            p = Promotions.objects.get(company=company, flag='Y', promotionsstatus='active', uuid=_parse_uuid_loose(uuid_param))
        except:
            return JsonResponse({}, safe=False)

        sv_map, gd_map = {}, {}
        def _resolve(sgcode):
            return sv_map.get(sgcode, gd_map.get(sgcode, sgcode))

        items, group_items = [], []

        if p.mainttype in ('10', '20') and p.mainpgroupid:
            for d in Promotionsgroupdetail.objects.filter(pgroupid=p.mainpgroupid, flag='Y').values(
                    'ttype', 'pgcode', 'qty1', 'price1', 'disc', 'amount1', 'oriprice'):
                sgcode = d['pgcode'] or ''
                all_codes = [d['pgcode']]
                for sv in Serviece.objects.filter(company=company, svrcdoe__in=all_codes).only('svrcdoe', 'svrname'):
                    sv_map[sv.svrcdoe] = sv.svrname
                for g in Goods.objects.filter(company=company, gcode__in=all_codes).only('gcode', 'gname'):
                    gd_map[g.gcode] = g.gname
                pp = float(d['price1'] or 0)
                items.append({
                    'ttype': d['ttype'] or 'S', 'sgcode': sgcode,
                    'itemname': _resolve(sgcode),
                    's_qty': float(d['qty1'] or 1),
                    's_price': float(d['oriprice'] or 0),
                    'promotionsprice': pp,
                    'promotionsqty': float(d['qty1'] or 0),
                    'promotionsamount': float(d['amount1'] or 0) or (float(d['qty1'] or 1) * pp),
                    'stype': 'N',
                })
        elif p.mainttype == '30':
            combo_details = Promotionsdetail.objects.filter(promotionsid=p.promotionsid, flag='Y').values(
                'ttype', 'sgcode', 's_qty', 's_price', 'promotionsprice', 'promotionsqty', 'promotionsamount', 'stype')
            all_codes = [d['sgcode'] for d in combo_details if d.get('sgcode')]
            for sv in Serviece.objects.filter(company=company, svrcdoe__in=all_codes).only('svrcdoe', 'svrname'):
                sv_map[sv.svrcdoe] = sv.svrname
            for g in Goods.objects.filter(company=company, gcode__in=all_codes).only('gcode', 'gname'):
                gd_map[g.gcode] = g.gname
            for d in combo_details:
                sgcode = d['sgcode'] or ''
                pp = float(d['promotionsprice'] or 0)
                if not pp: pp = float(d['s_price'] or 0)
                ct = d['ttype'] or ''
                if not ct: ct = 'S' if sgcode in sv_map else ('G' if sgcode in gd_map else '')
                group_items.append({
                    'sgcode': sgcode, 'itemname': _resolve(sgcode),
                    'qty': float(d['promotionsqty'] or 1),
                    'price': pp, 'promotionsprice': pp,
                    'amount': float(d['promotionsamount'] or 0) or (float(d['promotionsqty'] or 1) * pp),
                    'ttype': ct,
                })
            items = list(Promotionsdetail.objects.filter(promotionsuuid=p.uuid, flag='Y').values(
                'ttype', 'sgcode', 's_qty', 's_price', 'promotionsprice', 'promotionsqty', 'promotionsamount', 'stype'))
        else:
            items = list(Promotionsdetail.objects.filter(promotionsuuid=p.uuid, flag='Y').values(
                'ttype', 'sgcode', 's_qty', 's_price', 'promotionsprice', 'promotionsqty', 'promotionsamount', 'stype'))

        combo_total = sum(gi['amount'] for gi in group_items) if group_items else 0
        return JsonResponse({
            'uuid': str(p.uuid), 'promotionsid': p.promotionsid or '',
            'promotionsname': p.promotionsname or '',
            'mainttype': p.mainttype or '',
            'mainttype_name': MAINTTYPE_NAMES.get(p.mainttype or '', ''),
            'fromdate': p.fromdate or '', 'todate': p.todate or '',
            'disc': float(p.disc) if p.disc else None,
            's_price': float(p.s_price) if p.s_price else None,
            'combo_total': combo_total,
            'items': items, 'group_items': group_items,
        })

    # 无 uuid：只返回活动列表（不含明细，但组合活动附带 combo_total）
    promos = list(Promotions.objects.filter(
        company=company, flag='Y', promotionsstatus='active',
    )[:30])

    # 批量算 combo_total
    combo_pids = [p.promotionsid for p in promos if p.mainttype == '30' and p.promotionsid]
    combo_totals = {}
    if combo_pids:
        for d in Promotionsdetail.objects.filter(promotionsid__in=combo_pids, flag='Y').values(
                'promotionsid', 'promotionsamount', 'promotionsqty', 'promotionsprice'):
            pid = d['promotionsid'] or ''
            amt = float(d['promotionsamount'] or 0) or (float(d['promotionsqty'] or 1) * float(d['promotionsprice'] or 0))
            combo_totals[pid] = combo_totals.get(pid, 0) + amt

    return JsonResponse([{
        'uuid': str(p.uuid), 'promotionsid': p.promotionsid or '',
        'promotionsname': p.promotionsname or '',
        'mainttype': p.mainttype or '',
        'mainttype_name': MAINTTYPE_NAMES.get(p.mainttype or '', ''),
        'fromdate': p.fromdate or '', 'todate': p.todate or '',
        'disc': float(p.disc) if p.disc else None,
        's_price': float(p.s_price) if p.s_price else None,
        'combo_total': combo_totals.get(p.promotionsid, 0) if p.mainttype == '30' else 0,
    } for p in promos], safe=False)



# ====== 选品接口（从 cashier 迁入） ======

@csrf_exempt
def service_items(request):
    '''获取服务项目列表'''
    company = request.GET.get('company', '')
    qs = Serviece.objects.filter(company=company, flag='Y').values('svrcdoe', 'svrname', 'price')
    data = [{'code': r['svrcdoe'], 'name': r['svrname'], 'price': float(r['price'] or 0), 'ttype': 'S'} for r in qs]
    return JsonResponse(data, safe=False)


@csrf_exempt
def goods_items(request):
    '''获取商品列表'''
    company = request.GET.get('company', '')
    qs = Goods.objects.filter(company=company, flag='Y').values('gcode', 'gname', 'price')
    data = [{'code': r['gcode'], 'name': r['gname'], 'price': float(r['price'] or 0), 'ttype': 'G'} for r in qs]
    return JsonResponse(data, safe=False)


@csrf_exempt
def cardtype_items(request):
    '''获取卡类列表（用于购卡选型）'''
    company = request.GET.get('company', '')
    qs = Cardtype.objects.filter(company=company, flag='Y').values('cardtype', 'cardname', 'suptype', 'comptype', 'price')
    data = [{'code': r['cardtype'], 'name': r['cardname'], 'price': float(r['price'] or 0), 'ttype': 'C', 'comptype': r['comptype'] or '', 'suptype': r['suptype'] or ''} for r in qs]
    return JsonResponse(data, safe=False)


@csrf_exempt
def sysadmin_models(request):
    """返回 sysadmin 模型列表（挂载到 /api/adviser/ 路由下以解决 Vite proxy 问题）"""
    from sysadmin.registry import get_registry
    groups = get_registry()
    result = []
    group_order = ['基础配置', '核心业务', '营销']
    for g in group_order:
        models = groups.get(g, [])
        if not models:
            continue
        result.append({
            'name': g,
            'models': [{
                'id': f"{m['app_label']}.{m['model_name']}",
                'verbose_name': m['verbose_name'],
                'icon': m['icon'],
            } for m in models],
        })
    return JsonResponse({'groups': result})

@csrf_exempt
def sysadmin_meta(request, app_label, model_name):
    """GET /adviser/sysadmin-models/{app}.{model}/meta/ — 字段元数据"""
    from sysadmin.views import model_meta as original
    return original(request, app_label, model_name)

@csrf_exempt
def sysadmin_data(request, app_label, model_name):
    """GET/POST /adviser/sysadmin-data/{app}.{model}/ — 数据列表/新建"""
    from sysadmin.views import model_data as original
    return original(request, app_label, model_name)

@csrf_exempt
def sysadmin_detail(request, app_label, model_name, pk):
    """GET/PUT/DELETE /adviser/sysadmin-data/{app}.{model}/{pk}/ — 详情/更新/删除"""
    from sysadmin.views import model_data_detail as original
    return original(request, app_label, model_name, pk)

@csrf_exempt
def sysadmin_search(request):
    """GET /adviser/sysadmin-search/ — FK 搜索"""
    from sysadmin.views import related_search as original
    return original(request)

@csrf_exempt
def srvtopty_tree(request):
    """GET /adviser/srvtopty-tree/ — 服务大类树形结构"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    if not company:
        return JsonResponse({'tree': []})
    from baseinfo.models import Srvtopty
    from sysadmin.views import build_tree
    qs = Srvtopty.objects.filter(company=company, flag='Y')
    items = list(qs.values('pk', 'topcode', 'ttname', 'parentcode'))
    tree = build_tree(items)
    return JsonResponse({'tree': tree})


@csrf_exempt
def srvtopty_save(request):
    """POST /adviser/srvtopty-save/ — 新增/编辑服务大类"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)
    company = data.get('company') or request.headers.get('X-Company', '')
    topcode = data.get('topcode', '')
    ttname = data.get('ttname', '')
    parentcode = data.get('parentcode', '') or ''
    pk = data.get('pk', '')
    if not company or not topcode or not ttname:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'}, status=400)
    from baseinfo.models import Srvtopty
    if pk:
        try:
            obj = Srvtopty.objects.get(pk=pk)
            obj.topcode = topcode
            obj.ttname = ttname
            obj.parentcode = parentcode
            obj.save()
            return JsonResponse({'ok': True, 'pk': obj.pk})
        except Srvtopty.DoesNotExist:
            return JsonResponse({'ok': False, 'message': '分类不存在'}, status=404)
    # 新建
    obj = Srvtopty.objects.create(
        company=company, topcode=topcode, ttname=ttname,
        parentcode=parentcode, flag='Y'
    )
    return JsonResponse({'ok': True, 'pk': obj.pk})


@csrf_exempt
def srvtopty_delete(request):
    """POST /adviser/srvtopty-delete/ — 软删除服务大类"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)
    pk = data.get('pk', '')
    from baseinfo.models import Srvtopty
    try:
        obj = Srvtopty.objects.get(pk=pk)
        obj.flag = 'N'
        obj.save()
        return JsonResponse({'ok': True})
    except Srvtopty.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '分类不存在'}, status=404)


@csrf_exempt
def appoption_list(request):
    """GET /adviser/appoption-list/?seg=brand — 获取 Appoption 选项（用于下拉）"""
    seg = request.GET.get('seg', '')
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    if not seg or not company:
        return JsonResponse({'results': []})
    from baseinfo.models import Appoption
    qs = Appoption.objects.filter(company=company, flag='Y', seg=seg).order_by('itemname')
    results = []
    for o in qs:
        code = o.itemname or o.itemvalues
        name = o.itemvalues or o.itemname
        results.append({'value': code, 'label': name, 'code': code, 'name': name})
    return JsonResponse({'results': results})


@csrf_exempt
def servieceprice_list(request):
    """GET /adviser/servieceprice-list/?srvcode=xxx — 获取服务项目价位"""
    srvcode = request.GET.get('srvcode', '')
    if not srvcode:
        return JsonResponse({'results': []})
    from baseinfo.models import Servieceprice
    qs = Servieceprice.objects.filter(srvcode=srvcode, flag='Y').order_by('qty')
    results = []
    for p in qs:
        results.append({
            'pk': p.pk,
            'qty': p.qty or 1,
            'price': float(p.price or 0),
            'amount': float(p.amount or 0),
            'commission': float(p.commission or 0),
            'achivement': float(p.achivement or 1),
            'fromdate': p.fromdate.strftime('%Y-%m-%d') if p.fromdate else '',
            'todate': p.todate.strftime('%Y-%m-%d') if p.todate else '',
            'saleflag': p.saleflag or 'Y',
            'stype': p.stype or 'N',
        })
    return JsonResponse({'results': results})


@csrf_exempt
def servieceprice_save(request):
    """POST /adviser/servieceprice-save/ — 批量保存价位"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)
    srvcode = data.get('srvcode', '')
    company = data.get('company') or request.headers.get('X-Company', '')
    prices = data.get('prices', [])
    if not srvcode:
        return JsonResponse({'ok': False, 'message': '缺少项目编号'}, status=400)
    from baseinfo.models import Servieceprice
    existing = list(Servieceprice.objects.filter(srvcode=srvcode, flag='Y'))
    existing_map = {p.pk: p for p in existing}
    submitted_pks = []
    for item in prices:
        pk = item.get('pk')
        qty = int(item.get('qty') or 1)
        price = Decimal(str(item.get('price') or 0))
        amount = Decimal(str(item.get('amount') or 0))
        if not amount:
            amount = qty * price
        commission = Decimal(str(item.get('commission') or 0))
        achivement = Decimal(str(item.get('achivement') or 1))
        fromdate_str = str(item.get('fromdate') or '')
        todate_str = str(item.get('todate') or '')
        saleflag = item.get('saleflag') or 'Y'
        stype = item.get('stype') or 'N'
        from datetime import datetime
        fromdate = None
        todate = None
        if fromdate_str:
            try: fromdate = datetime.strptime(fromdate_str, '%Y-%m-%d').date()
            except: pass
        if todate_str:
            try: todate = datetime.strptime(todate_str, '%Y-%m-%d').date()
            except: pass
        if pk and int(pk) in existing_map:
            obj = existing_map[int(pk)]
            obj.qty = qty
            obj.price = price
            obj.amount = amount
            obj.commission = commission
            obj.achivement = achivement
            obj.fromdate = fromdate
            obj.todate = todate
            obj.saleflag = saleflag
            obj.stype = stype
            obj.save()
            submitted_pks.append(int(pk))
        else:
            obj = Servieceprice.objects.create(
                company=company,
                srvcode=srvcode,
                qty=qty,
                price=price,
                amount=amount,
                commission=commission,
                achivement=achivement,
                fromdate=fromdate,
                todate=todate,
                saleflag=saleflag,
                stype=stype,
                flag='Y',
            )
            submitted_pks.append(obj.pk)
    for p in existing:
        if p.pk not in submitted_pks:
            p.flag = 'N'
            p.save()
    return JsonResponse({'ok': True, 'count': len(prices)})


@csrf_exempt
def serviece_list(request):
    """GET /adviser/serviece-list/ — 服务项目快速列表（只取列表所需字段）"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')
    topcode = request.GET.get('topcode', '')
    uncategorized = request.GET.get('uncategorized', '') == '1'
    brand = request.GET.get('brand', '')
    displayclass1 = request.GET.get('displayclass1', '')
    valiflag = request.GET.get('valiflag', '')

    from baseinfo.models import Serviece
    from django.db.models import Q
    qs = Serviece.objects.filter(company=company, flag='Y')

    if uncategorized:
        qs = qs.filter(Q(topcode__isnull=True) | Q(topcode=''))
    elif topcode:
        qs = qs.filter(topcode=topcode)

    if search:
        qs = qs.filter(Q(svrcdoe__icontains=search) | Q(svrname__icontains=search))

    if brand:
        qs = qs.filter(brand=brand)

    if displayclass1:
        qs = qs.filter(displayclass1=displayclass1)

    if valiflag:
        qs = qs.filter(valiflag=valiflag)

    total = qs.count()

    # 只取列表需要的字段，大幅减少数据传输
    rows = list(qs.order_by('svrcdoe').values(
        'pk', 'svrcdoe', 'svrname', 'topcode', 'brand', 'displayclass1',
        'price', 'costamount', 'stdmins', 'qty', 'saleflag', 'valiflag'
    )[(page - 1) * page_size: page * page_size])

    # Decimal → float 转换
    for row in rows:
        for k, v in row.items():
            if isinstance(v, Decimal):
                row[k] = float(v)

    return JsonResponse({'total': total, 'rows': rows, 'page': page, 'page_size': page_size})


@csrf_exempt
def ruler_list(request):
    """GET /adviser/ruler-list/ — 逻辑卡规则列表"""
    from baseinfo.models import Ruler
    qs = Ruler.objects.filter(flag='Y').order_by('pk')
    results = [{
        'id': r.pk,
        'rulername': r.rulername or '',
        'ruler': r.ruler or '',
    } for r in qs]
    return JsonResponse({'results': results})


@csrf_exempt
def ruler_save(request):
    """POST /adviser/ruler-save/ — 新增/编辑逻辑卡规则"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'}, status=400)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)

    from baseinfo.card_rules import parse_ruler
    from baseinfo.models import Ruler

    rulername = (data.get('rulername') or '').strip()
    ruler = (data.get('ruler') or '').strip()
    if not rulername or not parse_ruler(ruler):
        return JsonResponse({'ok': False, 'message': '规则名称或规则格式不正确'}, status=400)

    pk = data.get('id') or data.get('pk') or ''
    if pk:
        obj = Ruler.objects.filter(pk=pk).first()
        if not obj:
            return JsonResponse({'ok': False, 'message': '规则不存在'}, status=404)
        obj.rulername = rulername
        obj.ruler = ruler
        obj.flag = 'Y'
        obj.save()
    else:
        obj = Ruler.objects.create(rulername=rulername, ruler=ruler, flag='Y')
    return JsonResponse({'ok': True, 'id': obj.pk})


@csrf_exempt
def ruler_delete(request):
    """POST /adviser/ruler-delete/ — 软删除逻辑卡规则"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'}, status=400)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)

    from baseinfo.models import Ruler
    pk = data.get('id') or data.get('pk') or ''
    obj = Ruler.objects.filter(pk=pk).first()
    if not obj:
        return JsonResponse({'ok': False, 'message': '规则不存在'}, status=404)
    obj.flag = 'N'
    obj.save()
    return JsonResponse({'ok': True})


@csrf_exempt
def cardtype_discount_list(request):
    """GET /adviser/cardtype-discount-list/?cardtype=CT001 — 折扣分类规则列表"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    cardtype = request.GET.get('cardtype', '')
    from baseinfo.models import CardtypeVsDiscountClass
    qs = CardtypeVsDiscountClass.objects.filter(company=company, flag='Y')
    if cardtype:
        qs = qs.filter(cardtype=cardtype)
    rows = [{
        'pk': str(r.pk),
        'cardtype': r.cardtype or '',
        'ttype': r.ttype or 'S',
        'discountclass': r.discountclass or '',
        'discounttype': r.discounttype or 'DISC',
        'disc': float(r.disc or 0),
        'price': float(r.price or 0),
        'consume_flag': r.consume_flag or 'Y',
        'emplguideperc': float(r.emplguideperc or 1),
    } for r in qs.order_by('cardtype', 'ttype', 'discountclass')]
    return JsonResponse({'results': rows})


@csrf_exempt
def cardtype_discount_save(request):
    """POST /adviser/cardtype-discount-save/ — 批量保存折扣分类规则（全量替换）"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'}, status=400)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)

    company = data.get('company') or request.headers.get('X-Company', '')
    cardtype = data.get('cardtype', '')
    rules = data.get('rules', [])
    if not company or not cardtype:
        return JsonResponse({'ok': False, 'message': '缺少卡类编号'}, status=400)

    from baseinfo.models import Cardtype, CardtypeVsDiscountClass
    existing = list(CardtypeVsDiscountClass.objects.filter(
        company=company, cardtype=cardtype, flag='Y'))
    existing_by_pk = {str(r.pk): r for r in existing}
    existing_by_key = {(r.ttype or 'S', r.discountclass or ''): r for r in existing}
    submitted = []

    for item in rules:
        ttype = (item.get('ttype') or 'S').upper()
        discountclass = item.get('discountclass') or ''
        if not discountclass:
            continue
        pk = str(item.get('pk') or '')
        obj = existing_by_pk.get(pk) or existing_by_key.get((ttype, discountclass))
        discounttype = item.get('discounttype') or 'DISC'
        disc = Decimal(str(item.get('disc') or 0))
        price = Decimal(str(item.get('price') or 0))
        consume_flag = item.get('consume_flag') or 'Y'
        emplguideperc = Decimal(str(item.get('emplguideperc') or 1))
        if obj:
            obj.ttype = ttype
            obj.discountclass = discountclass
            obj.discounttype = discounttype
            obj.disc = disc
            obj.price = price
            obj.consume_flag = consume_flag
            obj.emplguideperc = emplguideperc
            obj.flag = 'Y'
            obj.save()
        else:
            ct = Cardtype.objects.filter(company=company, cardtype=cardtype, flag='Y').first()
            obj = CardtypeVsDiscountClass.objects.create(
                company=company,
                cardtype=cardtype,
                cardtypeuuid=ct,
                ttype=ttype,
                discountclass=discountclass,
                discounttype=discounttype,
                disc=disc,
                price=price,
                consume_flag=consume_flag,
                emplguideperc=emplguideperc,
                flag='Y',
            )
        submitted.append(obj.pk)

    for r in existing:
        if r.pk not in submitted:
            r.flag = 'N'
            r.save()
    return JsonResponse({'ok': True, 'count': len(rules)})


@csrf_exempt
def card_pricing(request):
    """POST /adviser/card-pricing/ — 批量计算卡支付单价与消费权限"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'}, status=400)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)

    from baseinfo.card_rules import resolve_card_item_price
    company = data.get('company') or request.headers.get('X-Company', '')
    cardtypeuuid = data.get('cardtypeuuid') or ''
    ccode = data.get('ccode') or ''
    items = data.get('items') or []

    ct = None
    ci = None
    if cardtypeuuid:
        ct = Cardtype.objects.filter(uuid=cardtypeuuid, flag='Y').first()
    elif ccode:
        ci = Cardinfo.objects.filter(
            company=company, ccode=ccode, flag='Y'
        ).order_by('-last_modified').first()
        if ci:
            ct = ci.cardtypeuuid

    results = []
    for it in items:
        ttype = it.get('ttype') or 'S'
        code = it.get('code') or it.get('srvcode') or it.get('gcode') or ''
        discountclass = it.get('discountclass') or ''
        topcode = it.get('topcode') or ''
        price = Decimal(str(it.get('price') or 0))
        qty = int(it.get('qty') or 1)
        res = resolve_card_item_price(
            company, ct, ci,
            ttype=ttype, itemcode=code, discountclass=discountclass,
            topcode=topcode, original_price=price,
        )
        results.append({
            'code': code,
            'ttype': ttype,
            'qty': qty,
            'original_price': float(price),
            'price': float(res['price']),
            'amount': float(res['price'] * qty),
            'allowed': res['allowed'],
            'source': res['source'],
            'reason': res.get('reason', ''),
        })
    return JsonResponse({'cardtype': ct.cardtype if ct else '', 'results': results})


@csrf_exempt
def goodsct_tree(request):
    """GET /adviser/goodsct-tree/ — 商品大类树形结构"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    if not company:
        return JsonResponse({'tree': []})
    from baseinfo.models import Goodsct
    from sysadmin.views import build_tree
    qs = Goodsct.objects.filter(company=company, flag='Y')
    items = list(qs.values('pk', 'goodsct', 'goodsctname', 'parent'))
    tree = build_tree(items, key='goodsct', label='goodsctname', parent_key='parent')
    return JsonResponse({'tree': tree})


@csrf_exempt
def goodsct_save(request):
    """POST /adviser/goodsct-save/ — 新增/编辑商品大类"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)
    company = data.get('company') or request.headers.get('X-Company', '')
    goodsct = data.get('goodsct', '')
    goodsctname = data.get('goodsctname', '')
    parent = data.get('parent', '') or ''
    pk = data.get('pk', '')
    if not company or not goodsct or not goodsctname:
        return JsonResponse({'ok': False, 'message': '缺少必要参数'}, status=400)
    from baseinfo.models import Goodsct
    if pk:
        try:
            obj = Goodsct.objects.get(pk=pk)
            obj.goodsct = goodsct
            obj.goodsctname = goodsctname
            obj.parent = parent
            obj.save()
            return JsonResponse({'ok': True, 'pk': obj.pk})
        except Goodsct.DoesNotExist:
            return JsonResponse({'ok': False, 'message': '分类不存在'}, status=404)
    obj = Goodsct.objects.create(
        company=company, goodsct=goodsct, goodsctname=goodsctname,
        parent=parent, flag='Y'
    )
    return JsonResponse({'ok': True, 'pk': obj.pk})


@csrf_exempt
def goodsct_delete(request):
    """POST /adviser/goodsct-delete/ — 软删除商品大类"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': '仅支持 POST'})
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'ok': False, 'message': '无效的 JSON'}, status=400)
    pk = data.get('pk', '')
    from baseinfo.models import Goodsct
    try:
        obj = Goodsct.objects.get(pk=pk)
        obj.flag = 'N'
        obj.save()
        return JsonResponse({'ok': True})
    except Goodsct.DoesNotExist:
        return JsonResponse({'ok': False, 'message': '分类不存在'}, status=404)


@csrf_exempt
def goods_list(request):
    """GET /adviser/goods-list/ — 商品快速列表（只取列表所需字段）"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')
    goodsct = request.GET.get('goodsct', '')
    uncategorized = request.GET.get('uncategorized', '') == '1'
    brand = request.GET.get('brand', '')
    displayclass1 = request.GET.get('displayclass1', '')
    valiflag = request.GET.get('valiflag', '')

    from baseinfo.models import Goods
    from django.db.models import Q
    qs = Goods.objects.filter(company=company, flag='Y')

    if uncategorized:
        qs = qs.filter(Q(goodsct__isnull=True) | Q(goodsct=''))
    elif goodsct:
        qs = qs.filter(goodsct=goodsct)

    if search:
        qs = qs.filter(Q(gcode__icontains=search) | Q(gname__icontains=search))

    if brand:
        qs = qs.filter(brand=brand)

    if displayclass1:
        qs = qs.filter(displayclass1=displayclass1)

    if valiflag:
        qs = qs.filter(valiflag=valiflag)

    total = qs.count()

    rows = list(qs.order_by('gcode').values(
        'pk', 'gcode', 'gname', 'goodsct', 'spec', 'brand', 'displayclass1',
        'price', 'buyprc', 'qty', 'unit', 'barcode',
        'minivalues', 'maxvalues', 'saleflag', 'valiflag'
    )[(page - 1) * page_size: page * page_size])

    for row in rows:
        for k, v in row.items():
            if isinstance(v, Decimal):
                row[k] = float(v)

    return JsonResponse({'total': total, 'rows': rows, 'page': page, 'page_size': page_size})
