from django.contrib import admin


# Register your models here.

from django import forms
import xadmin
from common.models import WifiList
# from baseinfo.models import Storeinfo
# from .models import CompanyItem,CompanyOrder,CompanyOrderItem,CompanyOrderPayInfo



# Register your models here.
#from .models import Wharehouse,Storeinfo,Supplier,Goodsct,Goodsprice,Goods,Vip,Cardtype,Cardvsdi,Paymode,Srvtopty,Serviece,Servieceprice,Srvrptype,Position,Empl
#from .models import Appoption

class WifiListAdmin(admin.ModelAdmin):
    fields = ('SSID', 'BSSID', 'valiflag','storecode', 'company')
    list_display =('SSID', 'BSSID', 'valiflag','storecode', 'company')

admin.site.register(WifiList, WifiListAdmin)


# class CompanyItemAdmin(admin.ModelAdmin):
#     fields = ('company_item_code', 'company_item_name', 'company_item_desc','company_item_qty', 'company_pay_period','company_item_price','companylist')
#     list_display =('company_item_code', 'company_item_name', 'company_item_desc','company_item_qty', 'company_pay_period','company_item_price','companylist')
#
# admin.site.register(CompanyItem, CompanyItemAdmin)

