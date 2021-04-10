#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from datamanage import views
from datamanage.getolddata_foryoulan import GetOldData
from datamanage.init_company import init_common_base_info  #,init_baseinfo

urlpatterns=[
    # init company
    url(r'^init_baseinfo/?', views.init_baseinfo),
    # url(r'^init_common_base_info/?', init_common_base_info),
    # url(r'^init_demo_items/', views.init_demo_items),

    url(r'^getolddata/', GetOldData),
    url(r'^EmplReadAndWrite/?', views.EmplReadAndWrite),
    url(r'^ReadAndWrite/?',views.ReadAndWrite),
    url(r'^GoodsReadAndWrite/?', views.GoodsReadAndWrite),
    url(r'^ServieceReadAndWrite/?', views.ServieceReadAndWrite),
    url(r'^GenerateCardTypeByServiece/?', views.GenerateCardTypeByServiece),
    url(r'^VipReadAndWrite/?', views.VipReadAndWrite),
    url(r'^CardtypeReadAndWrite/?', views.CardtypeReadAndWrite),
    url(r'^CardinfoReadAndWrite/?', views.CardinfoReadAndWrite),
    url(r'^transappoptionstolist/?', views.transappoptionstolist),
    url(r'^listtoappoption/?', views.listtoappoption),
    url(r'^fromsql_to_appoption/?', views.fromsql_to_appoption),

    url(r'^dailycheck/?', views.dailycheck),
    # generate oldcardtypebytiem from mssql youlan
    # url(r'^CardtypeItemDetailReadandWrite/?', views.CardtypeItemDetailReadandWrite),

    # generate promotions&promotiondetail by oldcardtypebyitem
    # url(r'^InitPromotionsInfo/?', views.InitPromotionsInfo),
    # url(r'^reordervip/', views.reordervip),
    # url(r'^reorderitem/', views.reorderitem),


]