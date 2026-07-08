#coding:utf-8
app_name = 'goods'
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from goods import views
from goods.checkgoods import checksalehead_not_in_goodstranslog,reseverlog

urlpatterns=[

    url(r'processgoods/?',views.ProcessGoods),
    url(r'ProcessDupGoodstranslog/?', views.ProcessDupGoodstranslog),
    url(r'www.ywproperty.co.uk/?', views.RecalcuteGoodsTransLogByStorecode),

    url(r'FillTransdtl/', views.FillTransdtl),
    url(r'checksalehead_not_in_goodstranslog/', checksalehead_not_in_goodstranslog),
    url(r'reseverlog/', reseverlog),
    url(r'^get_goodstockqty/?', views.get_goodstockqty),
    url(r'^yfy_goodsreport/', views.yfy_goodsreport),

# checksalehead_not_in_goodstranslog

    # url(r'changestatus/?',views.changestatus),
    # url(r'checkpwd/',views.checkpwd),
    # url(r'QueryBookingStatus/',views.QueryBookingStatus)了
#    url(r'^images$',)
]