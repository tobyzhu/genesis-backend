#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from report import views
from .common_report import amount_bydate

urlpatterns=[
    url(r'setdailyreportno1/',views.SetDailyReportNo1),
    url(r'setreportdata/?', views.SetReportData),
    url(r'makeplanbyvip/', views.makePlanByVip),
    url(r'getnewvipinfo/', views.getNewVipInfo),
    url(r'get_storedata/', views.get_StoreData),
    url(r'get_dailystoredata/', views.Manage_Data.get_dailystoredata),
    url(r'get_costbybrand/', views.get_CostByBrand),
    url(r'get_vipbase_yiren/', views.get_VipBase_Yiren),
    url(r'^get_vipdata_yiren/?', views.get_vipdata_yiren),

    url(r'get_invipcnt/', views.Manage_Data.get_invipcnt),
    url(r'get_inviptimes/', views.Manage_Data.get_inviptimes),

    url(r'amount_bydate/', amount_bydate),

    url(r'^get_base_data/', views.get_base_data),
    url(r'^get_coredata_bystore/?', views.get_coredata_bystore),
    url(r'^get_monthlyreportno1/?', views.get_monthlyreportno1),
    url(r'^get_reportdata_leftmoney/?', views.get_reportdata_leftmoney),

    # url(r'QueryBookingStatus/',views.QueryBookingStatus)
    url(r'^images/?',views.read_img)
]