
# Register your models here.

from django.contrib import admin
from django import forms
import xadmin
from jmj.models import ReportPeriod,PeriodData, OldData,GcodeMirror
from baseinfo.models import Goods


# Register your models here.
#from .models import Wharehouse,Storeinfo,Supplier,Goodsct,Goodsprice,Goods,Vip,Cardtype,Cardvsdi,Paymode,Srvtopty,Serviece,Servieceprice,Srvrptype,Position,Empl
#from .models import Appoption

#from .models import *

#class EnactmenAdmin(admin.ModelAdmin):
#    model = Enactmen

#admin.site.register(Enactmen,EnactmenAdmin)

class ReportPeriodAdmin(admin.ModelAdmin):
    fields = ('reportyear', 'reportname', 'period','perioddesc', 'fromdate','todate')
    list_display = ('reportyear', 'reportname','period','perioddesc', 'fromdate','todate')
    list_filter =  ('reportyear','reportname','period','perioddesc')

admin.site.register(ReportPeriod, ReportPeriodAdmin)

class PeriodDataAdmin(admin.ModelAdmin):
    fields = ('reportperiod', 'storecode', 'gcode', 'costprice','price','iqty','tiqty','toqty','thisperiodsalesqty','thisperiodsalesamount','totalsalesqty','totalsalesamount','stockqty','salespercent')
    list_display =('reportperiod', 'storecode', 'gcode', 'costprice','price','iqty','tiqty','toqty','thisperiodsalesqty','thisperiodsalesamount','totalsalesqty','totalsalesamount','stockqty','salespercent')


admin.site.register(PeriodData, PeriodDataAdmin)


class OldDataAdmin(admin.ModelAdmin):
    fields = ('storecode', 'saleatr', 'vsdate', 'gcode','salesqty','salesamount')
    list_display =  ('storecode', 'saleatr', 'vsdate', 'gcode','salesqty','salesamount')
    list_filter =  ('storecode','vsdate','gcode')

    def get_queryset(self, request):
        qs = OldData.objects.filter(saleatr='I')
        return qs

admin.site.register(OldData, OldDataAdmin)


class GcodeMirrorAdmin(admin.ModelAdmin):
    fields = ('gcode','gname','gcode2018','gcode2017','gcode2016','gcode2015','gcode2014','gcode2013','gcode2012','gcode2011','gcode2010','gcode2009','gcode2008','gcode2007','gcode2006')
    list_display =   ('gcode','gname','gcode2018','gcode2017','gcode2016','gcode2015','gcode2014','gcode2013','gcode2012','gcode2011','gcode2010','gcode2009','gcode2008','gcode2007','gcode2006')


admin.site.register(GcodeMirror, GcodeMirrorAdmin)
# class WharehouseInline(admin.TabularInline)
#     model = Wharehouse
#     fields = ('wharehousecode','wharehousename')
#     extra = 1
#
# class StoreinfoAdmin(admin.ModelAdmin):
#     fields = ('storecode','storename','dsn','precode')
#     list_display = ('storecode','storename')
#     inlines = [WharehouseInline]
#
# admin.site.register(Storeinfo,StoreinfoAdmin)

#class BrandAdmin(admin.ModelAdmin):

# #    fields = ('brandid')
# #    list_display = ()
#
# class GoodsInline(admin.StackedInline):
#     model = Goods
#     fields = (('gcode', 'gname', 'spec', 'brand', 'saleprc', 'buyprc', 'qty', 'unit', 'barcode'),
#               ( 'minivalues','maxvalues','pricechangeable', 'valiflag', 'supplierid', 'saleperc', 'pmguideperc'))
# #    fieldsets = [
# #        (None,{'fields':['gcode', 'gname', 'spec', 'brand', 'saleprc', 'buyprc', 'qty', 'unit', 'barcode']}),
# #        ('更多',{'fields':['minivalues','maxvalues','pricechangeable', 'valiflag', 'supplierid', 'saleperc', 'pmguideperc']}),
# #    ]
#     #    list_display = ('gcode','gname','brand','supplierid','ct')
#     list_filter = ('brand',)
#     search_fields = ['gcode', 'gname', 'barcode', 'brand', 'saleprc', 'buyprc', ]
#     extra = 1
#
#     def get_list_display(self, request):
#         self.list_display = ('gcode', 'gname', 'brand', 'supplierid', 'goodsct')
#         return self.list_display
#
# class SupplierAdmin(admin.ModelAdmin):
#     model = Supplier
#     fields = ('supplierid','suppliername',)
#     inlines = [GoodsInline]
# admin.site.register(Supplier,SupplierAdmin)
#
#
# class GoodsctAdmin(admin.ModelAdmin):
# #    model = Goodsct
#     fields = ['goodsct','goodsctname',]
#     list_display = ('goodsct','goodsctname')
# #    extra = 1
#     inlines = [GoodsInline]
# admin.site.register(Goodsct,GoodsctAdmin)
#
# class GoodspriceInline(admin.TabularInline):
#     model = Goodsprice
#     fields = ['qty','price','amount','commission','achievement','fromdate','todate']
#     extra = 3
#
#
# class GoodsForm(forms.ModelForm):
#     gcode = forms.CharField(label='编码',initial='pls input',max_length=16,widget=forms.TextInput(attrs={'size':'12'}))
#     gname = forms.CharField(max_length=32)
# #    spec = forms.CharField(widget=forms.TextInput())
#
#     class Meta:
#         forms.model= Goods
# #        fields =(('gcode','gname','goodsct'),('barcode','brand','supplierid'),('saleprc','buyprc','pricechangeable'),('qty','unit','spec'),('minivalues','maxvalues'),('saleperc','pmguideperc','valiflag'))
#
# class GoodsAdmin(admin.ModelAdmin):
#     fields =(('gcode','gname','goodsct'),('barcode','supplierid'),('saleprc','buyprc','pricechangeable','rptcode1'),('qty','unit','spec'),('minivalues','maxvalues'),('saleperc','pmguideperc','valiflag'))
# #    list_display = ('gcode','gname','brand','supplierid','goodsct')
#     list_filter =  ('goodsct',)
#     search_fields = ['gcode','gname','barcode','saleprc','buyprc',]
#
# #    filter_horizontal = ('goodsct',)
#     inlines = [GoodspriceInline]
#     forms = GoodsForm
#
#     def get_list_display(self, request):
#         self.list_display =  ('gcode','gname','supplierid','goodsct',)
#         return self.list_display
#
#     def save_model(self, request, obj, form, change):
#         obj.rptcode1 = self.model.objects.get(pk=obj.pk).saleprc
#         obj.save()
#
# admin.site.register(Goods,GoodsAdmin)
