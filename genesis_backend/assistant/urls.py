#coding = utf-8
app_name = "assistant"

from django.conf.urls import url

from assistant import views

urlpatterns = [
    url(r"^$", views.assistant_page, name="assistant_page"),
    url(r"^switch-user/$", views.assistant_switch_user, name="assistant_switch_user"),
    url(r"^logout-admin/$", views.assistant_logout_admin_home, name="assistant_logout_admin_home"),
    url(r"^api/chat/$", views.assistant_chat_api, name="assistant_chat_api"),
    url(r"^api/agents/$", views.assistant_agents_api, name="assistant_agents_api"),
    url(r"^api/profiles/$", views.assistant_profiles_api, name="assistant_profiles_api"),
    url(r"^api/threads/$", views.assistant_threads_api, name="assistant_threads_api"),
    url(r"^api/export/$", views.assistant_export_api, name="assistant_export_api"),
    url(r"^api/export/datasets/$", views.assistant_export_datasets_api, name="assistant_export_datasets_api"),
    url(r"^api/vip/sleeping-alert/$", views.assistant_vip_sleeping_alert_api, name="assistant_vip_sleeping_alert_api"),
    url(r"^api/vip/batch-export/$", views.assistant_vip_batch_export_api, name="assistant_vip_batch_export_api"),
    url(
        r"^api/threads/(?P<pk>[0-9]+)/$",
        views.assistant_thread_detail_api,
        name="assistant_thread_detail_api",
    ),
]
