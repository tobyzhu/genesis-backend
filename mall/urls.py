#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

import uuid
from django.conf.urls import include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token,jwt_response_payload_handler

from wechat import views
from mall import views
# from .login import login,authorized



router = routers.DefaultRouter('genesis/')

urlpatterns=[
    url('', include(router.urls)),
    url(r'get_banners/?', views.get_banners),
    url(r'get_onlineshowtype/?', views.get_onlineshowtype),
    url(r'get_goodslist_byshowtype/?', views.get_goodslist_byshowtype),
    # url(r'get_goodslist_byshowtype/?', views.get_onlineitemlist_byshowtype),


]
