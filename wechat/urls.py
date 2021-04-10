#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

import uuid
from django.conf.urls import include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token,jwt_response_payload_handler

from wechat import views
# from .login import login,authorized



router = routers.DefaultRouter('genesis/')

urlpatterns=[
    url('', include(router.urls)),
    url(r'get_wechatapp_function/', views.Get_WechatApp_Function),
    url(r'wechatlogin/', views.WechatLogin),
    url(r'decrypt/', views.deCrypt),
    url(r'getphone/', views.getphone),
    url(r'get_qrcode/', views.get_qrcode),
    # url(r'payment/', views.Payment),
    url(r'payment_notify/', views.Payment_notify),
    url(r'get_sanboxkey/', views.get_sanboxkey),
    # url(r'queryorder/?', views.queryorder),


    # url(r'login/', login),
    # 登入验证，使用JWT的模块，只要用户密码正确会自动生成一个token返回
    url(r'^login/', obtain_jwt_token),


    # url(r'authorized/', authorized),
# login

#    url(r'^images$',)
]
