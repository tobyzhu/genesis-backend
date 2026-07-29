#coding:utf-8
app_name = 'booking'
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from booking import views

urlpatterns=[
    # ========== 旧路由 (保留，banxiaozhu 依赖) ==========
    url(r'^querybooking/?',views.querybooking),
    url(r'queryroom/',views.queryroom),
    url(r'changestatus/?',views.changestatus),
    url(r'checkpwd/',views.checkpwd),
    url(r'QueryBookingStatus/',views.QueryBookingStatus),

    # ========== 新 REST 端点 (genesis_pc 使用) ==========
    # 预约事件 CRUD
    url(r'^events/$', views.events_list, name='events_list'),
    url(r'^events/create/$', views.events_create, name='events_create'),
    url(r'^events/(?P<event_id>\d+)/$', views.events_detail, name='events_detail'),
    url(r'^events/(?P<event_id>\d+)/update/$', views.events_update, name='events_update'),
    url(r'^events/(?P<event_id>\d+)/status/$', views.events_status, name='events_status'),
    url(r'^events/(?P<event_id>\d+)/cancel/$', views.events_cancel, name='events_cancel'),
    url(r'^events/(?P<event_id>\d+)/check-conflicts/$', views.events_check_conflicts, name='events_check_conflicts'),

    # 参考数据
    url(r'^timesets/$', views.timesets_list, name='timesets_list'),
    url(r'^schedules/$', views.schedules_list, name='schedules_list'),
    url(r'^employees/$', views.employees_list, name='employees_list'),
    url(r'^rooms/$', views.rooms_list, name='rooms_list'),
    url(r'^instruments/$', views.instruments_list, name='instruments_list'),
    url(r'^schedules/save/$', views.schedules_save, name='schedules_save'),
    url(r'^schedules/shift-list/$', views.shift_list, name='shift_list'),
]
