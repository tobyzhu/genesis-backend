from django.shortcuts import render
import sys
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from xlwt import *
from rest_framework import serializers,viewsets,pagination
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from django.db import models
import uuid
import django.utils.timezone as timezone
import time,datetime
from django.db.models import Q
import traceback

# from .serializers import UserSerializer, GroupSerializer
from .serializers import CrmCaseSerializer,CrmCaseDetailSerializer,VipCaseDetailSerializer
from baseinfo.serializers import VipSerializer
from .models import Empl,CrmCase,CrmCaseDetail,Vip,VipCaseDetail,CrmSubReport,CrmInfoItem,CrmInfoItemChoice
from adviser.views import sql_to_json

# Create your views here.

# @login_required()
# Create your models here.
from cashier.models import Expvstoll, Expense
from adviser.models import Cardinfo
from baseinfo.models import Cardtype
from baseinfo.models import Goods,Empl,Serviece,Vip
import common.constants
import crm.crmsql

class VipCaseDetailViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = VipCaseDetail.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('create_time')
    serializer_class = VipCaseDetailSerializer

class CrmCaseViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset =  CrmCase.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('planbegindate')
    serializer_class = CrmCaseSerializer


class CrmCaseDetailViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = CrmCaseDetail.objects.filter(company=common.constants.COMPANYID)
    serializer_class = CrmCaseDetailSerializer

@csrf_exempt
def AddCrmCaseDetail(request):
    if request.method=='POST':
        req = json.loads(request.body.decode())
        company = req.get('company')
        storecode = req.get('storecode')
        crmcaseid= req.get('caseid')
        detaildescription = req.get('detaildescription')
        ecode = req.get('ecode')
    if company == None:
        company = common.constants.COMPANYID
    if storecode == None:
        storecode = '000'

    try:
        crmcase = CrmCase.objects.get(uuid=crmcaseid)
    except:
        return HttpResponse('No this crm case!')
    print('request info ',company,storecode, crmcaseid,detaildescription,ecode)
    crmcasedetail = CrmCaseDetail.objects.create(company=company,storecode=storecode,caseid=crmcase,detaildescription=detaildescription)
    return HttpResponse('OK!')

@csrf_exempt
def UpdateCrmCaseDetail(request):
    # print(request)
    if request.method=='PUT':
        req = json.loads(request.body.decode())
        print(req)

        company = req.get('company')
        storecode = req.get('storecode')
        crmcasedetailuuid= req.get('crmcasedetailuuid')
        detaildescription = req.get('detaildescription')
        ecode = req.get('ecode')

    if company == None:
        company = common.constants.COMPANYID

    if storecode == None:
        storecode = '000'
        # return  HttpResponse('The storecode is need!')

    try:
        crmcasedetail = CrmCaseDetail.objects.get(uuid=crmcasedetailuuid)
        crmcasedetail.detaildescription = detaildescription
        crmcasedetail.save()
        return HttpResponse('OK!')
    except:
        return HttpResponse('No this crm case detail!')

    return HttpResponse('OK!')

class VipViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = VipSerializer

    def get_queryset(self):
        company = self.request.GET.get('company') or self.request.META.get('HTTP_X_COMPANY', '')
        storecode = self.request.GET.get('storecode') or self.request.META.get('HTTP_X_STORECODE', '')
        qs = Vip.objects.filter(flag='Y')
        if company:
            qs = qs.filter(company=company)
        if storecode:
            qs = qs.filter(storecode=storecode)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(vname__icontains=search) | Q(mtcode__icontains=search) | Q(vcode__icontains=search)
            )
        viplevel = self.request.GET.get('viplevel', '').strip()
        if viplevel:
            qs = qs.filter(viplevel=viplevel)
        viptype = self.request.GET.get('viptype', '').strip()
        if viptype:
            qs = qs.filter(viptype=viptype)
        sex = self.request.GET.get('sex', '').strip()
        if sex:
            qs = qs.filter(sex=sex)
        birth_gte = self.request.GET.get('birth__gte', '').strip()
        birth_lte = self.request.GET.get('birth__lte', '').strip()
        if birth_gte and birth_lte:
            qs = qs.filter(birth__gte=birth_gte, birth__lte=birth_lte)
        indate_gte = self.request.GET.get('indate__gte', '').strip()
        indate_lte = self.request.GET.get('indate__lte', '').strip()
        if indate_gte and indate_lte:
            qs = qs.filter(indate__gte=indate_gte, indate__lte=indate_lte)
        has_phone = self.request.GET.get('has_phone', '').strip().upper()
        if has_phone == 'Y':
            qs = qs.exclude(mtcode__exact='')
        elif has_phone == 'N':
            qs = qs.filter(mtcode__exact='')
        wechat = self.request.GET.get('wechat', '').strip()
        if wechat:
            qs = qs.filter(wechat__icontains=wechat)
        return qs.order_by('-indate', 'vcode')

def generatecrmcase(request):
    ps_date = request.GET['ps_date']
    srvintervaldays=7
    goodsintervaldays=30

    vipttypes =  Expvstoll.objects.filter(Q(vsdate=ps_date),Q(ttype='S')|Q(ttype='G')).values('company','storecode','vsdate','vipuuid','ttype').distinct()
    for item in range(len(vipttypes)):
        print(item)

        company = vipttypes[item]['company']
        storecode = vipttypes[item]['storecode']
        vsdate = datetime.datetime.strptime( vipttypes[item]['vsdate'],'%Y%m%d')
        vipuuid = vipttypes[item]['vipuuid']
        vip = Vip.objects.get(uuid=vipuuid)
        viptype = vip.viptype

        if vipttypes[item]['ttype']=='S':
            casetype='40'
            planbegindate = vsdate + datetime.timedelta(days=+srvintervaldays)
            casedesc = vip.vname +'服务回访'
        elif vipttypes[item]['ttype']=='G':
            casetype='45'
            planbegindate = vsdate + datetime.timedelta(days=+goodsintervaldays)
            casedesc = vip.vname +'购买商品回访'
        else:
            casetype='48'


        ecode = vip.ecode
        ecode2 = vip.ecode2
        print('vip=',vip.vname, vip.vcode,'ecode=',ecode, 'ecode2=',ecode2)
        if ecode == None:
            print(vip.vname, "do not set ecode")
        else:
            # try:
                print('company=',company,'storecode=',storecode,'casetype=',casetype,'vsdate=',vsdate,'ecode=',ecode)
                empl = Empl.objects.get(flag='Y',company=company,ecode=ecode)
                print('company=',company,'storecode=',storecode,'casetype=',casetype,'vsdate=',vsdate,'empl=',empl)
                crmcase = CrmCase.objects.get_or_create(company=company,storecode=storecode,casetype=casetype,vipuuid=vip,vsdate=vsdate,empl=empl)[0]
                print('crmcase',crmcase.ecode)
                crmcase.status ='10'
                crmcase.planbegindate = planbegindate
                crmcase.casedesc = casedesc
                crmcase.ecode=empl.ecode
                crmcase.save()
                print(viptype,vip.uuid, vip.vname,vsdate,casetype, empl.ename,'is created ')
            # except:
            #     # crmcase = CrmCase.objects.create(casetype=casetype,vipuuid=vipuuid,vsdate=vsdate,ecode=empl)
            #     # crmcase.
            #     print(viptype, vip.uuid,vip.vname, vsdate, casetype, 'already exists!')
            #     print("skip")


        if ecode2 == None:
            print("skipped")
            print(vip.vname, "do not set ecode2")
        else:
            try:
                empl2 = Empl.objects.get(company=company,storecode=storecode,ecode=ecode)
                crmcase = CrmCase.objects.get_or_create(company=company,storecode=storecode,casetype=casetype,vipuuid=vip,vsdate=vsdate,ecode=empl2)
                crmcase.status ='10'
                crmcase.planbegindate = planbegindate
                crmcase.casedesc = casedesc
                crmcase.save()
                print(viptype, vip.uuid,vip.vname, vsdate, casetype, empl2.ename,'is created ')
            except:
                # crmcase = CrmCase.objects.create(casetype=casetype,vipuuid=vipuuid,vsdate=vsdate,ecode=empl)
                # crmcase.
                print(viptype,vip.uuid, vip.vname, vsdate, casetype, 'already exists!')
                print("skip")


    return HttpResponse(0)


def update_crmcase(request):
    company=request.GET.get('company')
    storecode=request.GET.get('storecode')
    crmcaseuuid_s = request.GET.get('crmcaseuuid').replace('-','')
    crmcaseuuid = uuid.UUID(crmcaseuuid_s)
    try:
        crmcase_status = request.GET.get('status')
    except:
        crmcase_status =''
    print('tt',crmcaseuuid_s,crmcaseuuid,crmcase_status)

    try:
        crmcase = CrmCase.objects.get(company=company,uuid=crmcaseuuid)
        print('crmcase',crmcase.casedesc)
        # crmcase_status = crmcase.status
    except:
        print('error')
        # crmcase  = CrmCase.objects.create(uuid=crmcase_uuid)
        return HttpResponse('500', content_type="application/json")
    if crmcase_status =='' :
        crmcase_status = crmcase.status
    crmcase.status = crmcase_status
    crmcase.save()
    return HttpResponse('200', content_type="application/json")


def get_vipcasedetail_byvipuuid(request):
    company = request.GET.get('company','demo')
    print('company=',company)
    vipuuid = request.GET.get('vipuuid','').replace('-','')
    print('vipuuid=',vipuuid)

    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,status"\
          "  from vipcasedetail a"\
          "  where 1=1 and a.flag='Y' "\
          "  and a.company = %s AND a.vipuuid = %s " \
          "  order by a.create_time desc  "\

    params =  (company+' '+ vipuuid  ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_planvipcasedetail_byecode(request):
    company = request.GET.get('company','demo')
    print('company=',company)
    try:
        vipuuid = request.GET.get('vipuuid','').replace('-','')
        print('vipuuid=',vipuuid)
    except:
        vipuuid=''

    try:
        nextecode=request.GET.get('ecode','')
    except:
        nextecode=''

    nextdate_s = request.GET.get('nextdate','')
    print('nextdate_s',nextdate_s)
    nextdate = datetime.datetime.strptime(nextdate_s,'%Y-%m-%d')
    print('nextdate',nextdate)

    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,a.status," \
          "  a.vipuuid, b.vcode,b.vname, b.mtcode "\
          "  from vipcasedetail a, vip b"\
          "  where 1=1 and a.flag='Y' and b.flag='Y' " \
          "  and a.company=b.company and a.vipuuid = b.uuid"\
          "  and a.company = %s AND a.nextecode = %s  and nextdate=date(%s)" \
          "  order by a.create_time desc  "\

    params =  (company+' '+ nextecode +' '+ nextdate_s ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def get_vipcasedetail(request):
    uuid = request.GET.get('uuid')
    sql = "  select a.uuid , a.casetype , a.detail, a.ecode ,DATE(a.create_time) created_date, TIME (a.create_time) created_time,nextdate,nextecode,status"\
          "  from vipcasedetail a"\
          "  where 1=1 and a.flag='Y' "\
          "  and a.uuid = %s  " \
          "  order by a.create_time desc  "\

    params =  (uuid  ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

def update_vipcasedetail(request):
    uuid = request.GET.get('uuid').replace('-','')
    company=request.GET.get('company')
    storecode=request.GET.get('storecode')
    ecode =request.GET.get('ecode')
    casetype = request.GET.get('casetype')
    detail = request.GET.get('detail')
    vipuuid = request.GET.get('vipuuid').replace('-','')
    try:
        nextdate = request.GET.get('nextdate')
    except:
        nextdate= None

    try:
        nextecode=request.GET.get('nextecode')
    except:
        nextecode=''


    if len(uuid)==32:
        vipcasedetail = VipCaseDetail.objects.get(uuid=uuid)
        vipcasedetail.ecode=ecode
        vipcasedetail.casetype=casetype
        vipcasedetail.detail=detail
        vipcasedetail.last_modified=datetime.datetime.now()
        vipcasedetail.creater=ecode
        vipcasedetail.nextdate=nextdate
        vipcasedetail.nextecode=nextecode
        vipcasedetail.status='20'

        vipcasedetail.save()
        return HttpResponse('200', content_type="application/json")
    else:
        try:
            vip = Vip.objects.get(company=company,uuid=vipuuid)
            vipcasedetail = VipCaseDetail.objects.create(company=company,storecode=storecode,creater=ecode,ecode=ecode,flag='Y',vipuuid=vip,detail=detail,
                                                         nextdate=nextdate,nextecode=nextecode,status='20')
            return HttpResponse('200', content_type="application/json")
        except:
            # raise ValueError;
            return HttpResponse('500', content_type="application/json")

def get_crmcaselist(request):
    bytype = request.GET['bytype']
    company = request.GET['company']
    storecode = request.GET['storecode']
    status = request.GET['status']

    if bytype =='vipcrmcase':
        vipuuid = request.GET['vipuuid']
        if company in common.constants.COMPANYLIST_WITHOUT_MTCODE:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, '' mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename, a.status status, finishedate, planbegindate, planfinishdate,casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s  and a.status=%s and a.vipuuid=%s" \
                  " order by casetype, planfinishdate"

        else:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, c.mtcode mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename, a.status status, finishedate, planbegindate, planfinishdate,casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s  and a.status=%s and a.vipuuid=%s" \
                  " order by casetype, planfinishdate"

        params =  (company+' '+ storecode + ' ' + status+ ' '+ vipuuid).split()
        print(sql,params)
        json_data = sql_to_json(sql,params)
        print(json_data)
        return HttpResponse(json_data, content_type="application/json")

    if bytype =='crmcase':
        ecode = request.GET['ecode']
        planbegindate = request.GET['planbegindate']
        if company in common.constants.COMPANYLIST_WITHOUT_MTCODE:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, '' mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename," \
                  " a.status status, finishedate, planbegindate,planfinishdate, casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s and a.ecodelist like  concat('%%',%s,'%%') and a.planbegindate <= %s and a.planfinishdate >= %s and a.status=%s" \
                  " order by casetype, planfinishdate"
        else:
            sql = " select a.uuid uuid, casetype, c.viptype viptye, vipuuid,c.vcode  vcode,c.vname vname, c.mtcode mtcode,c.birth,c.indate," \
                  " b.ecode ecode, b.ename ename," \
                  " a.status status, finishedate, planbegindate,planfinishdate, casedesc, vsdate" \
                  " from crmcase a, empl b, vip c" \
                  " where a.company = b.company  and a.ecode = b.ecode " \
                  " and a.vipuuid = c.uuid and a.company =%s and a.storecode =%s and a.ecodelist like  concat('%%',%s,'%%') and a.planbegindate <= %s and a.planfinishdate >= %s and a.status=%s" \
                  " order by casetype, planfinishdate"
        params =  (company+' '+ storecode +' ' + ecode +'  ' + planbegindate +' ' + planbegindate + ' '+ status).split()
        print(sql,params)
        json_data = sql_to_json(sql,params)
        # print(json_data)
        return HttpResponse(json_data, content_type="application/json")

def get_vipconsumelist(request):
    company = request.GET.get('company', common.constants.COMPANYID)
    vipuuid_raw = (request.GET.get('vipuuid') or '').strip()
    keyword = (request.GET.get('keyword') or '').strip().lower()
    fromdate = (request.GET.get('fromdate') or '20180101').replace('-', '')
    todate = (request.GET.get('todate') or '20991231').replace('-', '')
    debug_ctx = {
        'company': company,
        'vipuuid_raw': vipuuid_raw,
        'fromdate': fromdate,
        'todate': todate,
        'keyword': keyword,
    }
    print('[get_vipconsumelist] request:', debug_ctx)

    try:
        if len(vipuuid_raw) == 32 and '-' not in vipuuid_raw:
            vipuuid = uuid.UUID(hex=vipuuid_raw)
        else:
            vipuuid = uuid.UUID(vipuuid_raw)

        ttype_map = {'S': '服务', 'G': '商品', 'C': '售卡', 'I': '充值'}
        stype_map = {'N': '正常', 'P': '赠送'}

        trans_qs = list(
            Expvstoll.objects.filter(
                company=company,
                valiflag='Y',
                vipuuid=vipuuid,
                vsdate__gte=fromdate,
                vsdate__lte=todate,
            )
            .select_related('vipuuid')
            .order_by('-vsdate', '-create_time')[:1000]
        )
        if not trans_qs:
            return HttpResponse('[]', content_type="application/json")

        trans_ids = [t.uuid for t in trans_qs]
        trans_map = {t.uuid: t for t in trans_qs}
        exp_qs = list(
            Expense.objects.filter(company=company, transuuid__in=trans_ids, flag='Y')
            .order_by('-create_time')[:3000]
        )

        need_srv = set()
        need_goods = set()
        need_cards = set()
        empl_codes = set()
        need_trans_cards = set()
        for e in exp_qs:
            if e.ttype == 'S' and e.srvcode:
                need_srv.add(e.srvcode)
            elif e.ttype == 'G' and e.srvcode:
                need_goods.add(e.srvcode)
            elif e.ttype in ('C', 'I') and e.srvcode:
                need_cards.add(e.srvcode)
            if e.pmcode:
                empl_codes.add(e.pmcode)
            if e.asscode1:
                empl_codes.add(e.asscode1)
            if e.asscode2:
                empl_codes.add(e.asscode2)
        for t in trans_qs:
            if t.ccode:
                need_trans_cards.add(t.ccode)

        srv_map = dict(Serviece.objects.filter(company=company, svrcdoe__in=list(need_srv)).values_list('svrcdoe', 'svrname'))
        goods_map = dict(Goods.objects.filter(company=company, gcode__in=list(need_goods)).values_list('gcode', 'gname'))
        sold_card_map = dict(Cardinfo.objects.filter(company=company, ccode__in=list(need_cards)).values_list('ccode', 'cardtype'))
        trans_card_map = dict(Cardinfo.objects.filter(company=company, ccode__in=list(need_trans_cards)).values_list('ccode', 'cardtype'))
        # 获取卡类名称映射
        all_cardtypes = set()
        for v in sold_card_map.values():
            if v:
                all_cardtypes.add(v)
        for v in trans_card_map.values():
            if v:
                all_cardtypes.add(v)
        ct_name_map = {}
        if all_cardtypes:
            ct_name_map = dict(
                Cardtype.objects.filter(company=company, cardtype__in=list(all_cardtypes))
                .values_list('cardtype', 'cardname')
            )
        empl_map = dict(Empl.objects.filter(company=company, ecode__in=list(empl_codes)).values_list('ecode', 'ename'))

        rows = []
        for e in exp_qs:
            t = trans_map.get(e.transuuid_id)
            if not t:
                continue
            itemname = e.srvcode or ''
            if e.ttype == 'S':
                itemname = srv_map.get(e.srvcode, e.srvcode or '')
                if e.srvcode:
                    itemname = itemname + ' (' + e.srvcode + ')' 
            elif e.ttype == 'G':
                itemname = goods_map.get(e.srvcode, e.srvcode or '')
                if e.srvcode:
                    itemname = itemname + ' (' + e.srvcode + ')' 
            elif e.ttype in ('C', 'I'):
                itemname = sold_card_map.get(e.srvcode, e.srvcode or '')
                # itemname = cardtype_code, 转换为卡名称+卡号
                cardtype_code = itemname
                card_name = ct_name_map.get(cardtype_code, cardtype_code)
                itemname = card_name + '(' + (e.srvcode or '') + ')' 

            if keyword and keyword not in str(itemname or '').lower():
                continue

            cardname = '未设定'
            if t.ccode:
                cardname = trans_card_map.get(t.ccode, t.ccode) or '未设定'
            exptxpaydesc = '余额:' + str(t.cardleftmoney if t.cardleftmoney is not None else 0)
            # exptxserno 取最后的数字部分
            # exptxserno 取最后一个_ 后的部分
            exptxserno_raw = t.exptxserno or ''
            exptxserno_num = exptxserno_raw.rsplit('_', 1)[-1] if '_' in exptxserno_raw else exptxserno_raw
            rows.append({
                'transuuid': str(t.uuid),
                'ccode': t.ccode or '',
                'cardname': cardname,
                'storecode': t.storecode or '',
                'exptxserno': exptxserno_num,
                'vsdate': t.vsdate or '',
                'itemname': itemname,
                's_qty': e.s_qty,
                's_price': e.s_price,
                'secdisc': e.secdisc,
                'amount': e.s_mount,
                'pmcode': e.pmcode or '',
                'seccode': e.asscode1 or '',
                'thrcode': e.asscode2 or '',
                'pmname': empl_map.get(e.pmcode, e.pmcode or ''),
                'secname': empl_map.get(e.asscode1, e.asscode1 or ''),
                'thrname': empl_map.get(e.asscode2, e.asscode2 or ''),
                'ttype': ttype_map.get((e.ttype or '').strip(), '其他'),
                'stype': stype_map.get((e.stype or '').strip(), '其他'),
                'exptxpaydesc': exptxpaydesc,
            })
            if len(rows) >= 500:
                break
        print('[get_vipconsumelist] ok rows=', len(rows))
        return HttpResponse(json.dumps(rows, cls=DjangoJSONEncoder), content_type="application/json")
    except Exception as e:
        print('[get_vipconsumelist] ERROR:', e)
        print(traceback.format_exc())
        return HttpResponse(
            json.dumps({
                'ok': False,
                'message': 'get_vipconsumelist error',
                'detail': str(e),
                'trace_last': traceback.format_exc().splitlines()[-1] if traceback.format_exc() else '',
                'request': debug_ctx,
            }, cls=DjangoJSONEncoder),
            status=500,
            content_type="application/json"
        )



def get_vip_crmcasedetail(request):
    company = request.GET['company']
    vipuuid = request.GET['vipuuid']
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']

    sql = " SELECT b.uuid crmcasedetailuuid, c.vcode, c.vname, b.storecode storeocode, casetype, a.status casestatus, planbegindate,planfinishdate, finishedate, casedesc, b.create_time,b.creater, detaildescription "\
            " FROM crmcase a, crmcasedetail b, vip c, empl d "\
            " where a.uuid = b.caseid_id and a.vipuuid = c.uuid and a.ecode = d.ecode "\
            " and a.company=d.company and a.company = %s and a.vipuuid = %s "\
            " order by b.create_time"

    params =  (company+' '+ vipuuid  ).split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")


@api_view(['GET'])
def get_vip_filter_options(request):
    """\u8fd4\u56de\u4f1a\u5458\u7b5b\u9009\u9009\u9879\uff08\u7b49\u7ea7\u3001\u7c7b\u578b\uff09"""
    company = request.GET.get('company', '')
    levels = list(
        Vip.objects.filter(company=company, flag='Y')
        .exclude(viplevel__exact='')
        .values_list('viplevel', flat=True)
        .distinct().order_by('viplevel')
    )
    return Response({'viplevels': levels})

def get_crmcasedetail_bycaseid(request):
    company = request.GET['company']
    uuid = request.GET['uuid']
    # fromdate = request.GET['fromdate']
    # todate = request.GET['todate']

    sql = "   SELECT a.uuid crmcaseuuid, a.vipuuid vipuuid, a.casedesc, b.uuid uuid,  b.create_time,b.creater, detaildescription ,c.vname vname"\
            " FROM crmcase a, crmcasedetail b, vip c"\
            " where 1=1 and a.uuid = b.caseid_id AND a.vipuuid = c.uuid"\
            " and a.company = %s and b.uuid = %s "\
            " order by b.create_time"

    params =  (company+' '+ uuid  ).split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")


@api_view(['GET'])
def get_vip_filter_options(request):
    """\u8fd4\u56de\u4f1a\u5458\u7b5b\u9009\u9009\u9879\uff08\u7b49\u7ea7\u3001\u7c7b\u578b\uff09"""
    company = request.GET.get('company', '')
    levels = list(
        Vip.objects.filter(company=company, flag='Y')
        .exclude(viplevel__exact='')
        .values_list('viplevel', flat=True)
        .distinct().order_by('viplevel')
    )
    return Response({'viplevels': levels})

def get_viplist_bycrmrptid(request):
    # datedelta = datetime.datedelta(days=-7)
    delta = datetime.timedelta(days=-90)
    now = datetime.datetime.now()
    defaultfromdate = datetime.datetime.strftime((now + delta),'%Y%m%d')
    defaulttodate = datetime.datetime.strftime( now  ,'%Y%m%d')

    try:
        company=request.GET['company']
    except:
        company=''

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        fromdate=request.GET['fromdate'].replace('-','')
        if len(fromdate)==0:
            fromdate=defaultfromdate

    except:
        fromdate=defaultfromdate

    try:
        todate = request.GET['todate'],replace('-','')
        if len(todate)==0:
            todate=defaulttodate
    except:
        todate =defaulttodate

    try:
        minileftmoney = request.GET['minileftmoney']
    except:
        minileftmoney= 0

    try:
        maxleftmoney = request.GET['maxleftmoney']
    except:
        maxleftmoney= 5000

    try:
        ecode = request.GET['ecode']
    except:
        ecode=''

    try:
        crmrptid = request.GET['crmrptid']
    except:
        crmrptid ='1'
    print('crmrptid=',crmrptid)

    if crmrptid == '1'  :
        sql = crm.crmsql.CRM_SQL101
        print('sql=',sql)
        params = (company+'  '+ storecode +'  '+ fromdate +'  '+ todate+' '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)

        return HttpResponse(json_data, content_type="application/json")

    if crmrptid =='2':
        sql = crm.crmsql.CRM_SQL102
        params = (company+'  '+ storecode +'  '+ fromdate +'  '+ todate+' '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '3':
        sql = crm.crmsql.CRM_SQL103
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '4':
        sql = crm.crmsql.CRM_SQL104
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人卡余额查询
    if crmrptid == '5':
        sql = crm.crmsql.CRM_SQL105
        params = (company + '  ' + storecode + ' '+ str(minileftmoney)  + ' '+ str(maxleftmoney) + '  '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    if crmrptid == '6':
        sql = crm.crmsql.CRM_SQL105
        params = (company + '  ' + storecode + ' '+ str(minileftmoney)  + ' '+ str(maxleftmoney) + '  '+ ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人生日
    if crmrptid == '8':
        fromdate=str(fromdate).replace('-','')
        todate = str(todate).replace('-','')
        sql = crm.crmsql.CRM_SQL108
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

    # 客人生日
    if crmrptid == '9':
        fromdate=str(fromdate).replace('-','')
        todate = str(todate).replace('-','')
        sql = crm.crmsql.CRM_SQL109
        params = (company + '  ' + storecode + '  ' + fromdate + '  ' + todate + ' ' + ecode).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

def get_crmsubreport(request):
    company = request.GET['company']
    crmsubreport = CrmSubReport.objects.filter(company=company,flag='Y').values_list('id','crmsubreportName')
    sql = "  select id, crmsubreportname from crmsubreport " \
          "  where flag='Y' and company = %s "

    params =  (company+' ').split()
    print('sql:',sql,'params:',params)
    json_data = sql_to_json(sql,params)
    print('json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")


@api_view(['GET'])
def get_vip_filter_options(request):
    """\u8fd4\u56de\u4f1a\u5458\u7b5b\u9009\u9009\u9879\uff08\u7b49\u7ea7\u3001\u7c7b\u578b\uff09"""
    company = request.GET.get('company', '')
    levels = list(
        Vip.objects.filter(company=company, flag='Y')
        .exclude(viplevel__exact='')
        .values_list('viplevel', flat=True)
        .distinct().order_by('viplevel')
    )
    return Response({'viplevels': levels})