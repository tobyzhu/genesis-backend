#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from jmj import views,jmjreport

urlpatterns=[

    url(r'readandwrite/?', views.ReadAndWrite),
    url(r'delinvaildtrans/?', views.DelInvaildTrans),
    url(r'^initperioddata/?', views.InitPeriodData),
    url(r'^SetPeriodData/?', views.SetPeriodData),
    url(r'^SetPeriodIqty/?', views.SetPeriodIqty),
    url(r'^SetYearPeriodData/?',views.SetYearPeriodData),
    url(r'^SetPrecentData/', views.SetPrecentData),
    url(r'^SetPeriodOrderQty/', views.SetPeriodOrderQty),
    url(r'^report1/', jmjreport.report1),








    # url(r'changestatus/?',views.changestatus),
    # url(r'checkpwd/',views.checkpwd),
    # url(r'QueryBookingStatus/',views.QueryBookingStatus)
#    url(r'^images$',)
]