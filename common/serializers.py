from django.contrib.auth.models import User, Group
from rest_framework import serializers,pagination
from rest_framework.reverse import reverse
import uuid
import datetime

from common.constants import COMPANYID
from .models import WifiList #,CompanyItem, mpanyOrder,CompanyOrderItem,CompanyOrderPayInfo

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


class WifiListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wifilist-detail',lookup_field='uuid')
    class Meta:
        model = WifiList
        fields =('url','company','storecode','SSID','BSSID','valiflag')

#
# class CompanyItemSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = CompanyItem
#         fields =('id','company_item_code','company_item_name','company_item_desc','company_item_qty','company_pay_period','company_item_price')
#
# class CompanyOrderSerializer(serializers.HyperlinkedModelSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name='companyorder-detail',lookup_field='id')
#     wechatuser =serializers.CharField(required=True,allow_blank=False)
#     openid = serializers.CharField(required=True,max_length=128)
#     class Meta:
#         model = CompanyOrder
#         fields=('url','id','wechatuser','openid','unionid','order_no','order_amount','order_status','payed_datetime')
#
# class CompanyOrderItemSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = CompanyOrderItem
#         fields=('company_order','order_no','order_item','companylist','storelist','payed_qty','company_pay_period','payed_price','payed_amount','order_fromdate','order_todate')
#
# class CompanyOrderPayInfoSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = CompanyOrderPayInfo
#         fields=('company_order','order_no','payed_method','payed_amount')

