#coding:utf-8
app_name = 'sysadmin'
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^models/$', views.model_list, name='sysadmin-models'),
    url(r'^models/(?P<app_label>\w+)\.(?P<model_name>\w+)/meta/$', views.model_meta, name='sysadmin-meta'),
    url(r'^data/(?P<app_label>\w+)\.(?P<model_name>\w+)/$', views.model_data, name='sysadmin-data'),
    url(r'^data/(?P<app_label>\w+)\.(?P<model_name>\w+)/(?P<pk>[0-9a-f-]+)/$', views.model_data_detail, name='sysadmin-data-detail'),
    url(r'^related-search/$', views.related_search, name='sysadmin-related-search'),
]
