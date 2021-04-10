# encoding=utf-8
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render
# from django.views import View

import hashlib
import simplejson,json
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseServerError, Http404,JsonResponse,HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import urllib,requests
from rest_framework_jwt.views import obtain_jwt_token,jwt_response_payload_handler

from rest_framework_jwt.settings import api_settings
import uuid
import xml.etree.ElementTree as ET


from django.contrib.auth.backends import ModelBackend

import wechat.constants as settings
# from genesis.utils import log_err

from django.contrib.auth import authenticate
# Create your views here.
from django.contrib import auth
from rest_framework import  pagination,viewsets
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import uuid as UUID
import datetime
import json

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .WXBizDataCrypt import WXBizDataCrypt
from .third_party import wzhifusdk

# Create your views here.

import wechat.constants as wxsetting
from  wechat.constants import *
import common.constants
from adviser.views import sql_to_json
from .models import WechatUser,WechatAppFunctions
#from common.models import CompanyItem,CompanyOrder,CompanyOrderItem,CompanyOrderPayInfo
from baseinfo.models import Empl,Vip,Storeinfo,Appoption
from .wx_pay_setting import *

def getUserTypeByAppID(appcode):
    # 帮小主
    if appcode=='100':
        return '100'

    # 小主咖
    if appcode=='200':
        return '200'

status={
    'HTTP_400_BAD_REQUEST':400,
    'HTTP_503':503
}

def get_appinfo(appcode):
    # 帮小主
    if appcode=='100':
        appinfo={
            'appid':'wx2c96228775369c88',
            'secret':'05828429c23e5cd7f9c15b2ad360c28f',
            'token':  'fkfix9jn2nVMzdfk0921Fzwik32',
            'my_username':  'gh_bef61927eda5',
            'encodingAESKey': 'EKmn6KjeDvfS7Av90ljAUwhmTDJvpSkuqE3ZE19ZQq1',
            'mch_id':my_mch_id,
            'UFDODER_URL':'https://api.mch.weixin.qq.com/pay/unifiedorder',
            'NOTIFY_URL':BASE_DIR+'/wechat/payment_notify/',
            'CREATE_IP':'',
            'nonce_str':'',
            'cert_path':my_cert_path,
            'device_info':'WEB'
        }

        return appinfo

    # 小主咖
    # wechatapp @ softweb.com.cn
    if appcode=='200':
        appinfo={
            'appid':'wx0963eedb54cee209',
            'secret':'cc11acb75f07421dd803dc1a27578fa1',
            'token':'fkfix9jn2nVMzdfk0921Fzwik32',
            'my_username':'',
            'encodingAESKey':''
        }
        return appinfo

def get_uuid(appcode,mobile):
    if appcode=='100':
        wxuser =WechatUser.objects.get(appcode=appcode,mobile=mobile)
        if wxuser:
            return wxuser.uuid
            # empl = Empl.objects.get(company=wxuser.company,mtcode=wxuser.mobile)
            # if empl:
            #     return empl.uuid

class WechatBackend(ModelBackend):
   '''
   自定义用户验证(setting.py)
   '''
   def authenticate(self, openid, **kwargs):
       try:
           user=WechatUser.objects.get(openid=openid)
           # if user.check_openid(openid):
           #      return user
           if user:
               return user
       except Exception as e:
           return None


# @csrf_exempt
def WechatLogin(request):
    # 前端发送code到后端,后端发送网络请求到微信服务器换取openid
    appcode= request.GET['appcode']
    code = request.GET['code']
    appinfo=get_appinfo(appcode)
    # print(wxsetting.wx_appid, wxsetting.wx_appsecret, code)
    if not code:
        # return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(400, content_type="application/json")

    url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
        .format(appinfo['appid'], appinfo['secret'], code)

    r = requests.get(url)
    print('r', r)
    res = json.loads(r.text)
    print('res=', res)
    openid = res['openid'] if 'openid' in res else None
    session_key = res['session_key'] if 'session_key' in res else None
    print('openid=', openid,'session_key=',session_key)

    if not openid:
        resp_data = {
            "code": 500,
            "company": common.constants.DEMO_COMPANY,
            "storecode": common.constants.DEMO_SOTRECODE,
            "ecode":common.constants.DEMO_ECODE,
            "user_uuid": '',
            "nickname": 'demo',
            "avatarUrl": '',
            "openid":''
        }
        print(resp_data)
        return JsonResponse(resp_data)
        # return Response({'message': '微信调用失败'}, status=status.HTTP_503)
        # return HttpResponse(500, content_type="application/json")
    # 判断用户是否第一次登录
    try:
        wechatuser = WechatUser.objects.get(openid=openid,appcode=appcode)
        print('exists:',wechatuser)
    except Exception:
        # 微信用户第一次登陆,新建用户
        print('create wechatuser')
        # nickname = nickName   #request.data.get('nickname')
        # sex = userinfo['gender'] # request.data.get('sex')
        # avatarUrl = avatarUrl # request.data.get('avatar')
        # wechatuser = WechatUser.objects.create(appcode=appcode,openid=openid,nickname=nickname, avatarUrl=avatarUrl)
        wechatuser = WechatUser.objects.create(appcode=appcode,openid=openid)
        # wechatuser.set_password(openid)

        # print('userinfo',userinfo.nickName)

    # 手动签发jwt
    # jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
    # jwt_encode_handler = settings.JWT_ENCODE_HANDLER
    # #
    # payload = jwt_payload_handler(wechatuser)
    # token = jwt_encode_handler(payload)
    # print('payload',payload)
    # print('token',token)
    if appcode=='100':
        resp_data = {
            "code" : 200,
            "company":wechatuser.company,
            "user_uuid": wechatuser.uuid.__str__().replace('-',''),
            "nickname": wechatuser.nickname,
            "avatarUrl": wechatuser.avatarUrl,
            "session_key":session_key,
            "openid":openid
        }
        print(resp_data)
        return JsonResponse(resp_data)

    if appcode=='200':
        try:
            vip = Vip.objects.get(uuid=wechatuser.useruuid)
        except:
            vip = None

        resp_data = {
            "code" : 200,
            "company":wechatuser.company,
            "user_uuid": wechatuser.uuid.__str__().replace('-',''),
            "nickname": wechatuser.nickname,
            "avatarUrl": wechatuser.avatarUrl,
            "session_key":session_key,
            "openid":openid,
            "vipuuid":str(vip.uuid)
        }
        print(resp_data)
        return JsonResponse(resp_data)
    # return HttpResponse(resp_data, content_type="application/json")

#
# def getPhoneNumber(request):
#
def deCrypt(request):
    appId = wxsetting.my_appid
    # sessionKey = wxsetting.my_secret
    encryptedData = request.GET['encryptedData'] #'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
    iv = request.GET['iv']  #'r7BXXKkLb8qrSNn05n0qiA=='
    sessionKey=request.GET['session_key']
    print(appId,sessionKey)
    pc = WXBizDataCrypt(appId, sessionKey)

    print( pc.decrypt(encryptedData, iv))
    return 0


def getphone(request):
    try:
        appcode=request.GET['appcode']
    except:
        appcode='100'
    appinfo = get_appinfo(appcode)
    appId =appinfo['appid']

    access_token= get_access_token(appcode)

    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        user_uuid = request.GET['user_uuid']
    except:
        user_uuid=''

    # 获取加密手机号
    encryptedData=request.GET['encryptedData']

    # 处理加密的手机号
    # encryptedData = encryptedData + '=='

    # 获取加密向量
    # vinum = request.GET.get('vinum')

    iv = request.GET['iv']

    # 处理加密向量
    # iv = vinum + '=='
    # iv=iv +'=='


    # appid
    appId =appinfo['appid']

    # 获取sessinkey
    # redis_conn = get_redis_connection('session_key')
    # sessionKey = redis_conn.get('session_key_%s' % openid)
    sessionKey =  request.GET['session_key']

    # 解密手机号
    print('appId=',appId,'sessionKey=', sessionKey)
    pc = WXBizDataCrypt(appId, sessionKey)
    # mobile_obj = pc.decrypt(encryptedData, vinum)
    mobile_obj = pc.decrypt(encryptedData, iv)
    mobile = mobile_obj['phoneNumber']

    if len(user_uuid)>0:
        wxuser = WechatUser.objects.get_or_create(uuid=user_uuid,appcode=appcode)[0]
        wxuser.mobile=mobile
        wxuser.save()
        company=wxuser.company
        if appcode=='100':
            uuidtype='empl'

            empl = Empl.objects.get(company=company,cmtcode=mobile)
            uuid=empl.uuid
            code = empl.ecode
            name =empl.ename

            data = {
                'uuidtype': uuidtype,
                'uuid': uuid,
                'mobile': mobile,
                'code': code,
                'name': name
            }
            return JsonResponse(data=data)

        if appcode=='200':
            uuidtype = 'vip'
            try:
                vip =Vip.objects.get(company=company,mtcode=mobile)
                print('get vip,',vip.vcode, vip.vname)

                vip.openid = wxuser.openid
                vip.save()

                uuid=vip.uuid
                code=vip.vcode
                name=vip.vname
                data = {
                    'statuscode':200,
                    'uuidtype':uuidtype,
                    'vipuuid':vip.uuid,
                    'mobile': mobile,
                    'vcode':code,
                    'vname':name,
                    'viptype':vip.viptype,
                    'viplevel':vip.viplevel,
                    'access_token':access_token
                    # 'vip':vip
                }
                print('data',data)
                return JsonResponse(data=data)
            except:
                data = {
                    'statuscode':500,
                    'uuidtype':uuidtype,
                    'uuid':'',
                    'mobile': mobile,
                    'code':'',
                    'name':''
                }
                print('data',data)
                return JsonResponse(data=data)


class MobileView(APIView):
    '''解密手机号'''

    def get(self, request):
        print('request',request)
        # 获取加密手机号
        # encryptedData = request.GET.get('encryptedData')
        encryptedData=request.GET['encryptedData']

        # 处理加密的手机号
        encryptedData = encryptedData + '=='

        # 获取加密向量
        # vinum = request.GET.get('vinum')

        iv = request.GET['iv']

        # 处理加密向量
        # iv = vinum + '=='
        iv=iv
        # 获取openid

        # openid = request.GET.get('openid')

        # appid
        # appId = APPID
        appId = wxsetting.my_appid

        # 获取sessinkey
        # redis_conn = get_redis_connection('session_key')
        # sessionKey = redis_conn.get('session_key_%s' % openid)
        sessionKey =  request.GET('session_key')

        # 解密手机号
        print(appId, sessionKey)
        pc = WXBizDataCrypt(appId, sessionKey)
        # mobile_obj = pc.decrypt(encryptedData, vinum)
        mobile_obj = pc.decrypt(encryptedData, iv)
        mobile = mobile_obj['phoneNumber']
        print(mobile)

        try:
            empl = WechatUser.objects.get(phone=mobile)
            ecode='888'
        except:
            ecode='888'
        data = {
            'mobile': mobile,
            'ecode':ecode,
            'code':'200'
        }
        # return Response(data=data, status=status.HTTP_200_OK)
        return JsonResponse(data)

def Get_WechatApp_Function(request):
    where ='1=1 '
    try:
        appcode=request.GET['appcode']
    except:
        appcode='100'

    try:
        company=request.GET['company']
        # where = ' and company='+company
    except:
        company=common.constants.COMPANYID
        # where = ' and company='+company

    try:
        storecode=request.GET['storecode']
    except:
        storecode=''

    try:
        functiontype = request.GET['type']
    except:
        functiontype='100'

    try:
        ecode = request.GET['ecode']
    except:
        ecode=''

    try:
        wxusertype = request.GET['wxusertype']
    except:
        wxusertype='100'

    try:
        functionid = request.GET['functionid']
    except:
        functionid=''

    print('Get_WechatApp_Function request,company=',company,',appcode=',appcode,wxusertype,functiontype,functionid)

    # functions = json.dumps(WechatAppFunctions.objects.filter(flag='Y',valiflag='Y',company=company,functionid=functionid).values('id','text','url','image'))
    # print('functions=',functions)

    sql = " select id,text,url,image" \
          " from WechatAppFunctions " \
          " where flag='Y' and valiflag ='Y' and company=%s AND appcode=%s and wxusertype = %s and functionid=%s" \
          " order by id asc"

    params = (company+' '+ appcode + ' ' + wxusertype + ' ' + functionid ).split()
    print(sql,params)
    json_data = sql_to_json(sql,params)
    return HttpResponse(json_data, content_type="application/json")

    # functions = json.dump(list(WechatAppFunctions.objects.filter(flag='Y',valiflag='Y',company=company,functionid=functionid).values_list('id','text','url','image')))
    # print(functions)
    # return JsonResponse(functions)

    # return HttpResponse(json_data, content_type="application/json")

def get_access_token(appcode):
    appinfo=get_appinfo(appcode)

    url=  "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(appinfo['appid'], appinfo['secret'])
    # url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
    #     .format(appinfo['appid'], appinfo['secret'])

    r= requests.get(url)
    print('r', r)
    res = json.loads(r.text)
    print('access token res=', res)
    return res

def get_qrcode(request):
    appcode= request.GET.get('appcode')
    qrcodetype = request.GET.get('qrcodetype')
    appinfo = get_appinfo(appcode)
    access_token = get_access_token(appcode)
    scene='yfy'
    # if qrcodetype=='unlimited':
    param={
        'scense':scene
    }
    print('param',param,'access_token',access_token['access_token'])
    url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(access_token['access_token'])
    # url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=ACCESS_TOKEN'
    # r = requests.post(url,json.dumps(param))
    print('url',url)

    ret = requests.post(url, json=param)

    print(ret.content)
    with open('getwxacodeunlimit.png', 'wb') as f:
        f.write(ret.content)

    # return res

    return HttpResponse(ret, content_type="application/json")

def get_company_order_no(prefix):
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    result = prefix + '' + local_time + random_str(5)
    return result

# def Payment(request):
#     try:
#         appcode = request.GET['appcode']
#     except:
#         appcode = '100'
#
#     app_wx_config = get_appinfo(appcode)
#     # appid = appinfo['appid']
#
#     company=request.GET['company']
#     companyname= Appoption.objects.get(company='common',seg='company',itemname=company).itemvalues
#
#     storecode=request.GET['storecode']
#     storeinfo = Storeinfo.objects.filter(company=company,storecode=storecode)
#
#     try:
#         openid = request.GET['openid']
#     except:
#         raise ValueError('Not find openid')
#         # openid ='os1ua5btyYTKgB2OPQY6RC249oEo'
#     try:
#         wechatuser= WechatUser.objects.get(openid=openid)
#     except:
#         raise ValueError('Not find WechatUser ')
#
#     companyitemid = request.GET['companyitemid']
#     try:
#         companyitem = CompanyItem.objects.get(id=companyitemid)
#         company_item_name= companyitem.company_item_name
#         company_item_desc = companyitem.company_item_desc
#         company_item_price = companyitem.company_item_price
#         company_item_amount = companyitem.company_item_amount
#     except:
#         raise ValueError('Not find companyitem')
#
#     print('companyitem',companyitem.company_item_name)
#
#     order_no= get_company_order_no('shgv')
#     company_order = CompanyOrder.objects.create(order_company=company,wechatuser=wechatuser,openid=openid,order_no=order_no,order_amount=company_item_amount,order_status='10',payed_datetime=datetime.datetime.now())
#     companyorderitem = CompanyOrderItem.objects.create(company_order=company_order,company_item=companyitem,order_no=order_no,order_item=companyitem.company_item_code,
#                                                        payed_qty=companyitem.company_item_qty,payed_price=companyitem.company_item_price,payed_amount=company_item_amount,
#                                                        company_pay_period=companyitem.company_pay_period )
#     companyorderpayinfo = CompanyOrderPayInfo.objects.create(company_order=company_order,order_no=order_no,payed_method='微信支付',payed_amount=company_item_amount)
#     print('order_no',order_no,company_order.openid)
#
#     payparam={
#         'order_no':order_no,
#         'total_fee':company_item_amount,
#         'openid':openid,
#         'body':companyname +'/'+company_item_name
#     }
#     print('payparam',payparam)
#     paydetail= get_jsapi_params2(payparam)
#
#     print('paydetail',paydetail)
#
#     company_order.wx_prepay_id=paydetail['prepay_id']
#     company_order.save()
#
#     json_data = json.dumps(paydetail)
#     print('json_data',json_data)
#     # return json_data
#     return HttpResponse(json_data, content_type="application/json")
#     # return HttpResponse(paydetail)


@csrf_exempt
def Payment_notify(request):
    '''
    微信支付回调接口
    无需登录便可访问
    无需参数
    '''
    try:
        print('请求方法：',request.method)
        return_xml = """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        webData = request.body
        print('回调返回信息：',webData)
        if bool(webData):
            xmlData = ET.fromstring(webData)
            if xmlData.find('return_code').text != 'SUCCESS':
                print('回调出现错误')
                return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
            else:
                if xmlData.find('result_code').text != 'SUCCESS':
                    print('支付失败！')
                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
                else:
                    order_no = xmlData.find('out_trade_no').text
                    transaction_id = xmlData.find('transaction_id').text
                    print('支付成功返回的订单编号：',order_no,transaction_id)
                    companyorder = CompanyOrder.objects.get(order_no=order_no)
                    companyorder.wx_transaction_id=transaction_id
                    companyorder.save()

                    return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')
    except Exception as e:
        print(e)
        print({"message": "网络错误：%s"%str(e), "errorCode": 1, "data": {}})
        return_xml = """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        return HttpResponse(return_xml,content_type='application/xml;charset=utf-8')

def get_sanboxkey(request):

    # url='https://api.mch.weixin.qq.com/sandboxnew/pay/micropay/?mch_id=1575233481&nonce_str=DDPfCeZDY3RqFjbS&sign=0326E5D62F9588EAC816995469170433'
    #
    # response = requests.request('post', url)
    # print('response',response.content)
    # return HttpResponse(response)
    # return response.content
    sandboxkey=get_sandboxkey()
    print('sandboxkey',sandboxkey)
    return HttpResponse(sandboxkey,content_type='applications/xml;charset=utf-8')

# def queryorder(request):
#     out_trade_no=request.GET['order_no']
#     print('out_trade_no',out_trade_no)
#     result = get_orderquery(out_trade_no)
#     if result['result_code']=='SUCCESS':
#         companyorder = CompanyOrder.objects.get(order_no=out_trade_no)
#         companyorder.wx_transaction_id=result['transaction_id']
#         CompanyOrder.order_status='20'
#         companyorder.save()



    return HttpResponse(result,content_type='applications/json;charset=utf-8')



