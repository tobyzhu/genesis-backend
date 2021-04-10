#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from booking import views

urlpatterns=[
    url(r'^querybooking/?',views.querybooking),
    url(r'queryroom/',views.queryroom),
    url(r'changestatus/?',views.changestatus),
    url(r'checkpwd/',views.checkpwd),
    url(r'QueryBookingStatus/',views.QueryBookingStatus)

#    url(r'^images$',)
]
