# encoding: utf-8

import hashlib
import time
import requests
from django.shortcuts import HttpResponse, render, redirect
from collections import OrderedDict
from random import Random
from bs4 import BeautifulSoup
import json

# import qrcode
# from bs4 import BeautifulSoup

from .constants import my_appid,my_mch_id,my_api_key

APP_ID = my_appid  # 你公众账号上的appid
MCH_ID = my_mch_id  # 你的商户号
API_KEY = my_api_key  # 微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里
APP_SECRECT = my_api_key
UFDODER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 该url是微信下单api
# UFDODER_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder"  # 该url是微信下单api
QUERYORDER_URL ="https://api.mch.weixin.qq.com/pay/orderquery"

NOTIFY_URL = "http://xxx/wechat/"  # 微信支付结果回调接口，需要改为你的服务器上处理结果回调的方法路径
CREATE_IP = '101.86.1.173'  # 你服务器的IP

# 生成随机字符串
def random_str(randomlength=8):
    """
    生成随机字符串
    :param randomlength: 字符串长度
    :return:
    """
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def order_num(phone):
    """
    生成扫码付款订单,
    :param phone:
    :return:
    """
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    result = phone + 'T' + local_time + random_str(5)
    return result


def get_sign(data_dict, key):
    # 签名函数，参数为签名的数据和密钥
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # print('params_str',params_str)
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    # print('sign',sign)
    return sign


def trans_dict_to_xml(data_dict):  # 定义字典转XML的函数
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')  # 返回XML，并转成utf-8，解决中文的问题


def trans_xml_to_dict(data_xml):
    soup = BeautifulSoup(data_xml, features='xml')
    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


def wx_pay_unifiedorde(detail):
    """
    访问微信支付统一下单接口
    :param detail:
    :return:
    """
    detail['sign'] = get_sign(detail, API_KEY)
    # print(detail)
    xml = trans_dict_to_xml(detail)  # 转换字典为XML
    response = requests.request('post', UFDODER_URL, data=xml)  # 以POST方式向微信公众平台服务器发起请求
    # data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    print('response',response,response.content)
    return response.content


def get_redirect_url():
    """
    获取微信返回的重定向的url
    :return: url,其中携带code
    """
    WeChatcode = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    urlinfo = OrderedDict()
    urlinfo['appid'] = APP_ID
    urlinfo['redirect_uri'] = 'http://xxx/wxjsapipay/?getInfo=yes'  # 设置重定向路由
    urlinfo['response_type'] = 'code'
    urlinfo['scope'] = 'snsapi_base'  # 只获取基本信息
    urlinfo['state'] = 'mywxpay'  # 自定义的状态码

    info = requests.get(url=WeChatcode, params=urlinfo)
    return info.url


def get_openid(code, state):
    """
    获取微信的openid
    :param code:
    :param state:
    :return:
    """

    if code and state and state == 'mywxpay':
        WeChatcode = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        urlinfo = OrderedDict()
        urlinfo['appid'] = APP_ID
        urlinfo['secret'] = APP_SECRECT
        urlinfo['code'] = code
        urlinfo['grant_type'] = 'authorization_code'
        info = requests.get(url=WeChatcode, params=urlinfo)
        info_dict = eval(info.content.decode('utf-8'))

        return info_dict['openid']
    return None

def get_sandboxkey():
    url='https://api.mch.weixin.qq.com/sandboxnew/pay/micropay/'
    params ={
        'mch_id': MCH_ID,
        'nonce_str': random_str(16)
    }
    params_list = sorted(params.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list)
    print('params_str',params_str)
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    print('sign',sign)

    params['sign'] = sign
    print('params',params)
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    print('xml',xml)
    # url=url+'?mch_id=1575233481&nonce_str=DDPfCeZDY3RqFjbS&sign=0326E5D62F9588EAC816995469170433'

    response = requests.request('post', url, data=params)
    print('response',response.content)
    return response.content



def get_jsapi_params(openid):
    """
    获取微信的Jsapi支付需要的参数
    :param openid: 用户的openid
    :return:
    """

    total_fee = 1  # 付款金额，单位是分，必须是整数
    # openid='os1ua5btyYTKgB2OPQY6RC249oEo'
    params = {
        'appid': APP_ID,  # APPID
        'mch_id': MCH_ID,  # 商户号
        'nonce_str': random_str(16),  # 随机字符串
        'out_trade_no': order_num('123'),  # 订单编号,可自定义
        'total_fee': total_fee,  # 订单总金额
        'spbill_create_ip': CREATE_IP,  # 发送请求服务器的IP地址
        'openid': openid,
        'notify_url': NOTIFY_URL,  # 支付成功后微信回调路由
        'body': 'xxx公司',  # 商品描述
        'trade_type': 'JSAPI',  # 公众号支付类型
    }
    # print(params)
    # 调用微信统一下单支付接口url
    notify_result = wx_pay_unifiedorde(params)
    print('notify_result',notify_result)
    content=  trans_xml_to_dict(notify_result)
    print('content',content)
    if content["return_code"] == 'SUCCESS':
        params['prepay_id'] = trans_xml_to_dict(notify_result)['prepay_id']
        params['timeStamp'] = int(time.time())
        params['nonceStr'] = random_str(16)
        params['sign'] = get_sign({'appId': APP_ID,
                                   "timeStamp": params['timeStamp'],
                                   'nonceStr': params['nonceStr'],
                                   'package': 'prepay_id=' + params['prepay_id'],
                                   'signType': 'MD5',
                                   },
                                  API_KEY)

        # 封装返回给前端的数据
        # data = {"prepay_id": prepay_id, "nonceStr": nonceStr, "paySign": paySign, "timeStamp": timeStamp}
        # return HttpResponse(packaging_list(data))
        print('params',params)
        return HttpResponse(params)
    else:
        return HttpResponse("请求支付失败")


    # return params

def get_jsapi_params2(options):
    """
    获取微信的Jsapi支付需要的参数
    :param openid: 用户的openid
    :return:
    """

    openid=options['openid']
    order_no = options['order_no']
    # total_fee = options['total_fee']*100
    total_fee = "%.0f" % (options['total_fee'] * 100)
    body= options['body']


    # total_fee = 1  # 付款金额，单位是分，必须是整数
    # openid='os1ua5btyYTKgB2OPQY6RC249oEo'
    params = {
        'appid': APP_ID,  # APPID
        'mch_id': MCH_ID,  # 商户号
        'nonce_str': random_str(16),  # 随机字符串
        'out_trade_no': order_no,  # 订单编号,可自定义
        'total_fee': total_fee,  # 订单总金额
        'spbill_create_ip': CREATE_IP,  # 发送请求服务器的IP地址
        'openid': openid,
        'notify_url': NOTIFY_URL,  # 支付成功后微信回调路由
        'body': body,  # 商品描述
        'trade_type': 'JSAPI',  # 公众号支付类型
    }
    # print(params)
    # 调用微信统一下单支付接口url
    notify_result = wx_pay_unifiedorde(params)
    print('notify_result',notify_result)
    content=  trans_xml_to_dict(notify_result)
    print('2 content',content)
    if content["return_code"] == 'SUCCESS':
        params['prepay_id'] = trans_xml_to_dict(notify_result)['prepay_id']
        print('parma[prepay_id',params['prepay_id'])
        params['timeStamp'] = int(time.time())
        params['nonceStr'] = random_str(16)

        params['sign'] = get_sign({'appId': APP_ID,
                                   "timeStamp": params['timeStamp'],
                                   'nonceStr': params['nonceStr'],
                                   'package': 'prepay_id=' + params['prepay_id'],
                                   'signType': 'MD5',
                                   },
                                  API_KEY)

        # 封装返回给前端的数据
        # data = {"prepay_id": prepay_id, "nonceStr": nonceStr, "paySign": paySign, "timeStamp": timeStamp}
        # return HttpResponse(packaging_list(data))

        print('2 params',params)
        return params

        # xml_data = trans_dict_to_xml(params)
        # print('xlm_data',xml_data)
        # json_data = json.dumps(params)
        # print('json_data',json_data)
        # return json_data

        # return HttpResponse(params)
    else:
        return HttpResponse("请求支付失败")

def get_orderquery(out_trade_no):
    params={
        'appid':APP_ID,
        'mch_id':MCH_ID,
        'out_trade_no':out_trade_no,
        'nonce_str':random_str(16),
        'sign_type': 'MD5'
    }
    params['sign'] = get_sign(params, API_KEY)
    print('params',params)
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    print('xml',xml)
    response = requests.request('post', QUERYORDER_URL, data=xml)  # 以POST方式向微信公众平台服务器发起请求
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    print('data_dict', data_dict)
    if data_dict['return_code']=='SUCCESS':

        # print('response',response,response.content)
        return data_dict
    else:

        print('return_code',response.return_code)
        return data_dict