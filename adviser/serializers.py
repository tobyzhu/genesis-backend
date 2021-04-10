from rest_framework import serializers,pagination
from rest_framework.reverse import reverse
import uuid
import datetime

from common.constants import COMPANYID
from adviser.models import Bookingevent,Cardinfo
from baseinfo.models import Vip
from baseinfo.serializers import GenesisSerializer,VipSerializer
# from baseinfo.views import Vip_detail,Vip_list

class BookingeventSerializer(serializers.HyperlinkedModelSerializer):
    bookingstartdate =serializers.DateField(required=True)
    bookingstarttime = serializers.TimeField(required=True)
    bookingendtime = serializers.TimeField(required=False)
    vcode = serializers.CharField(required=False,max_length=16)
    vname = serializers.CharField(required=True,max_length=16)
    mtcode = serializers.CharField(required=False,max_length=16)
    ecode = serializers.CharField(required=False,max_length=16)
    roomid = serializers.CharField(required=False,max_length=16)
    instrumentid = serializers.CharField(required=False,max_length=16)
    bookingdetail = serializers.CharField(required=False,max_length=128)
    # ename = serializers.CharField(required=False,max_length=32)
    vipuuid = VipSerializer(required=False)
    # vipurl = serializers.HyperlinkedIdentityField(view_name='vip-detail',lookup_field='vipuuid')
    # positioncode = serializers.HyperlinkedModelSerializer(view_name='position-detail')
    # positions = serializers.HyperlinkedRelatedField('empls',view_name='empl-list', lookup_field='positioncode')
    url = serializers.HyperlinkedIdentityField(view_name="bookingevent-detail",lookup_field='bookingeventid')
    # links = serializers.SerializerMethodField()

    class Meta:
        model = Bookingevent
        fields = ('bookingstartdate','bookingstarttime','bookingendtime','vcode','vname','mtcode','ecode','roomid',
                  'roomstarttime','roomendtime','instrumentid','instrumentbookingstarttime','instrumentbookingendtime',
                  'bookingdetail','bookingeventid','companyid','storecode','bookingstatus','bookingoperdate','operecode','vipuuid','url')
        # fields = "__all__"
        # filter = "company="

    def create(self,  validated_data):
        # vipuuid = validated_data.get('vipuuid',self.vipuuid)
        # print(vipuuid)
        # vip = Vip.object.get(uuid=vipuuid)
        # # .vipuuid = vip
        # self.vipuuid = vip
        return Bookingevent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.mtcode = validated_data.get('mtcode', instance.mtcode)
        instance.vname = validated_data.get('vname', instance.vname)
        instance.save()
        return instance


class CardinfoSerializer(serializers.HyperlinkedModelSerializer):
    vcode=serializers.CharField(max_length=16,required=False)
    ccode =serializers.CharField(max_length=16,required=True)
    cardtype = serializers.CharField(max_length=16,required=False)
    leftmoney = serializers.DecimalField(max_digits=16,decimal_places=2,default=0,required=False)
    s_price = serializers.DecimalField(max_digits=10,decimal_places=4, required=False)
    leftqty = serializers.IntegerField(required=False,default=0,min_value=0)
    # cardtypeuuid = serializers.CharField(required=False,max_length=16)
    # vipuuid = VipSerializer(required=False)
    url = serializers.HyperlinkedIdentityField(view_name="cardinfo-detail",lookup_field='uuid')
    # linkslizers.SerializerMethodField()

    class Meta:
        model = Cardinfo
        fields = ('vcode','ccode','cardtype','leftmoney','s_price','leftqty','url')
        filter = "company="

    def create(self,  validated_data):
        print(validated_data)
        return Cardinfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.vcode = validated_data.get('vcode', instance.vcode)
        instance.cardtype = validated_data.get('cardtype', instance.cardtype)
        instance.save()
        return instance
