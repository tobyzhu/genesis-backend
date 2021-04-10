#coding:utf-8
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import include,url
from rest_framework import routers

from .emplarch_yfy import cal_emplarch_yfy,cal_empalarch_yfy_daily
from .emplarch_yiren import cal_emplarchivement_yiren,get_saveemplarch
from cashier import views



urlpatterns = [
    # path('^genesis/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url('', include(router.urls)),
    # url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'cal_emplarch_yfy/?', cal_emplarch_yfy),
    url(r'cal_empalarch_yfy_daily/?', cal_empalarch_yfy_daily),
    url(r'get_emplarch_bymonth/?', views.get_emplarch_bymonth),
    url(r'cal_emplarch_yiren/?', cal_emplarchivement_yiren),
    url(r'cal_emplarchivement/?', views.cal_emplarchivement),
    url(r'process_pertrans/?', views.process_pertrans),
    url(r'get_saveemplarch/?', get_saveemplarch),
    url(r'get_emplarchivementbyecode/?', views.get_emplarchivementbyecode),
    url(r'reculate_trans/?', views.reculate_trans),
    url(r'offset_trans/?', views.offset_trans),
    url(r'checkout_byvip/?', views.checkout_byvip),
    url(r'checkout_byhunguuid/?', views.checkout_byhunguuid),
    url(r'vipitemtrans_confirm/?', views.vipitemtrans_confirm),
    url(r'fillcardhistory/?', views.fillcardhistory),

    # path('snippets/<int:pk>/', views.snippet_detail),
]
