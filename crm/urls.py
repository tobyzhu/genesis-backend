#coding:utf-8
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.conf import settings

from . import views

# from django.conf.urls import include
from rest_framework import routers
from .views import CrmCaseViewSet,CrmCaseDetailViewSet,VipViewSet,AddCrmCaseDetail,VipCaseDetailViewSet
from .models import CrmCase,CrmCaseDetail,VipCaseDetail
from baseinfo.models import Vip,Empl
from baseinfo.views import EmplViewSet
from crm.crmcase_yiren import getcrmcase_yiren

router = routers.DefaultRouter()
# router.register(r'user',UserViewSet)
# router.register(r'group',GroupViewSet)
router.register(r'vipcasedetail', VipCaseDetailViewSet)
router.register(r'crmcase', CrmCaseViewSet)
router.register(r'crmcasedetail', CrmCaseDetailViewSet)
router.register(r'vip', VipViewSet)
router.register(r'empl', EmplViewSet)

urlpatterns=[
    url('', include(router.urls)),
    # url(r'^baseinfo/vip/(?P<uuid>[^/.]+)/$', VipViewSet, namespace='vip-detail'),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^generatecrmcase/?', views.generatecrmcase),
    url(r'^update_crmcase/?', views.update_crmcase),
    url(r'^AddCrmCaseDetail/?', views.AddCrmCaseDetail),
    url(r'^UpdateCrmCaseDetail/?', views.UpdateCrmCaseDetail),
    url(r'^get_vipcasedetail_byvipuuid/?', views.get_vipcasedetail_byvipuuid),
    url(r'^update_vipcasedetail/?', views.update_vipcasedetail),
    url(r'^get_vipcasedetail/?', views.get_vipcasedetail),
    url(r'^get_planvipcasedetail_byecode/?', views.get_planvipcasedetail_byecode),
    url(r'^get_crmcaselist/?', views.get_crmcaselist),
    url(r'^get_vipconsumelist/?', views.get_vipconsumelist),
    url(r'^get_vip_crmcasedetail/?', views.get_vip_crmcasedetail),
    url(r'^get_crmcasedetail_bycaseid/?', views.get_crmcasedetail_bycaseid),
    url(r'^get_viplist_bycrmrptid/?', views.get_viplist_bycrmrptid),
    url(r'^getcrmcase_yiren/', getcrmcase_yiren),
    url(r'^get_crmsubreport/?', views.get_crmsubreport),


    # url(r'queryroom/',views.queryroom),
    # url(r'changebookingstatus/?',views.changebookingstatus),
    # url(r'test/',views.test)
#    url(r'^images$',)
]
