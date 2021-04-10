#coding = utf-8

from django.contrib import admin
from django import forms
import xadmin
from django.utils.translation import ugettext_lazy as _

# Register your models here.
from .models import Tags,VipTags,Wharehouse, Storeinfo, Supplier, Goodsct, Goodsprice, Goods, Vip,Cardsupertype, Cardtype, Cardvsdi, Paymode, Srvtopty, Serviece, Servieceprice, Srvrptype, Position, Empl
from .models import Appoption,Promotions,Promotionsdetail,ArchivementRuler,BankAccount
import common.constants
from goods.models import Serviecegoods,GoodsTransHead,GoodsTransDetail

# from .models import *
admin.site.site_header = 'Genesis美容企业管理平台'
admin.site.site_title  = '上海大谷'
# class EnactmenAdmin(admin.ModelAdmin):
#    model = Enactmen

COMPANY = common.constants.COMPANYID

companylist ={
    'xuedan':'xuedan',
    'yiren':'yiren',
    'yfy':'yfy',
    'youlan':'youlan',
    'toby':'dsdemo',
    'demo':'demo',
    'dsdemo':'dsdemo',
}

COMPANYGROUP1=['yfy','yiren','demo']
COMPANYGROUP2=['xuedan','dsdemo']

class BrandListFilter(admin.SimpleListFilter):
    title = _(u'品牌')
    parameter_name = 'brand'
    def lookups(self, request, model_admin):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        print('COMPANY',COMPANY)
        # COMPANY='dsdemo'
        brandlist = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list(
            'itemname', 'itemvalues')
        print('brandlist',brandlist)
        return brandlist
        # return ()

    def queryset(self, request, queryset):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        # COMPANY='dsdemo'
        brand = self.value()
        print('queryset brand', brand)
        if brand == None:
            return queryset.filter(company=COMPANY)
        else:
            return queryset.filter(company=COMPANY,brand=brand)

class Displayclass1ListFilter(admin.SimpleListFilter):
    title = _(u'显示分类一')
    parameter_name = 'displayclass1'
    def lookups(self, request, model_admin):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        PARAM = 'displayclass1'
        # brandlist = Appoption.objects.filter(company=COMPANY, flag='Y', seg= parameter_name ).values_list(
        #     'itemname', 'itemvalues')
        return Appoption.objects.filter(company=COMPANY, flag='Y', seg= PARAM ).values_list(
            'itemname', 'itemvalues')
        # return ()

    def queryset(self, request, queryset):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        param = self.value()

        if param == None:
            return queryset.filter(company=COMPANY)
        else:
            return queryset.filter(company=COMPANY, displayclass1=param)

class Displayclass2ListFilter(admin.SimpleListFilter):
        title = _(u'显示分类二')
        parameter_name = 'displayclass2'

        def lookups(self, request, model_admin):
            # qs = super().get_queryset(request)
            currentuser = request.user._wrapped.username
            COMPANY = companylist[currentuser]
            PARAM = 'displayclass2'
            # brandlist = Appoption.objects.filter(company=COMPANY, flag='Y', seg= parameter_name ).values_list(
            #     'itemname', 'itemvalues')
            return Appoption.objects.filter(company=COMPANY, flag='Y', seg=PARAM).values_list(
                'itemname', 'itemvalues')
            # return ()

        def queryset(self, request, queryset):
            currentuser = request.user._wrapped.username
            COMPANY = companylist[currentuser]
            param = self.value()

            if param == None:
                return queryset.filter(company=COMPANY)
            else:
                return queryset.filter(company=COMPANY, displayclass1=param)

# admin.site.register(Enactmen,EnactmenAdmin)
class AdminModel(admin.ModelAdmin):
    actions = ['export_as_excel',]
    list_per_page = 25

    # def get_changelist(self, request, **kwargs):
    #     print('kwargs:',kwargs)
    #     qs = super().get_queryset(request)
    #     currentuser = request.user._wrapped.username
    #     COMPANY = companylist[currentuser]
    #     BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list(
    #         'itemname', 'itemvalues')
    #     return BRAND

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
        return qs.filter(flag='Y',company=COMPANY)

    def save_model(self, request, obj, form, change):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        obj.company = COMPANY
        obj.creater = currentuser
        obj.save()

    def export_as_excel(self,request):
        qs = self.get_queryset(self,request)
        # qs.
        print('export_as_excel')

class AppoptionAdmin(AdminModel):
    model = Appoption
    fields = ('seg','itemname','itemvalues','itemvalues2')
    list_display = ('seg','itemname','itemvalues','itemvalues2')
    list_filter = ('seg',)
    list_editable = ( 'itemname', 'itemvalues','itemvalues2')
    ordering = ['seg','itemname']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        SEGS=['viplevel','tags','brand','financeclass1','financeclass2','displayclass1','displayclass2','bodyparts1','marketclass1','marketclass2','marketclass3','source','archivementclass1','archivementclass2','casetype','unit']

        # return qs.filter(flag='Y').filter(company=COMPANY).filter(seg__in=['viplevel','tags','brand','financeclass1','financeclass2','displayclass1','displayclass2','bodyparts1','marketclass1','marketclass2','marketclass3','source','archivementclass1','archivementclass2','casetype'])
        return  qs.filter(flag='Y',company=COMPANY,seg__in=SEGS)

admin.site.register(Appoption, AppoptionAdmin)

class ItemAdmin(AdminModel):
    if COMPANY in (COMPANYGROUP1):
        fieldsets = [
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc')]}),
            ('管理', {'fields': ['storelist', 'displayclass1', 'displayclass2', 'marketclass1', 'marketclass2','pricechangeable', 'saleflag', 'valiflag']}),
            ('标签', {'fields': ['tags']})
        ]
    if COMPANY in (COMPANYGROUP2):
        fieldsets = [
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc')]}),
            ('管理', {'fields': ['storelist', 'displayclass1', 'displayclass2', 'marketclass1', 'pricechangeable', 'saleflag', 'valiflag']}),
            ('标签', {'fields': ['tags']})
        ]
    list_display=()
    list_filter = (BrandListFilter, Displayclass1ListFilter, Displayclass2ListFilter)

class TagsAdmin(admin.ModelAdmin):
    fields = ('tag',)
    list_display = ('tag',)
admin.site.register(Tags, TagsAdmin)

class VipTagsAdmin(admin.ModelAdmin):
    fields = ('tag',)
    list_display = ('tag',)
admin.site.register(VipTags, TagsAdmin)

# class WharehouseInline(admin.StackedInline):
#     model = Wharehouse
#     fields = ('wharehousecode', 'wharehousename')
#     extra = 1

# class StoreinfoAdmin(admin.ModelAdmin):
class StoreinfoAdmin(AdminModel):
    fields = ('storecode', 'storename','dsn', 'precode','rooms','measureofarea','pmcodes','seccodes','validyvipcnt')
    list_display = ('storecode', 'storename')
    # inlines = [WharehouseInline]

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     # if request.user.is_superuser:
    #     #     return qs
    #     return qs.filter(company=common.constants.COMPANYID)

admin.site.register(Storeinfo, StoreinfoAdmin)

class WharehouseAdmin(AdminModel):
    model = Wharehouse
    fields = ('wharehousecode','wharehousename','storecode')
    list_display = ('wharehousecode','wharehousename','storecode')
    list_editable = ('wharehousename','storecode')

admin.site.register(Wharehouse, WharehouseAdmin)

class SupplierAdmin(AdminModel):
    model = Supplier
    fields = ('supplierid', 'suppliername')
    list_display = ['supplierid', 'suppliername']
    list_editable=( 'suppliername',)
    ordering =('supplierid',)
    # inlines = [EmplInline]

admin.site.register(Supplier, SupplierAdmin)

# class BrandAdmin(admin.ModelAdmin):

#    fields = ('brandid')
#    list_display = ()

class GoodsInline(AdminModel,admin.StackedInline):
    model = Goods
    fields = (('gcode', 'gname', 'spec', 'brand', 'saleprc', 'buyprc', 'qty', 'unit', 'barcode','goodsct','supplier'),
              ('minivalues', 'maxvalues', 'pricechangeable', 'valiflag', 'supplierid', 'saleperc', 'pmguideperc'))
    list_filter = ('brand',)
    search_fields = ['gcode', 'gname', 'barcode', 'brand', 'saleprc', 'buyprc', ]
    extra = 0

    def get_list_display(self, request):
        self.list_display = ('gcode', 'gname', 'brand', 'supplierid', 'goodsct')
        return self.list_display

class GoodsctAdmin(AdminModel):
    #    model = Goodsct
    fields = ['goodsct', 'goodsctname', ]
    list_display = ('goodsct', 'goodsctname')
    #    extra = 1
    # inlines = [GoodsInline]
admin.site.register(Goodsct, GoodsctAdmin)

class GoodspriceInline(admin.TabularInline):
    model = Goodsprice
    fields = ['gcode','qty', 'price', 'amount', 'commission', 'achievement', 'fromdate', 'todate']
    extra = 0


# class GoodsForm(forms.ModelForm):
#
#     def __init__(self, *args, **kwargs):
#         super(GoodsForm, self).__init__(*args, **kwargs)
#
#         self.fields['brand'].choices = get_choices(self.instance)
#
#         if self.instance:
#             self.fields['brand'].initial = self.instance.my_text_field



    #    spec = forms.CharField(widget=forms.TextInput())

    # class Meta:
    #     forms.model = Goods

class GoodsAdmin(AdminModel,admin.ModelAdmin):
    # fields = (  ('gcode', 'gname', 'mnemoniccode','price','buyprc'),
    #             ( 'brand','saleflag','valiflag','goodsct'),
    #             ('desc1','desc2','desc3','small_image','large_image'),
    #             ('qty', 'unit', 'spec'),
    #             ('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint',
    #              'thrpoint'),
    #                 ('displayclass1','displayclass2','financeclass1','financeclass2','archivementclass1', 'archivementclass2',
    #                  'marketclass1','marketclass2','marketclass3','marketclass4'),
    #             ('storelist','saleschannels'),'tags','saleschannels')
    fieldsets = [
        ('基础信息', {'fields': [('gcode', 'gname', 'mnemoniccode', 'price', 'buyprc', 'brand'),
                             ('qty', 'unit', 'spec', 'goodsct'), ]}),
        ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint',
                            'secpoint', 'thrpoint')]}),
        ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                           'archivementclass2',
                           'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),( 'pricechangeable',
                           'saleflag', 'valiflag')]}),
        ('其他', {'fields': [('storelist', 'tags')]})
    ]
    list_display = ('gcode', 'gname', 'brand', 'displayclass1', 'saleflag', 'valiflag', 'price', 'spec')
    list_editable = ('gname', 'brand', 'displayclass1', 'saleflag', 'valiflag', 'price', 'spec')

    # if COMPANY=='yiren':
    #     list_display = ('gcode','gname','brand','qty','unit','spec','buyprc','saleflag','valiflag','price','displayclass1')
    #     list_editable = ('gname', 'brand','qty','unit','spec', 'buyprc', 'saleflag', 'valiflag', 'price','displayclass1')
    # if COMPANY =='demo':
    #     fields = (('gcode', 'gname', 'mnemoniccode', 'price', 'buyprc'),
    #               ('brand', 'saleflag', 'valiflag', 'goodsct'),
    #               ('desc1', 'desc2', 'desc3', 'small_image', 'large_image'),
    #               ('qty', 'unit', 'spec'),
    #               ('pmguideperc', 'secguideperc', 'thrguideperc'),
    #               ('discountclass','displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
    #                'archivementclass2',
    #                'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),
    #               'tags', 'saleschannels')
    #     list_display = ('gcode','gname',BrandListFilter,'displayclass1','saleflag','valiflag','price','spec')
    #     list_editable = ('gname', BrandListFilter, 'displayclass1', 'saleflag', 'valiflag', 'price', 'spec')
    # list_filter = ('brand','financeclass1','displayclass1','saleflag','valiflag',)
    list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter)
    # list_editable = ('gname','brand','displayclass1','saleflag','valiflag','price','spec')
    search_fields = ['displayclass1','brand','gcode', 'gname', 'price', 'buyprc', ]
    ordering = ('displayclass1','displayclass2','brand','gcode')

    if COMPANY in COMPANYGROUP2:
        # fields = (('gcode', 'gname', 'mnemoniccode', 'price', 'buyprc'),
        #           ('brand', 'saleflag', 'valiflag', 'goodsct'),
        #           ('qty', 'unit', 'spec'),
        #           ('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint','thrpoint'),
        #           ('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
        #            'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),
        #           ('storelist', 'saleschannels'), 'tags')
        fieldsets = [
           ('基础信息', {'fields': [('gcode', 'gname','mnemoniccode', 'price','buyprc','brand'),('qty','unit','spec', 'goodsct'),]}),
           ('提成',{'fields':[('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint','thrpoint')]}),
           ('管理',{'fields':[('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
                   'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),('pricechangeable','saleflag','valiflag')]}),
           ('其他',{'fields':[('storelist','tags')]})
        ]

        list_display = ('gcode', 'gname', 'brand', 'displayclass1', 'saleflag', 'valiflag', 'price', 'spec')
        list_editable = ('gname', 'brand', 'displayclass1', 'saleflag', 'valiflag', 'price', 'spec')

    # filter_horizontal = ('brand',)
    inlines = [GoodspriceInline]
    # forms = GoodsForm
    actions = ['to_excel',]

admin.site.register(Goods, GoodsAdmin)

class SrvrptypeAdmin(AdminModel):
    fields = ['srvrptypecode', 'srvrptypename']
    list_display = ('srvrptypecode', 'srvrptypename')


admin.site.register(Srvrptype, SrvrptypeAdmin)

class SrvrptypeInline(admin.TabularInline):
    model = Srvrptype
    fileds = ('srvrptypename')
    extra = 1

#
# class ServiecepriceInline(admin.TabularInline):
#     model = Servieceprice
#     fileds = ('qty', 'price', 'amount', 'commission', 'achievement', 'fromdate', 'todate')
#     list_display =  ('qty', 'price', 'amount', 'commission', 'achievement', 'fromdate', 'todate')
#     exclude =['creater','uuid']
#     extra = 1
#
#     def amount(self, instance):
#         return instance.qty * instance.price
#
#     amount.short_descrition = '可消费金额'
#     amount.is_column = True
#     amount.allow_tags = True

class ServiecegoodsInline(admin.TabularInline):
    model = Serviecegoods
    fields = ('goodsuuid','qty')
    list_display=('qty',)
    raw_id_fields=['goodsuuid']
    exclude =['creater','uuid']
    extra = 1

class ServiecepriceInline(admin.TabularInline):
    model = Servieceprice
    fields = ('srvcode','qty','price','amount','saleflag','stype')
    list_display=('srvcode','qty','price','amount','saleflag')
    exclude =['creater','uuid']
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
        return qs.filter(flag='Y',company=COMPANY)

class ServieceInline(admin.StackedInline):
    model = Serviece
    #    fields = ('svrcdoe','svrname','svrprc','saleflag','topcode','srvrptypecode','stdmins','pperc','scperc','thprec')
    fieldsets = [
        (None, {'fields': [('svrcdoe', 'svrname', 'svrprc', 'saleflag'), 'topcode']}),
        ('提成', {'fields': [('pperc', 'scperc', 'thprec'), ('srvrptypecode', 'stdmins', 'pricechangeable')]}),
        #        ('管理',{'fields':['srvrptypecode','stdmins','pricechangeable','valiflag','intervalday']}),

    ]
    extra = 1
    inlines = [ServiecepriceInline ]
    search_fields = ['svrcdoe', 'svrname']


# radio_fields={"topcode":admin.VERTICAL}

class SrvtoptyAdmin(AdminModel):
    fields = ('topcode', 'ttname',)
    list_display = ('topcode', 'ttname',)
    prepopulated_fields = {'ttname': ('topcode',)}
    # inlines = [ServieceInline]


admin.site.register(Srvtopty, SrvtoptyAdmin)


class SrvtoptyInline(admin.TabularInline):
    model = 'Srvtopty'
    fields = ['topcode', 'ttname']
    extra = 5



class ServieceAdmin(AdminModel):
    fieldsets = [
         (None, {'fields': [('svrcdoe', 'svrname',  'price'),('qty','stdmins','intervalday','srvrptypecode', 'topcode'),]}),
         ('提成',{'fields':[ ('pmguideperc', 'secguideperc', 'thrguideperc','secpoint'),]}),
         ('管理',{'fields':['storelist','displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4','after_sales_scheme','pricechangeable','saleflag','valiflag']}),
         ('标签',{'fields':['tags']})
     ]
    #fieldsets = [
    #    (None, {'fields': [('svrcdoe', 'svrname',  'price'),('qty','stdmins','intervalday','srvrptypecode', 'topcode'),]}),
    #    ('提成',{'fields':[('pmguideperc', 'secguideperc', 'thrguideperc')]}),
    #    ('管理',{'fields':['storelist','displayclass1', 'displayclass2','marketclass1', 'marketclass2','pricechangeable','saleflag','valiflag']}),
    #    ('标签',{'fields':['tags']})
    #]
    list_display = ('svrcdoe', 'svrname','brand','saleflag','valiflag' ,'displayclass1','displayclass2', 'price')
    inlines = [ServiecepriceInline,ServiecegoodsInline]
    search_fields = ['displayclass1','displayclass2','qty','stdmins','brand','mnemoniccode','svrcdoe', 'svrname']

    list_filter = (BrandListFilter, 'displayclass1', 'displayclass2','qty','stdmins', 'topcode', 'saleflag', 'valiflag')
    list_per_page = 25
    list_editable = ('svrname','price','saleflag','valiflag','displayclass1','displayclass2',)
    # date_hierarchy = 'create_time'
    ordering = ('displayclass1','displayclass2','brand','svrcdoe',)
    # list_filter = (BrandListFilter,)
    # yfy
    if COMPANY=='yfy':
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'topcode','saleflag','valiflag')
    # 伊人
    if COMPANY=='yiren':
        list_display = (
        'svrcdoe', 'svrname', 'brand', 'qty', 'stdmins', 'saleflag', 'valiflag', 'displayclass1', 'displayclass2',
        'price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','qty','topcode','saleflag','valiflag')
    # list_filter = (BrandListFilter,)

    if COMPANY in COMPANYGROUP1:
        fieldsets = [
            ('基本信息', {'fields': [('svrcdoe', 'svrname', 'price'),
                               ('qty', 'stdmins', 'intervalday', 'topcode'), ]}),
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc','pmperc','secperc','thrperc','pmpoint','secpoint','thrpoint')]}),
            ('管理信息', {'fields': [( 'displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4',
                               'pricechangeable', 'saleflag', 'valiflag')]}),
            ('标签', {'fields': [('tags','storelist')]})
        ]
        list_display = ( 'svrcdoe', 'svrname', 'brand', 'saleflag', 'valiflag', 'displayclass1', 'displayclass2', 'price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','topcode','saleflag','valiflag')
        list_per_page = 25
        list_editable = ('svrname','price','brand','saleflag','valiflag','displayclass1','displayclass2',)
        inlines = [ServiecepriceInline, ServiecegoodsInline]
        # date_hierarchy = 'create_time'
        ordering = ('brand','displayclass1','displayclass2','svrcdoe',)


    if COMPANY in COMPANYGROUP2:
        fieldsets = [
            ('基本信息', {'fields': [('svrcdoe', 'svrname', 'price'),
                               ('qty', 'stdmins', 'intervalday', 'topcode'), ]}),
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc','pmperc','secperc','thrperc','pmpoint','secpoint','thrpoint')]}),
            ('管理信息', {'fields': [( 'displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4',
                               'pricechangeable', 'saleflag', 'valiflag')]}),
            ('其他', {'fields': [('storelist','tags')]})
        ]
        list_display = ( 'svrcdoe', 'svrname', 'brand', 'saleflag', 'valiflag', 'displayclass1', 'displayclass2', 'price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','topcode','saleflag','valiflag')
        list_per_page = 25
        list_editable = ('svrname','price','brand','saleflag','valiflag','displayclass1','displayclass2',)
        inlines = [ServiecepriceInline, ServiecegoodsInline]
        # date_hierarchy = 'create_time'
        ordering = ('brand','displayclass1','displayclass2','svrcdoe',)


admin.site.register(Serviece, ServieceAdmin)

class CardvsdiInline(admin.TabularInline):
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

class CardsupertypeAdmin(AdminModel):
    fields = ('code', 'name', 'pcode', 'normal_pcode','present_pcode')
    list_display = ('code', 'name',  'normal_pcode','present_pcode')
    list_editable=('name',  'normal_pcode','present_pcode',)
    ordering = ('code',)


admin.site.register(Cardsupertype, CardsupertypeAdmin)


class CardtypeAdmin(AdminModel):
    # fields = ( ('cardtype', 'cardname', 'mnemoniccode','price', 'leftmoney', 'saleflag','valdatetype','validays', 'comptype'),
    #            # ('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint', 'thrpoint'),
    #            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc',
    #                                'pmpoint', 'secpoint', 'thrpoint')]}),
    #            'suptype','brand','displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2', 'cardnote')

    fieldsets = [
        ('基础信息', {'fields': [('suptype','comptype'),('cardtype', 'cardname', 'mnemoniccode', 'price', 'leftmoney', 'brand'),
                             ('valdatetype', 'validays','cardnote') ]}),
        ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint',
                            'secpoint', 'thrpoint')]}),
        ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                           'archivementclass2',
                           'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),( 'pricechangeable',
                           'saleflag', 'valiflag')]}),
        ('其他', {'fields': [('storelist', 'tags')]})
    ]

    order_field = ('suptype','displayclass1','brand','displayclass2','cardtype')
    #    form = CardtypeForm
    list_display = ('cardtype', 'cardname','suptype','displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2','rptcode6','saleflag','price','brand')
    inlines = [CardvsdiInline]

    search_fields = ['mnemoniccode','cardtype', 'cardname']
    list_filter = ('suptype','displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2',)
    list_per_page = 25
    list_editable = ('displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2','rptcode6','saleflag','brand',)
    # date_hierarchy = 'create_time'
    ordering = ('suptype','brand','cardtype',)

    if COMPANY in COMPANYGROUP1:
        # fields = ( ('cardtype', 'cardname', 'price','mnemoniccode', 'leftmoney', 'saleflag', 'valdatetype', 'validays', 'comptype'),
        #           ('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint',
        #            'thrpoint'),
        #            'suptype', 'brand', 'displayclass1', 'displayclass2', 'marketclass1', 'marketclass2', 'marketclass3',
        #            'marketclass4', 'financeclass1', 'financeclass2',
        #           'cardnote')
        fieldsets = [
            ('基础信息', {'fields': [('suptype', 'cardtype', 'cardname', 'mnemoniccode', 'price', 'leftmoney', 'brand'),
                                 ('valdatetype', 'validays', 'comptype', 'cardnote')]}),
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint',
                               'secpoint', 'thrpoint')]}),
            ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                                'archivementclass2','marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),
                               ('pricechangeable', 'saleflag', 'valiflag')]}),
            ('其他', {'fields': [('storelist', 'tags')]})
        ]
        list_display = ('cardtype', 'cardname','suptype','displayclass1','displayclass2','saleflag','price','brand')
        list_filter = ('suptype','displayclass1','displayclass2',)
        list_editable = ( 'displayclass1', 'displayclass2', 'saleflag', 'brand',)

    if COMPANY in COMPANYGROUP2:
        fieldsets = [('基础信息', {'fields': [('suptype', 'comptype'),('cardtype', 'cardname', 'mnemoniccode', 'price', 'leftmoney', 'brand'),
                                 ('valdatetype', 'validays', 'cardnote')]}),
                        ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint','secpoint', 'thrpoint')]}),
                        ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                                            'archivementclass2','marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),
                                           ('pricechangeable', 'saleflag', 'valiflag')]}),
                        ('其他', {'fields': [('storelist', 'tags')]})
                    ]
        list_display = ('cardtype', 'cardname','suptype','displayclass1','displayclass2','saleflag','price','brand')
        list_filter = ('suptype','displayclass1','displayclass2',)
        list_editable = ('cardname', 'displayclass1', 'displayclass2', 'saleflag', 'brand',)

admin.site.register(Cardtype, CardtypeAdmin)


class PaymodeAdmin(AdminModel):
    fieldsets = [
        (None, {'fields': ['pcode', 'pname']}),
        ('Advance Information', {'fields': ['iscash', 'currency', 'rate', 'guideperc'], 'classes': ['collapse']}),
    ]
    list_display = ('pcode', 'pname', 'iscash')


admin.site.register(Paymode, PaymodeAdmin)


#
# class VipAdmin(admin.ModelAdmin):
#     def preview(self,obj):
#  #       return u'<img src="'+self.%s" height="256",width="256" />'
#         return u'<img src="/%s" height="64",width="64" >' % (obj.photofile)
#     preview.allow_tags = True
#     preview.short_description = u'photofile'
#
#     fieldsets=[
#         (None,  {'fields':['vcode','vname','mtcode','photofile',]}),
#         ('Advance Information',{'fields':['telph','addr','birth','qq','wechat','weibo','email','indate'],'classes':['wide','extrapretty']}),
#         ]
#
#     list_display=('vcode','vname','mtcode','preview')
#     search_fields=('vcode','vname','mtcode',)
#     ordering = ['vcode']
#
# #    readonly_fields = ('preview',)
# #    exclude = ('image file',)
#
# admin.site.register(Vip,VipAdmin)

class EmplInline(admin.TabularInline):
    model = Empl
    fields = ('ecode', 'ename', 'indate', 'cmtcode', 'status', 'emplpwd', 'photofile')
    extra = 1


class PositionAdmin(AdminModel):
    fields = ('positioncode', 'positiondesc', 'bookingflag')
    list_display = ['positioncode', 'positiondesc', 'bookingflag']
    # inlines = [EmplInline]

admin.site.register(Position, PositionAdmin)



#
# class StockdetailInline(admin.TabularInline):
#     model = Stockdetail
#     fields = ('gcode','qty')
# #    filter_horizontal = ('gcode',)
#     filter=('gcode','gname')
#     extra = 1
#
# class StockmstAdmin(admin.ModelAdmin):
#     fields =(('storecode','wharehousecode','stockdate','ecode','doccode'),'note')
#     ordering = ['stockdate']
#     list_display = ('storecode','wharehousecode','stockdate','ecode','doccode')
#     inlines = [StockdetailInline]
#
# admin.site.register(Stockmst,StockmstAdmin)

class PromotionsdetailInline(admin.TabularInline):
    model = Promotionsdetail
    fields = ('ttype','sgcode', 's_qty', 's_price', 's_amount', 'custperc', 'emplperc')
    extra = 1

    def get_sgcname(self,object):
        ttype=self.ttype

    def set_sgcode(self,object):
        if self.ttype == 'S':
            SGCODE = Serviece.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('svrcdoe',
                                                                                                       'svrname')
        if self.ttype == 'G':
            SGCODE = Goods.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('gcode', 'gname')
        if self.ttype == 'C':
            SGCODE = Cardtype.objects.filter(company=common.constants.COMPANYID, flag='Y').values_list('cardtype',
                                                                                                       'cardname')

        return SGCODE


class PromotionsAdmin(AdminModel):
    fields = ('promotionsid', 'promotionsname', 'mainttype')
    list_display = ['promotionsid', 'promotionsname', 'mainttype']
    inlines = [PromotionsdetailInline]

admin.site.register(Promotions, PromotionsAdmin)



class EmplAdmin(AdminModel):
    fields =( ('ecode', 'ename','position','storecode','indate','cmtcode','status','team'),'storelist')
    list_display = ['ecode', 'ename','storecode','position','status','team']
    list_filter = ('storecode','position','status')
    list_editable =  ( 'ename', 'position','storecode','status','team')

admin.site.register(Empl, EmplAdmin)

class ArchivementRulerAdmin(AdminModel):
    fields = ( 'storecode','archivementclass1','position','basenumtype','frombasenum','tobasenum','tichengperc','tichengbase')
    list_display = ['storecode','archivementclass1', 'position','basenumtype','frombasenum','tobasenum','tichengperc','tichengbase']
    list_filter = ('storecode','archivementclass1','position','basenumtype')
    list_editable =  ( 'position','basenumtype','frombasenum','tobasenum','tichengperc','tichengbase')

admin.site.register(ArchivementRuler, ArchivementRulerAdmin)

class BankAccountAdmin(AdminModel):
    fields = ( 'accountcode','accountname','bankname','accountnumber','accountdesc','status','storelist')
    list_display = [ 'accountcode','accountname','bankname','accountnumber','accountdesc','status','storelist']
    list_filter = ('status','status','bankname')
    list_editable =  ( 'accountname','bankname','accountnumber','accountdesc','status','storelist')

admin.site.register(BankAccount, BankAccountAdmin)

# class GoodsTransDetailInline(admin.TabularInline):
#     model = GoodsTransDetail
#
#     fields = ('ditem','gcode', 'goodsvaldate', 'qty', 'price', 'amount')
#     extra = 1
#
#     # if request.user.is_superuser:
#     def changelist_view(self, request, extra_context=None):
#         user = request.user
#
#         if user.is_superuser:
#             self.list_display = ['ditem','gcode', 'goodsvaldate', 'qty', 'price', 'amount']
#         else:
#             self.list_display = ['ditem','gcode', 'goodsvaldate', 'qty', 'price']
#         return super(GoodsTransDetailInline, self).changelist_view(request, extra_context=None)
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         # if request.user.is_superuser:
#         #     return qs
#
#         return qs.filter(flag='Y').filter(company=common.constants.COMPANYID)
#
#
#
#
# class GoodsTransHeadAdmin(AdminModel):
#     fields = ('vsdate', 'whcode', 'doccode','ecode')
#     list_display = ['vsdate', 'whcode', 'doccode','ecode']
#     inlines = [GoodsTransDetailInline]
#
# admin.site.register(GoodsTransHead, GoodsTransHeadAdmin)
