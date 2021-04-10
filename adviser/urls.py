#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

import uuid
from django.conf.urls import include
from rest_framework import routers
from adviser.views import BookingeventViewSet,CardinfoViewSet,AddHung, NewCardHung,ServieceHung,AddShoppingCart,get_ShoppingCart,ShoppingCartHung,modify_ShoppingCartItem,get_ShoppingCartItem
from adviser import views


router = routers.DefaultRouter()
# router.register(r'bookingevent',BookingeventViewSet)
# router.register(r'cardinfo',CardinfoViewSet)

urlpatterns=[
    url('', include(router.urls)),
    url(r'getviplist/', views.getviplist),
    url(r'get_vipList_byviptypeandecode/', views.get_VipList_ByVipTypeAndEcode),
    url(r'get_viplist_bylevel/', views.get_VipList_ByLevel),

    url(r'get_vip_cardlist/', views.get_vip_cardlist),
    url(r'get_vip_itemlist/', views.get_vip_itemlist),

    # url(r'get_vip_cardlist2/', views.get_vip_cardlist2),
    url(r'get_bookinglist/', views.get_bookinglist),
    url(r'get_bookingevent/', views.get_bookingEvent),
    url(r'get_bookingable_empllist/', views.get_bookingable_empllist),
    url(r'add_bookingevent/', views.add_BookingEvent),
    url(r'update_bookingevent/', views.update_BookingEvent),

    url(r'get_nextccode/', views.get_nextccode),

    url(r'newcardhung/', views.NewCardHung),
    url(r'fillcardhung/', views.FillCardHung),
    url(r'serviecehung/', views.ServieceHung),
    url(r'addshoppingcart/', views.AddShoppingCart),
    url(r'get_shoppingcart/', views.get_ShoppingCart),
    url(r'get_shoppingcartitem/', views.get_ShoppingCartItem),
    url(r'modify_shoppingcartitem/', views.modify_ShoppingCartItem),
    url(r'shoppingcarthung/?', views.ShoppingCartHung),
    url(r'addhung/', views.AddHung),
    url(r'get_hung_byvipuuid/', views.get_hung_byvipuuid),
    url(r'get_hungitem/', views.get_hungitem),
    url(r'update_hungitem/', views.update_hungitem)

#    url(r'^images$',)
]
