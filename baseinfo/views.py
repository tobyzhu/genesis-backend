#coding = utf-8

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from pypinyin import pinyin
from pytz import unicode
import json
from rest_framework import  pagination,viewsets,generics
from django_filters.rest_framework import DjangoFilterBackend
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import uuid
from uuid import UUID
import datetime
# Create your views here.

from django.contrib.auth.models import User,Group
from .tools import set_vip_pinyin,set_mnemoniccode,main

# from rest_framework import ,pagination
from .serializers import UserSerializer, GroupSerializer
from .serializers import EmplSerializer, PositionSerializer,VipSerializer,VipbyEcodeSerializer,SrvtoptySerializer,ServieceSerializer,GoodsSerializer
from .serializers import CardvsdiSerializer,CardtypeSerializer
from .models import Appoption,Empl,Position,Vip,Serviece,Servieceprice,Srvtopty,Goods,Goodsct,Cardvsdi,Cardtype,Promotions,Hdsysuser,Useright
# import baseinfo.models
import common.constants
from adviser.views import sql_to_json

JSONEncoder_old_default = json.JSONEncoder.default
def JSONEncoder_new_default(self, o):
    if isinstance(o, UUID.UUID):
        return str(o)
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
        dt_str = o.isoformat()
        # truncate yyyy-MM-ddTHH:mm:ss.SSSSSSZ
        # --> yyyy-MM-ddTHH:mm:ss.SSSZ
        return dt_str[:23] + dt_str[26:]
    return JSONEncoder_old_default(self, o)
json.JSONEncoder.default = JSONEncoder_new_default

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CardtypeViewSet(viewsets.ModelViewSet):
    lookup_field = 'cardtype'
    queryset = Cardtype.objects.filter(company=common.constants.COMPANYID,saleflag='Y',flag='Y',valiflag='Y').order_by('cardtype')
    serializer_class = CardtypeSerializer

class CardvsdiViewSet(viewsets.ModelViewSet):
    # lookup_field = 'uuid'
    queryset = Cardvsdi.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('cardtype')
    serializer_class = CardvsdiSerializer

class SrvtoptyViewSet(viewsets.ModelViewSet):
    # lookup_field = 'uuid'
    queryset = Srvtopty.objects.all().order_by('topcode')
    serializer_class = SrvtoptySerializer

class SerieceViewSet(viewsets.ModelViewSet):
    # lookup_field = 'uuid'
    queryset = Serviece.objects.filter(company=common.constants.COMPANYID,saleflag='Y',flag='Y',valiflag='Y').order_by('svrcdoe')
    serializer_class = ServieceSerializer

# class ServiecepriceViewSet(viewsets.ModelViewSet):
#     queryset = Servieceprice.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('srvcode')
#     serializers_class = ServiecepriceSerializer

class GoodsViewSet(viewsets.ModelViewSet):
    # lookup_field = 'uuid'
    queryset = Goods.objects.filter(company=common.constants.COMPANYID,saleflag='Y',flag='Y',valiflag='Y').order_by('gcode')
    serializer_class = GoodsSerializer


class EmplViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Empl.objects.filter(company=common.constants.COMPANYID,flag='Y').order_by('ecode')
    serializer_class = EmplSerializer


class PositionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Position.objects.all().order_by('positioncode')
    serializer_class = PositionSerializer
    lookup_field = 'uuid'

class VipViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    # queryset = Vip.objects.filter(company=common.constants.COMPANYID).order_by('vname')
    queryset = Vip.objects.all().order_by('vname')
    serializer_class = VipSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('company', 'ecode')


# @csrf_exempt
def Vip_list(request):
    company = request.GET['company']
    ecode= request.GET['ecode']
    # url= request.GET['url']
    if request.method == 'GET':
        # vips = Vip.objects.filter(company=company,storecode='2',vname__isnull=0).filter(ecode='01').filter(flag='Y').values('uuid','vcode','vname','mtcode')
        # print(vips)
        queryset = Vip.objects.all()
        serializer = VipSerializer(queryset, many=True)

        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('company', 'ecode')

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)
        serializer = VipSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def Vip_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        vip = Vip.objects.get(pk=pk)
    except Vip.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = VipSerializer(vip)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = VipSerializer(vip, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        vip.delete()
        return HttpResponse(status=204)

@csrf_exempt
def create_Vip(request):
    print(request)
    try:
        company=request.GET['company']
    except:
        company=common.constants.DEMO_COMPANY

    try:
        storecode=request.GET['storecode']
    except:
        storecode=common.constants.DEMO_SOTRECODE

    try:
        ecode = request.GET['ecode']
    except:
        ecode=common.constants.DEMO_ECODE

    try:
        creater=request.GET['creater']
    except:
        creater=ecode

    try:
        viptype = request.GET['viptype']
    except:
        viptype='30'

    try:
        vname = request.GET['vname']
    except:
        vname=''

    try:
        vippinno = request.GET['vippinno']
    except:
        vippinno = common.constants.DEFAULT_VIP_PINNO

    try:
        mtcode = request.GET['mtcode']
    except:
        mtcode=''

    try:
        birthday = request.GET['birthday']
    except:
        birthday=''

    try:
        pmcode = request.GET['ecode']
    except:
        pmcode=''

    try:
        seccode = request.GET['ecode2']
    except:
        seccode=''

    try:
        source = request.GET['source']
    except:
        source = ''

    try:
        occupation = request.GET['occupation']
    except:
        occupation = ''

    try:
        occupation = request.GET['occupation']
    except:
        occupation = ''

    try:
        vdesc = request.GET['vdesc']
    except:
        vdesc = ''

    try:
        viplevel = request.GET['viplevel']
    except:
        viplevel = ''

    if viptype=='10':
        vcode=get_nextvcode(company,storecode)
    else:
        vcode=''

    # vipuuid = uuid()
    # print(vipuuid,vname)
    vip = Vip.objects.create(company=company,storecode=storecode,vcode=vcode,vname=vname,viptype=viptype,viplevel=viplevel,mtcode=mtcode,ecode=pmcode,ecode2=seccode,
                                    source=source,occupation=occupation,vdesc=vdesc,vippinno='000000',valiflag='Y')
    print('created vip',vip,vip.vname,vip.uuid)
    vipuuid=str(vip.uuid)
    print(vipuuid)
    sql = " select uuid,company,storecode, vcode,vname,viptype, viplevel, mtcode,ecode,ecode2,pinyin,source,occupation,vdesc" \
          " from vip " \
          " where company=%s and storecode=%s and uuid= replace(%s,'-','') "
    params = (company + ' ' + storecode + ' ' + vipuuid ).split()
    print(sql, params)
    json_data = sql_to_json(sql, params)

    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def update_Vip(request):
    print(request)
    try:
        company=request.GET['company']
    except:
        company=common.constants.DEMO_COMPANY

    try:
        vipuuid=request.GET['uuid']
    except:
        vipuuid=uuid.uuid4()

    try:
        vip = Vip.objects.get(uuid=vipuuid)
        print('get vip',vip.vcode,vip.vname)
    except:
        print('not get vip')
        return HttpResponse('501', content_type="application/json")

    try:
        storecode=request.GET['storecode']
        vip.storecode=storecode
    except:
        storecode=vip.storecode

    try:
        ecode = request.GET['ecode']
        vip.ecode=ecode
    except:
        ecode=vip.ecode

    try:
        creater=request.GET['creater']
    except:
        creater=vip.creater

    try:
        vname = request.GET['vname']
        vip.vname=vname
    except:
        vname=vip.vname

    try:
        vippinno = request.GET['vippinno']
        vip.vippinno=vippinno
    except:
        vippinno = vip.vippinno

    try:
        mtcode = request.GET['mtcode']
        vip.mtcode=mtcode
    except:
        mtcode=vip.mtcode

    print('get birthday format',request.GET['birthday'].replace('-',''))

    try:
        birthday = request.GET['birthday'].replace('-','')
        # print('birthday',birthday)
        vip.birth =birthday
    except:
        # print('vip.birth',vip.birth)
        birthday=vip.birth

    try:
        pmcode = request.GET['ecode']
        vip.ecode=pmcode
    except:
        pmcode=''

    try:
        seccode = request.GET['ecode2']
        vip.ecode2=seccode
    except:
        seccode=''

    try:
        source = request.GET['source']
        vip.source=source
    except:
        source = vip.source

    try:
        occupation = request.GET['occupation']
        vip.occupation = occupation
    except:
        occupation = ''

    try:
        vdesc = request.GET['vdesc']
        vip.vdesc = vdesc
    except:
        vdesc = vip.occupation

    try:
        viplevel = request.GET['viplevel']
        vip.viplevel =viplevel
    except:
        viplevel = vip.level

    try:
        viptype = request.GET['viptype']
    except:
        viptype = vip.viptype

    print('vip type:',viptype,vip.viptype)
    if vip.viptype=='10':
        vip.viptype='10'
    elif request.GET['viptype']=='10':
        viptype='10'
        print('before get nextvcode')
        vcode=get_nextvcode2(company,storecode)
        print('vcode',vcode)

        vip.viptype = viptype
        vip.vcode = vcode
    else:
        viptype=request.GET['viptype']
        vip.viptype=viptype

    vip.save()
    print('after update vip',vip.ecode,vip.ecode2)

    return HttpResponse('200', content_type="application/json")


@csrf_exempt
def get_appoption_byseg(request):
    company = request.GET['company']
    seg= request.GET['seg']
    sql = " select itemname , itemvalues " \
          " from  appoption " \
          " where 1=1 " \
          " and company=%s and seg=%s " \
          " and  flag='Y' " \
          " order by itemname"

    params = (company+' '+ seg ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_viplist_byecode(request):
    print(request)
    try:
        company = request.GET['company']
    except:
        company='yfy'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='88'
    try:
        ecode = request.GET['ecode']
    except:
        ecode='888'

    try:
        searchvalue = request.GET['searchvalue']
        searchvalueflag='Y'
    except:
        searchvalue=''
        searchvalueflag='N'
    print(searchvalueflag)

    companylist1 = ['yiren','yfy']
    companylist2 = ['salon','demo']
    # url= request.GET['url']
    if request.method == 'GET':
        if searchvalueflag=='N':
            sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname, mtcode,pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                  " from vip a, empl b" \
                  " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode and ( a.ecode = b.ecode or a.ecode2=b.ecode) and a.pinyin is not null " \
                  " and a.company =%s  and a.storecode =%s " \
                  " order by pinyin "
            params = (company + ' ' + storecode).split()

            if company in companylist1:
                sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname,'' mtcode, pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                      " from vip a, empl b" \
                      " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode and ( a.ecode = b.ecode or a.ecode2=b.ecode) and a.pinyin is not null " \
                      " and a.company =%s  and a.storecode =%s and a.ecode= %s" \
                      " order by pinyin "
                params = (company + ' ' + storecode +  '  '+ecode).split()

            if company in companylist2:
                sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname,mtcode, pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                      " from vip a, empl b" \
                      " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode and ( a.ecode = b.ecode or a.ecode2=b.ecode) and a.pinyin is not null " \
                      " and a.company =%s  and a.storecode =%s " \
                      " order by pinyin "
                params = (company + ' ' + storecode ).split()

            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")

        if searchvalueflag=='Y':

            sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname,mtcode, pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                  " from vip a, empl b" \
                  " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode  and a.pinyin is not null " \
                  " and (a.ecode = b.ecode or a.ecode2 = b.ecode)"\
                  " and a.company =%s  and a.storecode =%s and ( a.vcode like %s or a.vname like %s or a.mtcode like %s or a.pinyin like %s)" \
                  " order by pinyin limit 300"
            print(sql)

            if company in companylist1:
                sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname,'' mtcode, pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                      " from vip a, empl b" \
                      " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode  and a.pinyin is not null " \
                      " and (a.ecode = b.ecode or a.ecode2 = b.ecode)" \
                      " and a.company =%s  and a.storecode =%s and ( a.vcode like %s or a.vname like %s or a.mtcode like %s or a.pinyin like %s)" \
                      " order by pinyin limit 300"
                print(sql)

            if company in companylist2:
                sql = " select distinct a.uuid uuid, a.viptype viptype, vcode ,vname,mtcode, pinyin, b.ecode ecode, b.ename ename, a.viplevel,a.birth" \
                      " from vip a, empl b" \
                      " where a.company = b.company and a.flag='Y' and a.storecode=b.storecode  and a.pinyin is not null " \
                      " and (a.ecode = b.ecode or a.ecode2 = b.ecode)" \
                      " and a.company =%s  and a.storecode =%s and ( a.vcode like %s or a.vname like %s or a.mtcode like %s or a.pinyin like %s)" \
                      " order by pinyin limit 300"
                print(sql)
            params = (company + ' ' + storecode + ' ' + searchvalue + ' %' + searchvalue + '%  %' + searchvalue + '%  %' + searchvalue+'% ' ).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")

def get_vipbaseinfo(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    vipuuid = request.GET['vipuuid']
    if request.method == 'GET':
        sql = ' select storecode, vcode, vname, viptype, viplevel,mtcode,ecode,getbaseinfo(company,storecode,"empl",ecode,"ename") emame, ecode2，getbaseinfo(company,storecode,"empl",ecode2,"ename") emame2 ' \
              ' from vip ' \
              ' where 1=1 and company = %s and storecode=%s and (uuid = %s  or vcode = %s) '
        params = (company + ' ' + storecode + ' ' + vipuuid + ' ' + vipuuid).split()
        print(sql, params)
        json_data = sql_to_json(sql, params)
        return HttpResponse(json_data, content_type="application/json")

# class get_uuid(request):
def get_empl_uuid(ecode):
    empl = Empl.objects.get(company=common.constants.COMPANYID,ecode=ecode)
    return empl.uuid

def get_cardtypelist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    try:
        suptype = request.GET['suptype']
        sql = " select uuid,cardtype,cardname, price,suptype,comptype" \
              " from  cardtype  " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and suptype =%s "
        params = (company+' '+ suptype ).split()
    except:
        params = (company+' '+ '%' ).split()

    try:
        comptype = request.GET['comptype']
        sql = " select uuid,cardtype,cardname, price,suptype,comptype" \
              " from  cardtype  " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and comptype =%s "
        params = (company+' '+ comptype ).split()
    except:
        params = (company+' '+ '% ' ).split()

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_servieceprice(request):
    print('this is debug point ')
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    srvcode = request.GET['srvcode']
    #
    # try:
    #     qty = request.GET['qty']
    #     servieceprice = Servieceprice.objects.filter(company=company, srvcode=srvcode,qty=qty).values('srvcode', 'qty', 'price', 'amount')
    # except:
    #     servieceprice = Servieceprice.objects.filter(company=company,srvcode=srvcode).values('srvcode','qty','price','amount')
    # # print(list(servieceprices))
    # json_data = json.dumps(list(servieceprice),cls=DjangoJSONEncoder)

    sql = " select srvcode,qty, price,amount" \
          " from servieceprice  " \
          " where 1=1 and flag='Y'  " \
          " and company=%s and srvcode =%s "
    params = (company + ' ' + srvcode).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    print(json_data)
    return HttpResponse(json_data, content_type="application/json")


def get_serviece(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    # print(request.getlist())
    try:
        brand = request.GET['brand']
    except:
        brand ='%'

    try:
        displayclass1 = request.GET['displayclass1']
    except:
        displayclass1='%'

    try:
        tags = request.GET['tags']
    except:
        tags='%'
    print(brand,displayclass1,tags)

    try:
        searchvalue=request.GET['searchvalue']
    except:
        searchvalue='%'

    sql = " select a.uuid uuid,a.svrcdoe itemcode, a.svrname itemname, a.price price,a.brand, a.srvrptypecode srvrptypcode, a.displayclass1 displayclass1, a.tags tags,'S' ttype, 'N' stype " \
          " from  serviece a  " \
          " where 1=1  and  a.flag='Y' and a.saleflag='Y' " \
          " and a.company=%s and ( a.svrcdoe like %s or a.svrname like %s or a.brand like %s)"
    params = (company+' %'+ searchvalue +'%   %'+ searchvalue+'%   %'+  searchvalue+'% ' ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    s1 = Serviece.objects.filter(company=company,flag='Y',svrcdoe__contains=searchvalue).values('svrcdoe','svrname','price','brand')
    print(s1)
    return HttpResponse(json_data, content_type="application/json")

def get_goods(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        brand = request.GET['brand']
    except:
        brand ='%'

    try:
        displayclass1 = request.GET['displayclass1']
    except:
        displayclass1='%'

    try:
        tags = request.GET['tags']
    except:
        tags='%'

    try:
        searchvalue=request.GET['searchvalue']
    except:
        searchvalue='%'

    sql = " select a.uuid uuid,a.gcode itemcode, a.gname itemname, a.price price,a.brand, a.srvrptypecode srvrptypcode, a.displayclass1 displayclass1, a.tags tags,'G' ttype, 'N' stype " \
          " from  goods a  " \
          " where 1=1  and  a.flag='Y' and a.saleflag='Y' " \
          " and a.company=%s and ( a.gcode like %s or a.gname like %s or a.brand like %s)"
    params = (company+' %'+ searchvalue +'%   %'+ searchvalue+'%   %'+  searchvalue+'% ' ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)

    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_empllist(request):
    company = request.GET['company']
    storecode= request.GET['storecode']
    sql = " select a.uuid uuid,a.ecode ecode, a.ename ename" \
          " from  empl a, position b " \
          " where 1=1 and a.position = b.positioncode and a.flag='Y' and b.bookingflag='Y' " \
          " and a.company = b.company " \
          " and a.company=%s and a.storecode =%s "
    params = (company+' '+ storecode ).split()
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_pmcodelist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    storecode= request.GET['storecode']
    sql = " select a.uuid uuid,a.ecode ecode, a.ename ename" \
          " from  empl a, position b " \
          " where 1=1 and a.position = b.positioncode and a.flag='Y' " \
          " and a.company = b.company and ( b.positioncode BETWEEN  '200' and '299') " \
          " and a.company=%s and a.storecode =%s "
    params = (company+' '+ storecode ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    print(json_data)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_seccodelist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    storecode= request.GET['storecode']
    sql = " select a.uuid uuid,a.ecode ecode, a.ename ename" \
          " from  empl a, position b " \
          " where 1=1 and a.position = b.positioncode and a.flag='Y' and b.bookingflag='Y' " \
          " and a.company = b.company and ( b.positioncode BETWEEN  '100' and '199') " \
          " and a.company=%s and a.storecode =%s "
    params = (company+' '+ storecode ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_roomlist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    storecode= request.GET['storecode']
    sql = " select uuid,roomid,  roomname" \
          " from  room " \
          " where 1=1 " \
          " and company=%s and storecode =%s " \
          " and  flag='Y'"
    params = (company+' '+ storecode ).split()
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

@csrf_exempt
def get_instrumentlist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    storecode= request.GET['storecode']
    sql = " select instrumentid,  instrumentname" \
          " from  instrument " \
          " where 1=1 " \
          " and company=%s and storecode =%s " \
          " and  flag='Y'"
    params = (company+' '+ storecode ).split()
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_nextvcode1(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    storecode= request.GET['storecode']
    pmcode = request.GET['pmcode']
    prefix = storecode
    codelength=5

    vip = Vip.objects.filter(company=company, vcode__startswith=storecode).order_by('-vcode').first()
    print(vip)
    if len(vip.vcode)>0 :
        print(vip.vcode,'len(storecode)=', len(storecode), 'len(vip.vcode) - len(storecode)=',len(vip.vcode) - len(storecode) )
        nextcode = vip.vcode[len(storecode):len(vip.vcode)]
    else:
        nextcode='00000000'
    print(nextcode)

    nextvcode= storecode + ('00000000'+ str(int(nextcode)+1))[-codelength:]
    print('nextvcode=',nextvcode)
    return HttpResponse(nextvcode, content_type="application/json")

def get_nextvcode(company,storecode):
    # try:
    #     company = request.GET['company']
    # except:
    #     company = common.constants.COMPANYID
    #
    # storecode= request.GET['storecode']
    # pmcode = request.GET['pmcode']
    prefix = storecode
    codelength=5

    vip = Vip.objects.filter(company=company,storecode=storecode, vcode__startswith=storecode).order_by('-vcode').first()
    print(vip)
    if len(vip.vcode)>0 :
        print(vip.vcode,'len(storecode)=', len(storecode), 'len(vip.vcode) - len(storecode)=',len(vip.vcode) - len(storecode) )
        nextcode = vip.vcode[len(storecode):len(vip.vcode)]
    else:
        nextcode='00000000'
    print(nextcode)

    nextvcode= storecode + ('00000000'+ str(int(nextcode)+1))[-codelength:]
    print('nextvcode=',nextvcode)
    return nextvcode

def get_promotionslist(request):
    company = request.GET['company']
    storecode= request.GET['storecode']
    sql = " select promotionsid,  promotionsname" \
          " from  promotions " \
          " where 1=1 " \
          " and company=%s and storecode =%s " \
          " and  flag='Y'" \
          " order by promotionsid desc"


    params = (company+' '+ storecode ).split()
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_brandlist(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    type= request.GET['type']
    if type == 'goods':
        sql = " select distinct brand code, GetAppoptionValue(company,'brand',brand) name " \
              " from  goods " \
              " where 1=1 " \
              " and company=%s and saleflag='Y' and LENGTH(brand)>0 " \
              " and  flag='Y'" \
              " order by brand"
        params = (company+' ' ).split()

    if type == 'serviece':
        sql = " select distinct brand code, GetAppoptionValue(company,'brand',brand) name " \
              " from  serviece " \
              " where 1=1 " \
              " and company=%s and saleflag='Y' and LENGTH(brand)>0" \
              " and  flag='Y' " \
              " order by brand"

        params = (company + ' ').split()
    if type == 'cardtype':
        sql = " select distinct brand code, GetAppoptionValue(company,'brand',brand) name " \
              " from  cardtype " \
              " where 1=1 " \
              " and company=%s and saleflag='Y' and suptype='20' " \
              " and  flag='Y' " \
              " order by brand"

        params = (company + ' ').split()

    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_displayclass_bybrand(request):
    company = request.GET['company']
    # storecode= request.GET['storecode']
    try:
        brand = request.GET['brand']
    except:
        brand='1'

    type= request.GET['type']
    if type =='goods':
        sql = " select distinct displayclass1 code, GetAppoptionValue(company,'displayclass1',displayclass1) name " \
              " from  goods " \
              " where 1=1 and flag='Y' and saleflag='Y' and length(brand)>0 " \
              " and company=%s and brand = %s" \
              " order by displayclass1"
        params = (company+' ' + brand ).split()

    if type =='serviece':
        sql = " select distinct displayclass1 code, GetAppoptionValue(company,'displayclass1',displayclass1) name " \
              " from  serviece " \
              " where 1=1 and flag='Y' and saleflag='Y' and length(brand)>0 and length(displayclass1)>0 " \
              " and company=%s and brand = %s" \
              " order by displayclass1"
        params = (company+' '  + brand  ).split()

    if type =='cardtype':
        sql = " select distinct displayclass1 code, GetAppoptionValue(company,'displayclass1',displayclass1) name " \
              " from  cardtype " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and brand = %s" \
              " order by displayclass1"
        params = (company+' '+ brand).split()

    print(sql,params)
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_itemlist_brandanddisplayclasse(request):
    company = request.GET['company']
    # storecode= request.GET['storecode']
    try:
        brand = request.GET['brand']
    except:
        brand=''

    try:
        displayclass1 = request.GET['displayclass1']
    except:
        displayclass1 =''

    type = request.GET['type']
    if type =='goods':
        sql = " select distinct gcode itemcode, gname itemname,price,uuid " \
              " from  goods " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and brand = %s and displayclass1 = %s" \
              " order by gcode "
        params = (company + ' ' +' '+brand  + ' ' + ' '+ displayclass1 ).split()

    if type =='serviece':
        sql = " select distinct svrcdoe code, svrname name, price  " \
              " from  serviece " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and brand = %s and displayclass1 = %s" \
              " order by svrcdoe "
        params = (company + ' ' +' '+brand  + ' ' + ' '+ displayclass1 ).split()

    if type =='cardtype':
        sql = " select distinct cardtype code, cardname name,price  " \
              " from  cardtype " \
              " where 1=1 and flag='Y' and saleflag='Y' " \
              " and company=%s and brand = %s and displayclass1 = %s" \
              " order by cardtype "
        params = (company + ' ' +' '+brand  + ' ' + ' '+ displayclass1 ).split()

    print(sql,params)
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

def get_itemstructure(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    brands = Appoption.objects.filter(company=company,seg='brand')
    for brand in brands:
        displayclass1 = Serviece.objects.filter(company=company,brand=brand.itemname).values('displayclass1').distinct()
        brand.displayclass = displayclass1
        print(brand.itemname, brand.itemvalues,brand.displayclass)

    print(brands[0].displayclass)
    return HttpResponse('OK', content_type="application/json")

def generate_hdsysuser_by_empl(request):
    company=request.GET['company']

    empls = Empl.objects.filter(flag='Y',company=company,storecode='04',status='Y')
    for empl in empls:
        try:
            hdsysuser = Hdsysuser.objects.get(company=company,storecode=empl.storecode,sys_userid=empl.ecode)
        except:
            hdsysuser = Hdsysuser.objects.create(company=company,storecode=empl.storecode,sys_userid=empl.ecode,sys_passwd='12345',sys_fullname=empl.ename,sys_userstatus=1)
            hdsysuser.save()
    return HttpResponse('OK', content_type="application/json")

@csrf_exempt
def get_goodslist_bykeyword(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID

    try:
        searchvalue = request.GET['searchvalue']
        searchvalueflag='Y'
    except:
        searchvalue=''
        searchvalueflag='N'
    print(searchvalueflag)

    # url= request.GET['url']
    if request.method == 'GET':
        if searchvalueflag=='N':
            sql = " select distinct a.uuid uuid,  a.gcode itemcode ,a.gname itemname, a.price price, a.spec spec, a.brand brand,'G' ttype, 'N' stype " \
                  " from goods a, appoption b" \
                  " where a.company = b.company and a.flag='Y' and a.saleflag='Y' and b.seg='brand'  " \
                  " and ( a.brand = b.itemname )  " \
                  " and a.company =%s  and a.gcode =%s" \
                  " order by pinyin "
            params = (company + ' ' + searchvalue).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")

        if searchvalueflag=='Y':
            sql = " select distinct a.uuid uuid,  a.gcode itemcode ,a.gname itemname, a.price price, a.spec spec, a.brand brand" \
                  " from goods a, appoption b" \
                  " where a.company = b.company and a.flag='Y' and a.saleflag='Y'  and b.seg='brand'  " \
                  " and ( a.brand = b.itemname )  " \
                  " and a.company =%s  and  ( a.gcode like %s or a.gname like %s or a.brand like %s or b.itemvalues LIKE  %s or a.displayclass1 like %s)" \

            print(sql)
            params = (company + ' &' + searchvalue + '% %' + searchvalue + '% %' + searchvalue + '%  %' + searchvalue + '%  %' + searchvalue+'% ' ).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def get_cardtypelist_bykeyword(request):
    try:
        company = request.GET['company']
    except:
        company = common.constants.COMPANYID
    # ecode = request.GET['ecode']t
    try:
        comptype = request.GET['comptype']
    except:
        comptype='times'

    try:
        searchvalue = request.GET['searchvalue']
        searchvalueflag='Y'
    except:
        searchvalue=''
        searchvalueflag='N'
    print(searchvalueflag)

    # url= request.GET['url']
    if request.method == 'GET':
        if searchvalueflag=='N':
            sql = " select distinct a.uuid uuid, a.comptype a.cardtype cardtype ,a.cardname cardname, a.price price,a.brand brand,b.itemvalues brandname,  a.displayclass1 displayclass1, FALSE checked" \
                  " from cardtype a,appoption b" \
                  " where 1=1 and a.flag='Y' and a.saleflag='Y' and b.seg='brand'  and ttype='S' " \
                  " and ( a.brand = b.itemname )  " \
                  " and a.company =%s and a.comptype=%s  and a.cardtype =%s" \
                  " order by  cardtype "
            params = (company + ' '+ comptype + '  ' + searchvalue).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")

        if searchvalueflag=='Y':
            sql = " select distinct a.uuid uuid,a.comptype,  a.cardtype cardtype ,a.cardname cardname, a.price price,a.brand brand,b.itemvalues brandname,  a.displayclass1 displayclass1, FALSE checked" \
                  " from cardtype a,appoption b" \
                  " where a.company = b.company and a.flag='Y' and a.saleflag='Y'  and b.seg='brand'  " \
                  " and ( a.brand = b.itemname )  " \
                  " and a.company =%s  and a.comptype=%s and  ( a.cardtype like %s or a.cardname like %s or a.brand like %s or b.itemvalues LIKE  %s or a.displayclass1 like %s) " \
                  " order by cardtype"

            print(sql)
            params = (company +'  '+comptype +  ' %' + searchvalue + '% %' + searchvalue + '% %' + searchvalue + '%  %' + searchvalue + '%  %' + searchvalue+'% ' ).split()
            print(sql, params)
            json_data = sql_to_json(sql, params)
            return HttpResponse(json_data, content_type="application/json")

def generate_userright_by_position(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    positions = Hdsysuser.objects.filter(company=company,flag='Y',sys_idtype='20')
    print('positions',positions)
    for position in positions:
        print('begin position',position.sys_fullname,position.sys_userid,position.uuid,company)
        userrights = Useright.objects.filter(company=company,flag='Y',sys_userid=''.join(str(position.uuid).split('-')))

        empls = Empl.objects.filter(company=company,flag='Y',storecode='00',status='Y',position=position.sys_userid)
        for empl in empls:
            print('begin empl',empl.ecode, empl.ename)
            try:
                hdsysuser = Hdsysuser.objects.get(company=company,storecode=empl.storecode,sys_userid=empl.ecode)
            except:
                hdsysuser = Hdsysuser.objects.create(company=company, storecode=empl.storecode, sys_userid=empl.ecode,
                                                     sys_passwd='12345', sys_fullname=empl.ename, sys_userstatus=1)
                hdsysuser.save()
                # print('no hdsysuser',empl.ecode,empl.ename)

            print('userrights',userrights, hdsysuser.sys_userid,hdsysuser.sys_fullname,hdsysuser.uuid )
            for userright in userrights:
                print('begin userright',hdsysuser.sys_userid,hdsysuser.sys_fullname,userright.sys_module)
                try:
                    emplright = Useright.objects.get(company=company,storecode=empl.storecode,sys_userid=''.join(str(hdsysuser.uuid).split('-')),sys_module=userright.sys_module)
                except:
                    emplright = Useright.objects.create(company=company,storecode=empl.storecode,sys_userid=''.join(str(hdsysuser.uuid).split('-')),sys_module=userright.sys_module,sys_writerights='N')
                print('emplright',emplright.sys_module)
                # emplright.save()

    return HttpResponse('完成', content_type="application/json")