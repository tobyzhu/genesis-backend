#coding = utf-8

from django.contrib.auth.models import User, Group
from rest_framework import serializers,pagination
from rest_framework.reverse import reverse
import uuid
import datetime

from common.constants import COMPANYID
from .models import Empl,Position,Vip, Serviece,Servieceprice,Srvtopty,Goods,Goodsct,Cardvsdi,Cardtype

class GenesisSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        self.uuid = uuid()
        self.create_time = datetime.now()
        self.last_modified = datetime.now()
        self.flag='Y'
        self.company=COMPANYID
        return self.objects.save(**validated_data)

    def update(self,instance,validate_data):
        instance.last_modified = validate_data.get('last_modified', instance.last_modified)

    fields = (  'uuid', 'company', 'storecode','create_time', 'last_modified','creater','flag')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="user-detail",lookup_field='id')
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

    # url = serializers.HyperlinkedIdentityField(view_name="user-detail")

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class EmplSerializer(serializers.HyperlinkedModelSerializer):
    ecode =serializers.CharField(required=True,allow_blank=False)
    ename = serializers.CharField(required=False,max_length=32)
    position = serializers.CharField(required=True)
    # positioncode = serializers.HyperlinkedModelSerializer(view_name='position-detail')
    emplpwd = serializers.CharField(required=False)
    # positions = serializers.HyperlinkedRelatedField('empls',view_name='empl-list', lookup_field='positioncode')
    url = serializers.HyperlinkedIdentityField(view_name="empl-detail",lookup_field='uuid')
    # links = serializers.SerializerMethodField()
    class Meta:
        model = Empl
        fields = ('ecode','ename','position','emplpwd','url','uuid')

    # def create(self, validated_data):
    #         """
    #         Create and return a new `Snippet` instance, given the validated data.
    #         """
        # return Empl.objects.create(**validated_data)
    # def get_links(self, obj):
    #     request = self.context['request']
    #     return {
    #         'self': reverse('empl-detail',
    #                         kwargs={'pk': obj.pk}, request=request),
    #         'tasks': reverse('task-list',
    #                          request=request) + '?empl={}'.format(obj.pk),
    #     }


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Position
        fields = ('uuid','positioncode','positiondesc','bookingflag')

    def create(self, validated_data):
        return Position.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.positiondesc = validated_data.get('positiondesc', instance.positiondesc)
        instance.bookingflag = validated_data.get('bookingflag',instance.bookingflag)
        instance.save()
        return instance

class CardtypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='cardtype-detail',lookup_field='cardtype')
    class Meta:
        model = Cardtype
        fields =('url','cardtype','cardname')

class CardvsdiSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='serivece-detail',lookup_field='uuid')
    class Meta:
        model = Cardvsdi
        fields ="__all__"

class SrvtoptySerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='serivece-detail',lookup_field='uuid')
    class Meta:
        model = Srvtopty
        fields ="__all__"


class ServieceSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='serivece-detail',lookup_field='uuid')
    class Meta:
        model = Serviece
        fields =('uuid','svrcdoe','svrname','price','brand','srvrptypecode','displayclass1','tags')
        # fields =('svrcdoe','svrname')

# class ServiecepriceSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Servieceprice
#         fields = "__all__"

class GoodsSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='serivece-detail',lookup_field='uuid')
    class Meta:
        model = Goods
        fields =('gcode','gname','price','displayclass1','tags')

class VipSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vip-detail',lookup_field='uuid')
    company =serializers.CharField(required=True,allow_blank=False)
    storecode =serializers.CharField(required=True,allow_blank=False)
    uuid = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = Vip
        fields = ('uuid','company','storecode','viptype','vcode','vname','viplevel','mtcode','ecode','ecode2','url','pinyin','birth','source','occupation','vdesc')

    def create(self, validated_data):
        return Vip.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.mtcode = validated_data.get('mtcode', instance.mtcode)
        instance.vname = validated_data.get('vname',instance.vname)
        instance.save()
        return instance

class VipbyEcodeSerializer(serializers.HyperlinkedIdentityField):
    url = serializers.HyperlinkedIdentityField(view_name='vip-detail',lookup_field='uuid')
    class Meta:
        model = Vip
        fields = ('uuid','vcode','vname','viplevel','mtcode','url','pinyin')

class UserPagination(pagination.PageNumberPagination):
    page_size = 20

    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #     ('count', self.page.paginator.count),
    #     ('next', self.get_next_link()),
    #     ('previous', self.get_previous_link()),
    #     ('page_size', self.page_size),
    #     ('results', data)
    #     ]))