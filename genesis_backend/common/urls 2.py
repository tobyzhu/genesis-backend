#coding:utf-8
app_name = 'common'
from django.conf.urls import url

from django.conf.urls.static import static
from django.conf import settings

import uuid
from django.conf.urls import include
from rest_framework import routers
from common.views import WifiListViewSet,check_WifiList,check_userpwd,init_baseinfo,init_baseinfo_bystore,init_baseinfo_salon,init_demo,company_list,company_stores,switch_store #,CompanyItemViewSet,CompanyOrderViewSet
from baseinfo.auth_api import hdsysuser_login_json, hdsysuser_stores, hdsysuser_permissions, api_v1_hdsysuser_login, hdsysuser_search_json
from . import views
router = routers.DefaultRouter()
router.register(r'wifilist',WifiListViewSet)
# router.register(r'companyitem',CompanyItemViewSet)
# router.register(r'companyorder',CompanyOrderViewSet)

urlpatterns = [
    url('', include(router.urls)),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^check_wifilist/', check_WifiList),
    url(r'^check_userpwd/', check_userpwd),
    url(r'^hdsysuser_login/', hdsysuser_login_json),
    url(r'^hdsysuser_stores/', hdsysuser_stores),
    url(r'^hdsysuser_permissions/', hdsysuser_permissions),
    url(r'^hdsysuser_search/', hdsysuser_search_json),
    url(r'^init_baseinfo/', init_baseinfo),
    url(r'^init_baseinfo_bystore/', init_baseinfo_bystore),
    url(r'^init_baseinfo_salon/', init_baseinfo_salon),
    url(r'^init_demo/', init_demo),
    url(r'^company_list/', company_list),
    url(r'^switch_store/', switch_store),
    url(r"^company_stores/", company_stores),


    url(r'^query_companyorder/', views.query_CompanyOrder),

]


