#coding=utf-8

from __future__ import unicode_literals
import math
from datetime import datetime,timedelta
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import uuid
#from pyecharts import Line3D
import json
import simplejson
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import  pagination,viewsets
from rest_framework.parsers import JSONParser
from django.db import connection
import json
import pandas as pd
from pandas.io.json import json_normalize
import tablib
from django.core.serializers import serialize
# REMOTE_HOST = "https://pyecharts.github.io/assets/js"

from adviser.models import ExpvstollHung,ExpenseHung,Cardinfo,Bookingevent,Cardinfo,ShoppingCart
from adviser.serializers import BookingeventSerializer,CardinfoSerializer
from baseinfo.models import Serviece,Servieceprice,Goods,Srvtopty,Srvrptype,Goodsct,Vip,Cardtype,Cardsupertype,Empl
from cashier.models import EarnestMoney
import common.constants
from common.models import Sequence

def sql_to_json(sql,params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)

        list_data = []
        desc = cursor.description
        if desc == None:
            return []
        columns = [col[0] for col in desc]
        for row in cursor.fetchall():
            list_data.append(dict(zip(columns, row)))
        # return cardtypelist

        json_data = json.dumps(list_data,cls=DjangoJSONEncoder)
        # print('json_data',json_data)
        cursor.close()
        # connection.close()
        connection.close()
        return json_data

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
        sql = " select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price s_price, a.leftqty leftqty, promotionsid,b.suptype suptype, a.status status ," \
              "  concat((case status when 'P' then '挂账-' else '正常-' end ),cardname,'(',trim(a.cardnote),')', a.leftqty,'*',a.s_price,'=',a.leftmoney) carddesc  " \
              " from cardinfo a, cardtype b " \
              " where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype " \
              " and a.status in ('O','P')" \
              " and a.vipuuid = %s and b.suptype=%s"

        params = (company + ' ' + vipuuid + ' ' + suptype).split()
        print('sql:', sql, 'params', params)
    except:
        params = (company+' '+ '%   %' ).split()

    try:
        comptype = request.GET['comptype']
        if comptype == 'amount':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, promotionsid,b.suptype suptype, a.status status ," \
                  "  a.stype stype, concat((case a.status when 'P' then '挂账-' else '正常-' end ),'-',a.stype,'-' , cardname,'-结余:',a.leftmoney) carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s"

            params = (company + ' ' + vipuuid + ' ' + comptype).split()

        if comptype == 'times':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, promotionsid,b.suptype suptype, a.status status ," \
                  "  a.stype stype,concat((case a.status when 'P' then '挂账-' else '正常-' end ),'-',a.stype,'-', cardname,'-',ifnull(a.cardnote,''),  '  结余:',a.leftqty,'次') carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype and a.leftqty >0 " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s" \
                  "  order by a.ccode"
            params = (company + ' ' + vipuuid + ' ' + comptype).split()

        if comptype == 'period':
            sql = "  select a.uuid uuid, vcode,ccode,a.cardtype cardtype ,cardname, a.cardtypeuuid cardtypeuuid, a.leftmoney leftmoney,  a.s_price price, a.leftqty leftqty, promotionsid,b.suptype suptype, a.status status ," \
                  "  a.stype stype, concat((case a.status when 'P' then '挂账-' else '正常-' end ),'-',a.stype,'-', cardname, '-',ifnull(a.cardnote,'') , '  结余:',a.leftqty,'次') carddesc " \
                  "  from cardinfo a, cardtype b " \
                  "  where a.flag='Y' and b.flag='Y' and a.company =%s and a.company = b.company and a.cardtype=b.cardtype and a.leftmoney >0 " \
                  "  and a.status in ('O','P')" \
                  "  and a.vipuuid = %s and b.comptype=%s " \
                  "  order by a.ccode"

            params = (company + ' ' + vipuuid + ' ' + comptype).split()

    except:
        params = (company+' '+ '%  %' ).split()

    json_data = sql_to_json(sql,params)
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
              "     where company=%s "\
              "      and storecode=%s "\
              "      group by storecode, whcode, gcode  "\
             "      ) b, goods g "\
             "  where a.company=b.company  and a.company = g.company  and a.storecode=b.storecode "\
             "  and a.gcode = b.gcode  and a.gcode = g.gcode "\
             "  and a.gtranukid = b.gtranukid and a.qty2>0" \
             " order by displayclass1,brand,itemcode" \
             " limit 50"

        # params = (company + ' ' + vipuuid ).split()
        params = (company +' ' +storecode ).split()
        print('sql:', sql, 'params', params)

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

def GetSerno(company,storecode,tablecode):
    try:
        sequence = Sequence.objects.get(company=company,storecode=storecode,tablecode=tablecode)
    except:
        sequence = Sequence.objects.create(company=company, storecode=storecode, tablecode=tablecode,sequence=0)
    print('sequence',sequence)
    sequence.sequence= sequence.sequence+1
    sequence.save()

    return company + '_'+ storecode +'_hung_'+ str(sequence.sequence)

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

                cardinfo = Cardinfo.objects.create(
                    company=company,storecode=storecode,ccode=newccode,vcode=vcode,cardtype=newcardtype,status='P',
                    leftqty=qty, s_price=price,leftmoney=leftmoney,svalue=amount,stype=stype,
                    suptype=cardtypeuuid.suptype,vipuuid=vip, cardtypeuuid=cardtypeuuid,promotionsid=promotionsid,cardnote=remark
                )
                paycardtype=''
                if len(payccode)>0:
                    try:
                        paycard=Cardinfo.objects.filter(company=company,status='O',ccode=payccode).filter()
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
                    company=company,storecode=storecode,
                    exptxserno_hung =exptxserno_hung,
                    ditem_hung='001',
                    ttype_hung = ttype,
                    stype_hung = stype,
                    srvcode_hung = newccode,
                    s_qty_hung = qty,
                    s_price_hung = price,
                    s_mount_hung = amount,
                    srvmondisc_hung=mondisc,
                    secdisc_hung=secdisc,
                    addvamoney_hung=leftmoney,
                    pmcode_hung = pmcode,
                    asscode1_hung = seccode,
                    asscode2_hung = thrcode,
                    newcardtype_hung = newcardtype,
                    hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
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
            hunguuid = ''.join(str(expvstollhung.uuid).split('-'))
        )
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
        print('1',request.GET['param'])
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
        except:
            remark=''


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

        print('2')
        shoppingcartitem.save()
        print('3')
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
                except:
                    remark = ''

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
    if request.method=='POST':
        data = json.loads(request.GET['param'])
        print('request param:', data)
        company = data['company']
        storecode = data['storecode']
        ecode = data['ecode']
        vipuuid = data['vipuuid'].replace('-','')
        ttype = data['ttype']

        sql = " select ccode, itemcode,itemname, qty, price,secdisc,mondisc,amount,pmcode,seccode,thrcode,promotionsid,uuid,ttype, stype, " \
              " ( case stype when 'P' then '赠送' when 'E' then '定金' else '正常' end) stypename,F_Getnamebysrvcode(itemcode,ttype,company) itemname," \
              " planqty, planamount, payedamount, oweamount, remark" \
              " from  shoppingcart " \
              " where 1=1 and flag='Y' and status='10'" \
              " and company=%s and storecode =%s and vipuuid = %s AND ttype=%s" \

        params = (company+' '+ storecode+ ' '+ vipuuid + ' '+ttype ).split()
        print(sql,params)
        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

    if request.method=='GET':
        try:
            company = request.GET['company']
        except:
            company=common.constants.COMPANYID

        try:
            storecode = request.GET['storecode']
        except:
            storecode='88'

        try:
            ecode = request.GET['ecode']
        except:
            ecode='888'

        try:
            vipuuid = request.GET['vipuuid'].replace('-','')
        except:
            vipuuid='123'

        try:
            ttype = request.GET['ttype']
        except:
            ttype='S'

        sql = " select ccode, itemcode,itemname, qty, price,secdisc,mondisc,amount,pmcode,seccode,thrcode,promotionsid,uuid,ttype, stype, " \
              " ( case stype when 'P' then '赠送'  when 'E' then '定金' else '正常'  end) stypename,F_Getnamebysrvcode(itemcode,ttype,company) itemname," \
              " planqty, planamount, payedamount, oweamount, remark" \
              " from  shoppingcart " \
              " where 1=1 and flag='Y' and status='10'" \
              " and company=%s and storecode =%s and vipuuid = %s AND ttype=%s" \

        params = (company+' '+ storecode+ ' '+ vipuuid + ' '+ttype ).split()
        print(sql, params)

        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
@transaction.atomic
def get_ShoppingCartItem(request):
    if request.method=='POST':
        data = json.loads(request.GET['param'])
        print('request param:', data)
        company = data['company']
        storecode = data['storecode']
        ecode = data['ecode']
        vipuuid = data['vipuuid'].replace('-','')
        try:
            uuid = data['uuid']
        except:
            uuid=''

        sql = " select ccode,itemcode,itemname, qty, price,secdisc,mondisc,amount,pmcode,seccode,thrcode,promotionsid,uuid,ttype, stype, " \
              " ( case stype when 'P' then '赠送' when 'E' then '定金' else '正常' end) stypename ,F_Getnamebysrvcode(itemcode,ttype,company) itemname, " \
              " planqty, planamount, payedamount, oweamount, remark,depositeflag" \
              " from  shoppingcart " \
              " where 1=1 and flag='Y' and status='10'" \
              " and company=%s and storecode =%s and vipuuid = %s AND uuid=%s" \

        params = (company+' '+ storecode+ ' '+ vipuuid + ' '+uuid ).split()

        json_data = sql_to_json(sql,params)
        return HttpResponse(json_data, content_type="application/json")

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
                expvstollhung = ExpvstollHung.objects.get_or_create(company=company,storecode=storecode,creater=ecode,valiflag_hung='Y',
                                                                    vsdate_hung=vsdate,vipuuid=vip,vcode_hung=vip.vcode,ccode_hung=payccode,
                                                                    cardtype_hung=cardtype,ttype_hung=ttype,psstatus_hung='10')[0]

                if expvstollhung.exptxserno_hung==None:
                    exptxserno_hung =  GetSerno(company, storecode, 'hung')
                    expvstollhung.exptxserno_hung=exptxserno_hung
                else:
                    exptxserno_hung = expvstollhung.exptxserno_hung

                hunguuid=str(expvstollhung.uuid).replace('-','')
                print('hunguuid=',hunguuid)
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
                                                          pmcode_hung=cartitem.pmcode,asscode1_hung=cartitem.seccode,asscode2_hung=cartitem.thrcode)
                print(expensehung.srvcode_hung)
                expensehung.save()

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
            expvstollhung = ExpvstollHung.objects.filter(company=company,storecode=storecode,valiflag_hung='Y',
                                                            vsdate_hung=vsdate,vipuuid=vip, psstatus_hung=psstatus,ccode_hung=payccode,ttype_hung=ttype)[0]
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

@csrf_exempt
def get_hung_byvipuuid(request):
    try:
        company=request.GET['company']
    except:
        company='yfy'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='88'

    try:
        ecode=request.GET['ecode']
    except:
        ecode='888'

    try:
        vipuuid = request.GET['vipuuid']
    except:
        vipuuid='%'
    print('vipuuid:',uuid)

    sql = " select a.exptxserno_hung exptxserno, a.uuid hunguuid, a.psstatus_hung psstatus, a.vsdate_hung vsdate, a.ccode_hung payccode, "\
          "  b.uuid itemuuid, b.DITEM_hung item, b.TTYPE_hung ttype,b.stype_hung stype," \
          "  (case b.ttype_hung when 'S' then '服务' when 'G' then '商品' when 'C' then '售卡' when 'I' then '充值' else '' end) ttypename ," \
          "  (case b.stype_hung when 'N' then '正常' when 'P' then '赠送' else '' end ) stypename, "\
          "  b.srvcode_hung itemcode, F_Getnamebysrvcode(b.srvcode_hung,b.ttype_hung,b.company) itemname, b.S_PRICE_hung price, b.S_QTY_hung qty, b.SECDISC_hung secdisc, "\
          "  b.srvmondisc_hung mondisc, b.S_MOUNT_hung amount, "\
          "  b.PMCODE_hung pmcode, b.ASSCODE1_hung seccode, b.ASSCODE2_hung thrcode"\
          "  from expvstoll_hung a, expense_hung b"\
          "  where 1=1 and a.valiflag_hung='Y' and a.flag='Y' and b.flag='Y' "\
          "  and a.company=b.company "\
          "  and a.company=%s and a.storecode=%s "\
          "  and a.uuid=b.hunguuid "\
          "  and a.vipuuid like replace(%s,'-','') "\
          "  and a.psstatus_hung  in ('10','20','30','40','50')"\
          "  order by  a.exptxserno_hung, a.vsdate_hung, a.psstatus_hung"

    print(sql)
    params = (company+' '+ storecode +' ' + vipuuid).split()
    print(params)

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_hungitem(request):
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

    sql = " select b.exptxserno_hung exptxserno, "\
          "  b.uuid itemuuid, b.DITEM_hung item, b.TTYPE_hung ttype,b.stype_hung stype,(case b.ttype_hung when 'S' then '服务' when 'G' then '商品' when 'C' then '售卡' when 'I' then '充值' else '' end ) ttypename,"\
          "  b.srvcode_hung itemcode, F_Getnamebysrvcode(b.srvcode_hung,b.ttype_hung,b.company) itemname, b.S_PRICE_hung price, b.S_QTY_hung qty, b.SECDISC_hung secdisc, "\
          "  b.srvmondisc_hung mondisc, b.S_MOUNT_hung amount, "\
          "  b.PMCODE_hung pmcode, b.ASSCODE1_hung seccode, b.ASSCODE2_hung thrcode, a.psstatus_hung psstatus "\
          "  from  expvstoll_hung a, expense_hung b"\
          "  where 1=1 and a.flag='Y' and b.flag='Y' " \
          "  and a.company=b.company and a.uuid=b.hunguuid "\
          "  and b.company=%s and b.storecode=%s "\
          "  and b.uuid=%s "

    print(sql)
    params = (company+' '+ storecode +' ' + uuid).split()
    print(params)

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

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

    print('ttype,flag',ttype, flag,hungitem.srvcode_hung)
    if ttype=='C' and  flag=='N':
        print('in ')
        cardinfo=Cardinfo.objects.get(company=company,ccode=hungitem.srvcode_hung)
        print('between')
        cardinfo.status='C'
        print('out')
        cardinfo.save()

    hungitems = ExpenseHung.objects.filter(company=company,hunguuid=hunguuid,flag='Y')
    if len(hungitems)==0:
        trans=ExpvstollHung.objects.get(company=company,uuid=hunguuid)
        # trans.flag='N'
        trans.valiflag_hung='N'
        trans.save()


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
            vip = Vip.objects.get(comany=company,uuid=vipuuid)
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
