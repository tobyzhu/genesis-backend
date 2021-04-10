#coding:utf-8

from django.conf.urls.static import static
from django.conf import settings

import uuid
from django.conf.urls import include,url
from rest_framework import routers
from .views import EmplViewSet,PositionViewSet,UserViewSet,GroupViewSet,VipViewSet,Vip_list,Vip_detail,SrvtoptyViewSet,SerieceViewSet,get_viplist_byecode, GoodsViewSet
from .views import CardtypeViewSet,CardvsdiViewSet,get_serviece,get_servieceprice,get_goodslist_bykeyword,get_goods,get_appoption_byseg
from .tools import set_vip_pinyin,set_mnemoniccode
import baseinfo.views
from . import views


router = routers.DefaultRouter('genesis/')
router.register(r'user',UserViewSet)
router.register(r'group',GroupViewSet)
router.register(r'position', PositionViewSet)
router.register(r'empl', EmplViewSet)
router.register(r'vip', VipViewSet)
router.register(r'srvtopty', SrvtoptyViewSet)
router.register(r'serviece', SerieceViewSet)
router.register(r'goods', GoodsViewSet)
router.register(r'cardtype', CardtypeViewSet)
router.register(r'cardvsdi', CardvsdiViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('^genesis/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    url('', include(router.urls)),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^vip_list/?', Vip_list),
    url(r'^vip_detail/?<uuid:pk>', Vip_detail),
    url(r'^get_viplist_byecode/?', get_viplist_byecode),
    url(r'^get_vipbaseinfo/?', views.get_vipbaseinfo),
    url(r'^set_vip_pinyin/?', set_vip_pinyin),
    url(r'^create_vip/', views.create_Vip),
    url(r'^update_vip/', views.update_Vip),
    url(r'^get_cardtypelist/', views.get_cardtypelist),
    url(r'^get_serviece/?', get_serviece),
    url(r'get_srvprice/?', views.get_servieceprice),
    url(r'^get_goods/?', get_goods),
    url(r'^get_appoption_byseg/?', get_appoption_byseg),
    url(r'^get_empllist/', views.get_empllist),
    url(r'^get_pmcodelist/', views.get_pmcodelist),
    url(r'^get_seccodelist/', views.get_seccodelist),
    url(r'^get_roomlist/', views.get_roomlist),
    url(r'^get_instrumentlist/', views.get_instrumentlist),
    url(r'^get_nextvcode/', views.get_nextvcode),
    url(r'^get_promotionslist/', views.get_promotionslist),
    url(r'^get_brandlist/', views.get_brandlist),
    url(r'^get_displayclass_bybrand/', views.get_displayclass_bybrand),
    url(r'^get_itemlist_brandanddisplayclasse/', views.get_itemlist_brandanddisplayclasse),
    url(r'^get_itemstructure/', views.get_itemstructure),
    url(r'^set_mnemoniccode/?', set_mnemoniccode),
    # 权限管理设定
    url(r'^generate_hdsysuser_by_empl/?', views.generate_hdsysuser_by_empl),
    url(r'^generate_userright_by_position/?', views.generate_userright_by_position),

    url(r'^get_goodslist_bykeyword/?', views.get_goodslist_bykeyword),
    url(r'^get_cardtypelist_bykeyword/?', views.get_cardtypelist_bykeyword),

    # path('snippets/<int:pk>/', views.snippet_detail),
]