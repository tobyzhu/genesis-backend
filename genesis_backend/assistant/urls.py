#coding = utf-8
app_name = "assistant"

from django.conf.urls import url

from assistant import mp_views, views

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
    url(r"^api/vip/lifecycle/$", views.assistant_vip_lifecycle_api, name="assistant_vip_lifecycle_api"),
    url(r"^api/vip/lifecycle/sync/$", views.assistant_vip_lifecycle_sync_api, name="assistant_vip_lifecycle_sync_api"),
    url(
        r"^api/vip/lifecycle/snapshot/$",
        views.assistant_vip_lifecycle_snapshot_api,
        name="assistant_vip_lifecycle_snapshot_api",
    ),
    url(
        r"^api/vip/lifecycle/migrations/$",
        views.assistant_vip_lifecycle_migrations_api,
        name="assistant_vip_lifecycle_migrations_api",
    ),
    url(
        r"^api/vip/lifecycle/crm-tasks/$",
        views.assistant_vip_lifecycle_crm_tasks_api,
        name="assistant_vip_lifecycle_crm_tasks_api",
    ),
    url(r"^api/vip/batch-export/$", views.assistant_vip_batch_export_api, name="assistant_vip_batch_export_api"),
    url(
        r"^api/threads/(?P<pk>[0-9]+)/$",
        views.assistant_thread_detail_api,
        name="assistant_thread_detail_api",
    ),
    url(r"^mp/api/chat/$", mp_views.mp_assistant_chat_api, name="mp_assistant_chat_api"),
    url(r"^mp/api/threads/$", mp_views.mp_assistant_threads_api, name="mp_assistant_threads_api"),
    url(
        r"^mp/api/threads/(?P<pk>[0-9]+)/$",
        mp_views.mp_assistant_thread_detail_api,
        name="mp_assistant_thread_detail_api",
    ),
    url(r"^mp/api/vip/lifecycle/$", mp_views.mp_vip_lifecycle_api, name="mp_vip_lifecycle_api"),
    url(
        r"^mp/api/vip/lifecycle/one/$",
        mp_views.mp_vip_lifecycle_one_api,
        name="mp_vip_lifecycle_one_api",
    ),
    url(
        r"^mp/api/vip/lifecycle/migrations/$",
        mp_views.mp_vip_lifecycle_migrations_api,
        name="mp_vip_lifecycle_migrations_api",
    ),
    url(
        r"^mp/api/vip/lifecycle/crm-tasks/$",
        mp_views.mp_vip_lifecycle_crm_tasks_api,
        name="mp_vip_lifecycle_crm_tasks_api",
    ),
]
