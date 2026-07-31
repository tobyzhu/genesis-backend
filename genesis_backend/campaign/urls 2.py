from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^trial-signup/$', views.trial_signup, name='trial-signup'),
]
