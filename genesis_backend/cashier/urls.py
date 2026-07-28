#coding:utf-8
app_name = 'cashier'
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

    url(r'service_items/?', views.service_items),
    url(r'goods_items/?', views.goods_items),
    url(r'cardtype_items/?', views.cardtype_items),
    # path('snippets/<int:pk>/', views.snippet_detail),
    url(r'get_checkout_shortfall/?', views.get_checkout_shortfall),
    url(r'checkout_hungs/?', views.checkout_hungs),
    url(r'get_receipt/', views.get_receipt),
    url(r'get_checkedout_orders/?', views.get_checkedout_orders),
    url(r'batch_checkout/?', views.batch_checkout),
    url(r'payment_methods/?', views.payment_methods),
    url(r'customer_checkout_confirm/?', views.customer_checkout_confirm),
    url(r'update_checkedout/?', views.update_checkedout),
    url(r'shift_handover/?', views.shift_handover),
    url(r'daily_settlement/?', views.daily_settlement),
    url(r'get_order_payment/?', views.get_order_payment),
    url(r'search_by_payment/?', views.search_by_payment),
    url(r'settlement_history/?', views.settlement_history),
    url(r'settlement_detail/?', views.settlement_detail),
    url(r'customer_checkout/?', views.customer_checkout),
    url(r'payment_report/?', views.payment_report),
]
