#from django.contrib import admin
from django import forms
import xadmin
from xadmin import views

# Register your models here.
from .models import Wharehouse,Storeinfo,Supplier,Goodsct,Goodsprice,Goods,Vip,Cardtype,Cardvsdi,Paymode,Srvtopty,Serviece,Servieceprice,Srvrptype,Position,Empl,Vip20

#from .models import *
# class BaseSetting(object):
#     enable_themes=True
#     use_bootswatch=True
# xadmin.site.register(views.BaseAdminView,BaseSetting)

class GlobalSetting(object):
    # 设置base_site.html的Title
    site_title = '美容企业管理平台Genesis'
    # 设置base_site.html的Footer
    site_footer  = 'SHGV Co. Ltd.'
    menu_style = "accordion"

xadmin.site.register(xadmin.views.CommAdminView, GlobalSetting)

class WharehouseInline(object):
    model = Wharehouse
    fields = ('wharehousecode','wharehousename')
    extra = 1

class StoreinfoAdmin(object):
    fields = ('storecode','storename','dsn','precode')
    list_display = ('storecode','storename')
    inlines = [WharehouseInline]

xadmin.site.register(Storeinfo,StoreinfoAdmin)


# class BrandAdmin(admin.ModelAdmin):

#    fields = ('brandid')
#    list_display = ()

class GoodsInline(object):
    model = Goods
    fields = (('gcode', 'gname', 'spec', 'brand', 'saleprc', 'buyprc', 'qty', 'unit', 'barcode'),
              ('minivalues', 'maxvalues', 'pricechangeable', 'valiflag', 'supplierid', 'saleperc', 'pmguideperc'))
    #    fieldsets = [
    #        (None,{'fields':['gcode', 'gname', 'spec', 'brand', 'saleprc', 'buyprc', 'qty', 'unit', 'barcode']}),
    #        ('更多',{'fields':['minivalues','maxvalues','pricechangeable', 'valiflag', 'supplierid', 'saleperc', 'pmguideperc']}),
    #    ]
    #    list_display = ('gcode','gname','brand','supplierid','ct')
    list_filter = ('brand',)
    search_fields = ['gcode', 'gname', 'barcode', 'brand', 'saleprc', 'buyprc', ]
    extra = 1

#    def get_list_display(self, request):
#        self.list_display = ('gcode', 'gname', 'brand', 'supplierid', 'goodsct')
#        return self.list_display


class SupplierAdmin(object):
    model = Supplier
    fields = ('supplierid', 'suppliername',)
    inlines = [GoodsInline]

xadmin.site.register(Supplier, SupplierAdmin)

class GoodsctAdmin(object):
    #    model = Goodsct
    fields = ['goodsct', 'goodsctname', ]
    list_display = ('goodsct', 'goodsctname')
    #    extra = 1
    inlines = [GoodsInline]

xadmin.site.register(Goodsct, GoodsctAdmin)

class GoodspriceInline(object):
    model = Goodsprice
    fields = ['qty', 'price', 'amount', 'commission', 'achievement', 'fromdate', 'todate']
    extra = 3

class GoodsForm(object):
    gcode = forms.CharField(label='编码', initial='pls input', max_length=16,
                            widget=forms.TextInput(attrs={'size': '12'}))
    gname = forms.CharField(max_length=32)

    #    spec = forms.CharField(widget=forms.TextInput())

    class Meta:
        forms.model = Goods


# fields =(('gcode','gname','goodsct'),('barcode','brand','supplierid'),('saleprc','buyprc','pricechangeable'),('qty','unit','spec'),('minivalues','maxvalues'),('saleperc','pmguideperc','valiflag'))

class GoodsAdmin(object):
    fields = (
    ('gcode', 'gname', 'goodsct'), ('barcode',  'supplierid'), ('saleprc', 'buyprc', 'pricechangeable'),
    ('qty', 'unit', 'spec'), ('minivalues', 'maxvalues'), ('saleperc', 'pmguideperc', 'valiflag'))
    #    list_display = ('gcode','gname','brand','supplierid','goodsct')
    list_filter = ('brand',)
    search_fields = ['gcode', 'gname', 'barcode',  'saleprc', 'buyprc', ]

    #    filter_horizontal = ('goodsct',)
    inlines = [GoodspriceInline]
 #   forms = GoodsForm

    # def get_list_display(self, request):
    #     self.list_display = ('gcode', 'gname',  'supplierid', 'goodsct',)
    #     return self.list_display


xadmin.site.register(Goods, GoodsAdmin)


class SrvrptypeAdmin(object):
    fields = ['srvrptypecode', 'srvrptypename']
    list_display = ('srvrptypecode', 'srvrptypename')


xadmin.site.register(Srvrptype, SrvrptypeAdmin)


class SrvrptypeInline(object):
    model = Srvrptype
    fileds = ('srvrptypename')
    extra = 1


class ServiecepirceInline(object):
    model = Servieceprice
    fileds = ('qty', 'price', 'amount', 'commission', 'achievement', 'fromdate', 'todate')
    extra = 1


class ServieceInline(object):
    model = Serviece
    #    fields = (('svrcdoe','svrname','svrprc','saleflag','topcode'),('srvrptypecode','stdmins'),('pperc','scperc','thprec'))
    fieldsets = [
        (None, {'fields': [('svrcdoe', 'svrname', 'svrprc', 'saleflag'), 'topcode','tag']}),
        ('提成', {'fields': [('pperc', 'scperc', 'thprec'), ('srvrptypecode', 'stdmins', 'pricechangeable')]}),
        #        ('管理',{'fields':['srvrptypecode','stdmins','pricechangeable','valiflag','intervalday']}),
    ]
    extra = 1
    inlines = [ServiecepirceInline]
    search_fields = ['svrcdoe', 'svrname']


# radio_fields={"topcode":admin.VERTICAL}

class SrvtoptyAdmin(object):
    fields = ('topcode', 'ttname',)
    list_display = ('topcode', 'ttname',)
    prepopulated_fields = {'ttname': ('topcode',)}
    inlines = [ServieceInline]


xadmin.site.register(Srvtopty, SrvtoptyAdmin)


class SrvtoptyInline(object):
    model = 'Srvtopty'
    fields = ['topcode', 'ttname']
    extra = 5


class ServieceAdmin(object):
    fieldsets = [
        (None, {'fields': [('svrcdoe', 'svrname', 'svrprc', 'saleflag'), 'topcode']}),
        ('提成', {'fields': [('pperc', 'scperc', 'thprec'), ('srvrptypecode', 'stdmins', 'pricechangeable')]}),
        #        ('管理',{'fields':['srvrptypecode','stdmins','pricechangeable','valiflag','intervalday']}),
    ]
    list_display = ('svrcdoe', 'svrname', 'svrprc', 'saleflag', 'topcode',)
    inlines = [ServiecepirceInline]
    search_fields = ['svrcdoe', 'svrname']


xadmin.site.register(Serviece, ServieceAdmin)


class CardvsdiInline(object):
    model = Cardvsdi
    fields = ('topcode', 'cardvsdisc', 'flag', 'guideperc')
    inlines = [SrvtoptyInline]
    extra = 1


class CardtypeForm(forms.ModelForm):
    cardtype = forms.CharField(initial='')
    cardname = forms.CharField(initial='cardtype name')
    cardnote = forms.CharField(initial=0)

    class Meta:
        forms.model = Cardtype


class CardtypeAdmin(object):
    fields = (('cardtype', 'cardname', 'oriprice', 'leftmoney', 'salesflag', 'comptype'), 'cardnote')
    order_field = ('cardtype')
    #    form = CardtypeForm
    list_display = ('cardtype', 'cardname', 'cardnote')
    inlines = [CardvsdiInline]


xadmin.site.register(Cardtype, CardtypeAdmin)


class PaymodeAdmin(object):
    fieldsets = [
        (None, {'fields': ['pcode', 'pname']}),
        ('Advance Information', {'fields': ['iscash', 'currency', 'rate', 'guideperc'], 'classes': ['collapse']}),
    ]
    list_display = ('pcode', 'pname', 'iscash')

xadmin.site.register(Paymode, PaymodeAdmin)


class VipAdmin(object):
    # def preview(self, obj):
    #     #       return u'<img src="'+self.%s" height="256",width="256" />'
    #     return u'<img src="/%s" height="64",width="64" >' % (obj.photofile)
    #
    # preview.allow_tags = True
    # preview.short_description = u'photofile'
    fields =('viptype','vname','vcode','mtcode','source','sex','ecode','ecode2','birth')
    # fieldsets = [
    #     (None, {'fields': ['vcode', 'vname', 'mtcode', 'photofile', ]}),
    #     ('Advance Information', {'fields': ['telph', 'addr', 'birth', 'qq', 'wechat', 'weibo', 'email', 'indate'],
    #                              'classes': ['wide', 'extrapretty']}),
    # ]

    list_display = ['viptype','vname','mtcode','vcode','source','sex','ecode','ecode2','birth','create_time',]
    search_fields = ['viptype','sex','vcode','vname','mtcode','source','ecode','ecode2','birth','create_time',]
    ordering = ['viptype','vcode',]
    relfield_style ='fk-ajax'

# readonly_fields = ('preview',)
   # exclude = ('image file',)

xadmin.site.register(Vip,VipAdmin )

class Vip20Admin(object):
    fields = ('viptype','vname','vcode','mtcode','source','sex','ecode','ecode2','birth')
    list_display = ['viptype', 'vname', 'mtcode', 'vcode', 'source', 'sex', 'ecode',  'create_time', ]
    search_fields = ['viptype', 'sex', 'vcode', 'vname', 'mtcode', 'source', 'ecode', 'create_time', ]
    ordering = ['viptype', 'vcode', ]
    relfield_style = 'fk-ajax'

    def queryset(self, request):
        qs = super(VipAdmin, self).get_queryset(request).filter(viptype='20')
        # qs = qs.filter( viptype = '散客')
        return qs

xadmin.site.register(Vip20,VipAdmin )

class EmplInline(object):
    model = Empl
    fields = ('ecode', 'ename', 'indate', 'cmtcode', 'status', 'emplpwd', 'photofile')
    extra = 1

class PositionAdmin(object):
    fields = ('positioncode', 'positiondesc', 'bookingflag')
    list_display = ['positioncode', 'positiondesc', 'bookingflag']
    inlines = [EmplInline]

xadmin.site.register(Position, PositionAdmin)

