from django.contrib.auth.models import User, Group
from rest_framework import serializers,permissions
from rest_framework.reverse import reverse
import uuid
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from common.constants import COMPANYID
from .models import CrmCase,CrmCaseDetail,VipCaseDetail
from baseinfo.models import Vip
from baseinfo.serializers import VipSerializer
from baseinfo.views import VipViewSet,EmplViewSet

class VipCaseDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='VipCaseDetail-detail',lookup_field='uuid')
    company =serializers.CharField(required=True,allow_blank=False)
    storecode =serializers.CharField(required=True,allow_blank=False)
    uuid = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = VipCaseDetail
        # fields =('casetype','vipuuid','viptype','vcode','vname','mtcode','ecode','status','url')
        fields ="__all__"
        # fields = ('uuid','casetype','vipuuid','ecode','ename','viptype','vcode','vname','mtcode','casedesc','planbegindate','vsdate','status','url')

class CrmCaseSerializer(serializers.HyperlinkedModelSerializer):
    url=  serializers.HyperlinkedIdentityField(view_name="crmcase-detail", lookup_field='uuid')
    # vipuuid = serializers.CharField(max_length=32)
    vipuuid = serializers.HyperlinkedIdentityField(view_name='vip-detail',lookup_field='uuid')
    ecode = serializers.HyperlinkedIdentityField(view_name='empl-detail',lookup_field='uuid')
    # ename = serializers.ReadOnlyField(source='ecode.ename')
    # viptype = serializers.ReadOnlyField(source='vipuuid.viptype')
    # vcode = serializers.ReadOnlyField(source='vipuuid.vcode')
    # vname= serializers.ReadOnlyField(source='vipuuid.vname')
    # mtcode = serializers.ReadOnlyField(source='vipuuid.mtcode')


    class Meta:
        model = CrmCase
        # fields =('casetype','vipuuid','viptype','vcode','vname','mtcode','ecode','status','url')
        fields ="__all__"
        # fields = ('uuid','casetype','vipuuid','ecode','ename','viptype','vcode','vname','mtcode','casedesc','planbegindate','vsdate','status','url')


class CrmCaseDetailSerializer(serializers.HyperlinkedModelSerializer):
    url=  serializers.HyperlinkedIdentityField(view_name="crmcasedetail-detail", lookup_field='uuid')
    # caseid = serializers.CharField(required=True,max_length=32)
    # caseid = serializers.HyperlinkedIdentityField(view_name='crmcase-detail',lookup_field='uuid')
    ecode = serializers.HyperlinkedIdentityField(view_name='empl-detail',lookup_field='uuid')
    ename = serializers.ReadOnlyField(source='ecode.ename')
    detaildescription = serializers.CharField(max_length=2000,required=True)


    class Meta:
        model = CrmCaseDetail
        # fields =('casetype','vipuuid','viptype','vcode','vname','mtcode','ecode','status','url')
        fields = ('caseid','ecode','ename','detaildescription','url')
        # fields = "__all__"

class VipSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vip-detail',lookup_field='uuid')

    class Meta:
        model = Vip
        fields = ('uuid','vcode','vname','mtcode','url')

    def create(self, validated_data):
        return Vip.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.mtcode = validated_data.get('mtcode', instance.mtcode)
        instance.vname = validated_data.get('vname',instance.vname)
        instance.save()
        return instance
