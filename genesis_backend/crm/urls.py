#coding:utf-8
app_name = 'crm'
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.conf import settings

from . import views
from . import pc_views
from . import mp_views

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
router.register(r'vip', VipViewSet, basename='vip')
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
    url(r'^vip_filter_options/?', views.get_vip_filter_options),
    url(r'^vip_insight/', views.vip_insight),
    url(r'^health_records/(?P<uuid>[^/]+)/', views.health_record_detail),
    url(r'^health_records/', views.health_record_list),

    # PC 客户关怀工作台 API
    url(r'^pc/dicts/?$', pc_views.crm_dicts),
    url(r'^pc/rules/?$', pc_views.crm_rule_list),
    url(r'^pc/rules/create/?$', pc_views.crm_rule_create),
    url(r'^pc/rules/(?P<uuid>[^/]+)/preview/?$', pc_views.crm_rule_preview),
    url(r'^pc/rules/(?P<uuid>[^/]+)/run/?$', pc_views.crm_rule_run),
    url(r'^pc/rules/(?P<uuid>[^/]+)/?$', pc_views.crm_rule_detail),
    url(r'^pc/tasks/?$', pc_views.crm_task_list),
    url(r'^pc/tasks/summary/?$', pc_views.crm_task_summary),
    url(r'^pc/tasks/create/?$', pc_views.crm_task_create),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/attempt/?$', pc_views.crm_task_attempt),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/attempt/(?P<attempt_uuid>[^/]+)/?$', pc_views.crm_task_attempt_delete),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/suggest/?$', pc_views.crm_task_suggest),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/complete/?$', pc_views.crm_task_complete),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/status/?$', pc_views.crm_task_status),
    url(r'^pc/tasks/(?P<uuid>[^/]+)/?$', pc_views.crm_task_detail),
    url(r'^pc/timeline/?$', pc_views.crm_timeline),
    url(r'^pc/timeline/(?P<uuid>[^/]+)/?$', pc_views.crm_timeline_detail),

    # 小程序端客户关怀 API（员工个人视角）
    url(r'^mp/vip-search/?$', mp_views.mp_vip_search),
    url(r'^mp/tasks/summary/?$', mp_views.mp_task_summary),
    url(r'^mp/tasks/?$', mp_views.mp_task_list),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/attempt/?$', mp_views.mp_task_attempt),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/attempt/(?P<attempt_uuid>[^/]+)/?$', mp_views.mp_task_attempt_delete),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/complete/?$', mp_views.mp_task_complete),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/status/?$', mp_views.mp_task_status),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/suggest/?$', mp_views.mp_task_suggest),
    url(r'^mp/tasks/(?P<uuid>[^/]+)/?$', mp_views.mp_task_detail),
    url(r'^mp/timeline/?$', mp_views.mp_timeline),


    # url(r'queryroom/',views.queryroom),
    # url(r'changebookingstatus/?',views.changebookingstatus),
    # url(r'test/',views.test)
#    url(r'^images$',)
]
