"""shgv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf import settings
from xadmin.plugins import xversion
import xadmin
from rest_framework_jwt.views import obtain_jwt_token

import adviser,booking.urls
from booking.views import querybooking,checkpwd

xversion.register_models()
xadmin.autodiscover()

urlpatterns = [

    url(r'booking/', include('booking.urls', namespace='booking')),
    url(r'checkpwd', booking.views.checkpwd),
    # url(r'changebookingstatus/?', adviser.views.changebookingstatus),
    url(r'admin/',include(admin.site.urls)),
    url(r'xadmin/',include(xadmin.site.urls)),
    url(r'common/', include('common.urls', namespace='common')),
    url(r'baseinfo/', include('baseinfo.urls',namespace='baseinfo')),
    url(r'adviser/',include('adviser.urls',namespace='adviser')),
    url(r'cashier/',include('cashier.urls',namespace='cashier')),
    url(r'goods/', include('goods.urls', namespace='goods')),
    url(r'crm/', include('crm.urls', namespace='crm')),
    url(r'jmj/', include('jmj.urls', namespace='jmj')),
    url(r'report/', include('report.urls', namespace='report')),
    url(r'datamanage/', include('datamanage.urls', namespace='datamanage')),
    url(r'sysoption/', include('baseinfo.urls', namespace='sysoption')),
    url(r'wechat/', include('wechat.urls', namespace='wechat')),
    url(r'mall/', include('mall.urls', namespace='mall')),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^api-token-auth/', obtain_jwt_token),
]

# urlpatterns = [url(r'^prefix/', include(urlpatterns))]
# urlpatterns = [url(r'^genesis/', include(urlpatterns))]

