#coding = utf-8

from django.contrib.auth.models import User, Group
from rest_framework import serializers,pagination
from rest_framework.reverse import reverse
import uuid
import datetime

from common.constants import COMPANYID
from .models import WechatUser

class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="WechatUser-detail",lookup_field='uuid')
    class Meta:
        model = WechatUser
        fields = ('uuid', 'nickname', 'url','openid','unionid')

    url = serializers.HyperlinkedIdentityField(view_name="WechatUser-detail")

