#coding = utf-8

from django.shortcuts import render
from django.core.serializers import serialize
import json
import numpy as np
import pandas as pd

from adviser.models import *
from adviser.views import sql_to_json
from baseinfo.models import *
from cashier.models import *
from common.constants import *
from adviser.views import *
from baseinfo.views import *
from cashier.views import *
from mall.models import Banner,onlineShowType,onlineShowItem

# Create your views here.

class onlineMall(object):
    def __init__(self,**kwargs):
        self.company = kwargs.get('company','')
        self.brand = kwargs.get('brand','')
        self.showtypecode = kwargs.get('showtypecode','')
        self.vipuuid=''

    def get_banners(self,**kwargs):
        apppage = kwargs.get('apppage','home')
        banners = Banner.objects.filter(flag='Y',company=self.company,apppage=apppage).values_list('id','linkURL','bannerimage','orderno')
        data_df = pd.DataFrame(list(banners),columns=('id','linkURL','bannerimage','orderno'))
        json_data = data_df.to_json(orient='records')
        return HttpResponse(json_data, content_type="application/json")

    def get_onlineshowtype(self):
        # onlineshowtypes = onlineShowType.objects.filter(company=self.company,flag='Y').values_list('id','showname','showimage','showurl').order_by('orderno')
        sql = "select showtypecode, showtypename, showtypeimage,orderno from onlineShowType where ttype='G' and company = %s order by orderno "
        params = ( self.company + ' ' ).split()
        json_data = sql_to_json(sql,params)
        return json_data
        # return HttpResponse(json_data, content_type="application/json")

    def get_onlinegoodslist(self,**kwargs):
        self.brand = kwargs.get('brand','%')
        sql = "select uuid, gcode, gname, brand, price,small_image, large_image from goods where  flag='Y' and saleflag='Y' and company=%s AND brand =  %s and saleschannels like '%20%' "
        params = ( self.company + ' '+ self.brand ).split()
        print('sql',sql)
        json_data = sql_to_json(sql,params)
        return json_data
        # return HttpResponse(json_data, content_type="application/json")

    def get_onlineitemlist_byshowtype(self,**kwargs):
        self.showtypecode = kwargs.get('showtypecode','%')
        print(self.company,self.showtypecode)
        onlinelist = onlineShowItem.objects.filter(flag='Y',company=self.company,onlineShowType__showtypecode=self.showtypecode).\
            values_list('goods__uuid','goods__gcode','goods__gname','itemdesc','onlineprice','small_showimage').order_by('id')
        print('onlinelist',onlinelist)
        data_df = pd.DataFrame(list(onlinelist),columns=('goods_uuid','gcode','gname','itemdesc','onlineprice','small_showimage'))
        data_df['goods_uuid'] = data_df.apply(lambda x: str(x.goods_uuid).replace('-',''), axis=1)
        print('data_df',data_df)
        json_data = data_df.to_json(orient='records',force_ascii=False)
        # json_data = json.dumps(list(onlinelist))
        print('json_data',json_data)

        return HttpResponse(json_data, content_type="application/json")

class onlineItem(object):
    def __init__(self,**kwargs):
        self.company = kwargs.get('company','')
        self.itemtype = kwargs.get('itemtype','G')
        self.itemcode = kwargs.get('itemcode','')
        self.item_uuid = kwargs.get('item_uuid','')

    def get_itembaseinfo(self):
        if self.itemtype == 'G':
            itembaseinfo = onlineShowItem.objects.filter(flag='Y',company=self.company,onlineShowType__ttype='G').\
                values_list('onlineShowType__showtypecode','onlineShowType__showtypename','goods__gname','goods_gname','itemdesc','onlineprice')


def get_banners(request):
    company=request.GET['company']
    apppage =request.GET['apppage']
    params = {
        'company':company,
        'apppage':apppage
    }
    onlinemall = onlineMall(**params)
    json_data = onlinemall.get_banners(**params)
    return HttpResponse(json_data, content_type="application/json")

def get_onlineshowtype(request):
    company=request.GET['company']
    params = {
        'company':company
    }
    onlinemall = onlineMall(**params)
    json_data = onlinemall.get_onlineshowtype()
    return HttpResponse(json_data, content_type="application/json")

def get_goodslist_byshowtype(request):
    company = request.GET['company']
    showtypecode = request.GET['showtypecode']
    if len(showtypecode) == 0:
        showtypecode='100'

    params = {
        'company':company
    }
    onlinemall = onlineMall(**params)

    # params2 = {
    #     'brand':showtypecode
    # }
    # json_data = onlinemall.get_onlinegoodslist(**params2)
    params2 = {
        'showtypecode':showtypecode
    }
    json_data = onlinemall.get_onlineitemlist_byshowtype(**params2)

    return HttpResponse(json_data, content_type="application/json")