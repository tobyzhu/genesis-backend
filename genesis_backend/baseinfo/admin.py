#coding = utf-8
from django.contrib import admin
from django import forms
# import xadmin
from django.utils.translation import ugettext_lazy as _
from datetime import datetime,timedelta
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from django.contrib import messages

from common.admin_excel import modeladmin_export_xlsx

# Register your models here.
from .models import Tags,VipTags,Wharehouse, Storeinfo, Supplier, Goodsct, Goodsprice, Goods, Vip,Cardsupertype, Cardtype, Cardvsdi, Paymode, Srvtopty, Serviece, Servieceprice, Srvrptype, Position, Empl
from .models import (
    Serviecegoods,
    Appoption,
    ItemModel,
    ITEM_APPOPTION_FIELD_NAMES,
    SEGS,
    Promotions,
    Promotionsdetail,
    ArchivementRuler,
    BankAccount,
    Team,
)

_ITEM_APPOPTION_FIELDS_F = frozenset(ITEM_APPOPTION_FIELD_NAMES)
import common.constants
from common.admin_utils import (
    get_admin_company,
    get_admin_username,
    GenesisCompanyAdminMixin,
    GenesisCompanyInlineMixin,
    COMPANYGROUP1,
    COMPANYGROUP2,
)
# from .forms import GoodsForm

# from .models import *
admin.site.site_header = 'Genesis美容企业管理平台'
admin.site.site_title  = '上海大谷'
# class EnactmenAdmin(admin.ModelAdmin):
#    model = Enactmen

COMPANY = common.constants.COMPANYID

# companylist 已废弃：请用 get_admin_company(request)（基于 Django User + GenesisUserProfile）

class BrandListFilter(admin.SimpleListFilter):
    title = _(u'品牌')
    parameter_name = 'brand'
    def lookups(self, request, model_admin):
        # qs = super().get_queryset(request)
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        print('COMPANY',COMPANY)
        # COMPANY='dsdemo'
        brandlist = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list(
            'itemname', 'itemvalues')
        print('brandlist',brandlist)
        return brandlist
        # return ()

    def queryset(self, request, queryset):
        # qs = super().get_queryset(request)
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        # COMPANY='dsdemo'
        brand = self.value()
        print('queryset brand', brand)
        if brand == None:
            return queryset.filter(company=COMPANY)
        else:
            return queryset.filter(company=COMPANY,brand=brand)

def _appoption_display_lookups(company: str, model_admin, slot: int):
    """列表筛选：与 ItemModel 一致，优先专用 seg（srv/goods/cardtype），无数据则回退 displayclass1/2。"""
    mn = model_admin.model._meta.model_name
    fb = "displayclass1" if slot == 1 else "displayclass2"
    seg = ItemModel.specialized_appoption_seg(mn, fb)
    qs = Appoption.objects.filter(company=company, flag="Y", seg=seg)
    if seg != fb and not qs.exists():
        qs = Appoption.objects.filter(company=company, flag="Y", seg=fb)
    return qs.values_list("itemname", "itemvalues")


class Displayclass1ListFilter(admin.SimpleListFilter):
    title = _(u'显示分类一')
    parameter_name = 'displayclass1'

    def lookups(self, request, model_admin):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        return _appoption_display_lookups(COMPANY, model_admin, 1)

    def queryset(self, request, queryset):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        param = self.value()

        if param == None:
            return queryset.filter(company=COMPANY)
        else:
            return queryset.filter(company=COMPANY, displayclass1=param)

class Displayclass2ListFilter(admin.SimpleListFilter):
    title = _(u'显示分类二')
    parameter_name = 'displayclass2'

    def lookups(self, request, model_admin):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        return _appoption_display_lookups(COMPANY, model_admin, 2)

    def queryset(self, request, queryset):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        param = self.value()

        if param == None:
            return queryset.filter(company=COMPANY)
        else:
            return queryset.filter(company=COMPANY, displayclass2=param)

# admin.site.register(Enactmen,EnactmenAdmin)
class AdminModel(GenesisCompanyAdminMixin, admin.ModelAdmin):
    actions = ['export_as_excel',]
    # list_per_page = 25
    # 列表页每页展示的条数
    list_per_page = 100
    # 分页,显示全部,真是数据小于该值时才会显示全部
    list_max_show_all = 200

    def export_as_excel(self, request, queryset):
        """
        将列表页勾选的行导出为 .xlsx（列与 list_display 一致，含仅 Admin 上定义的方法列）。
        """
        if not queryset.exists():
            self.message_user(
                request, "请先在列表中勾选要导出的记录。", level=messages.WARNING
            )
            return None
        return modeladmin_export_xlsx(self, request, queryset)

    export_as_excel.short_description = "导出为 Excel (xlsx)"

    # def save_related(self, request, form, formsets, change):
    #     obj = form.instance
    #     currentuser = request.user._wrapped.username
    #     COMPANY = get_admin_company(request)
    #     obj.company=COMPANY
    #     # obj.save()
    #     print(' save_related',COMPANY,obj)
    #     # self.company=COMPANY
    #     # self.save()
    #     super().save_related(request, form, formsets, change)


class AdminInlineModel(GenesisCompanyInlineMixin, admin.TabularInline):
    pass


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
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        allowed = [x[0] for x in SEGS]
        return qs.filter(flag='Y', company=COMPANY, seg__in=allowed)

admin.site.register(Appoption, AppoptionAdmin)

class ItemAdmin(AdminModel):
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        if db_field.name in _ITEM_APPOPTION_FIELDS_F:
            seg = ItemModel.specialized_appoption_seg(self.model._meta.model_name, db_field.name)
            qs = Appoption.objects.filter(company=COMPANY, flag='Y', seg=seg)
            if seg != db_field.name and not qs.exists():
                qs = Appoption.objects.filter(company=COMPANY, flag='Y', seg=db_field.name)
            if db_field.name == 'brand' and not qs.exists():
                qs = Appoption.objects.filter(flag='Y', seg='brand')
            kwargs['choices'] = [('','')] + list(qs.values_list('itemname', 'itemvalues'))
        choose_fields =['brand','viplevel','discountclass','displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2',
                        'archivementclass1','archivementclass2','bodyparts1','bodyparts2','tags','viptags','source','storelist','goodsct','topcode','suptype']
        for field in choose_fields:
            common_choose_fields = ['brand','viplevel','discountclass','displayclass1','displayclass2','marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2',
                        'archivementclass1','archivementclass2','bodyparts1','bodyparts2','tags','viptags','source']
            for common_field in common_choose_fields:
                if db_field.name == common_field:
                    if common_field in _ITEM_APPOPTION_FIELDS_F:
                        continue
                    kwargs['choices'] =[('','')]+ list(Appoption.objects.filter(company=COMPANY, flag='Y', seg=common_field).values_list( 'itemname', 'itemvalues'))

            if db_field.name=='storelist':
                kwargs['choices'] = Storeinfo.objects.filter(company=COMPANY,flag='Y').values_list('storecode','storename')
            elif db_field.name=='goodsct':
                kwargs['choices'] = Goodsct.objects.filter(company=COMPANY, flag='Y').values_list('goodsct', 'goodsctname')
            elif db_field.name=='topcode':
                kwargs['choices'] = Srvtopty.objects.filter(company=COMPANY,flag='Y').values_list('topcode','ttname')
            elif db_field.name=='suptype':
                kwargs['choices'] =  Cardsupertype.objects.filter(company=COMPANY,flag='Y').values_list('code','name')

            # else:
            #
            #     # kwargs['choices'] =[('','')]+ list(Appoption.objects.filter(company=COMPANY, flag='Y', seg=field).values_list( 'itemname', 'itemvalues'))
            #     print('admin else',field)
        if COMPANY in COMPANYGROUP1:
            self.readonly_fields = ('qty','unit')

        if COMPANY in COMPANYGROUP2:
            self.readonly_fields=()

        return super().formfield_for_choice_field(db_field, request, **kwargs)

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
    fields = ('storecode', 'storename','salewhcode','usewhcode')
    list_display = ('storecode', 'storename')
    # inlines = [WharehouseInline]
    readonly_fields = ('salewhcode','usewhcode')
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
#     # brand = forms.ChoiceField(choices= Appoption.objects.filter(flag='Y',seg='brand').values_list('itemname','itemvalues'))
#     def __init__(self, choices,*args, **kwargs):
#         super(GoodsForm, self).__init__(*args, **kwargs)
#         # print('goodsfrom self',self)
#         # self.fields['brand'].choices = get_choices(self.instance)
#         self.fields['brand'].choices =  Appoption.objects.filter(flag='Y', seg='brand').values_list( 'itemname', 'itemvalues')
#
#         if self.instance:
#             print('self.instance',self.instance,self.data)
#             # self.fields['brand'].choices = Appoption.objects.filter(company=self.instance.company, flag='Y', seg='brand').values_list( 'itemname', 'itemvalues')
#
#
#
#     #    spec = forms.CharField(widget=forms.TextInput())
#
#     class Meta:
#         forms.model = Goods
#         fields = (
#         ('gcode', 'gname', 'goodsct'), ('barcode', 'brand', 'supplierid'), ('saleprc', 'buyprc', 'pricechangeable'),
#         ('qty', 'unit', 'spec'), ('minivalues', 'maxvalues'), ('saleperc', 'pmguideperc', 'valiflag'))


class GoodsAdmin(ItemAdmin):
    # form = GoodsForm
    list_display = ('gcode', 'gname', 'displayclass1','displayclass2', 'saleflag', 'valiflag', 'price', 'spec','qty','unit')
    list_editable = ('gname','displayclass1','displayclass2',  'saleflag', 'valiflag', 'price', 'spec',)
    list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter)
    # list_editable = ('gname','brand','displayclass1','saleflag','valiflag','price','spec')
    search_fields = ['displayclass1','brand','gcode', 'gname', 'price', 'buyprc', ]
    ordering = ('displayclass1','displayclass2','brand','gcode')

    if COMPANY in COMPANYGROUP1:
        print('COMPANY1',COMPANY)
        fieldsets = [
            ('基础信息', {'fields': [('gcode', 'gname', 'mnemoniccode', 'price', 'buyprc', 'brand'),
                                 ('qty', 'unit', 'spec', 'goodsct'), ]}),
            (
            '提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint',
                               'secpoint', 'thrpoint')]}),
            ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                                'archivementclass2',
                                'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'), ('pricechangeable',
                                                                                                  'saleflag',
                                                                                                  'valiflag')]}),
            ('其他', {'fields': [('storelist', 'tags')]})
        ]
        # readonly_fields = ('qty', 'unit')pyt

    if COMPANY in COMPANYGROUP2:
        print('COMPANY2',COMPANY)
        fieldsets = [
           ('基础信息', {'fields': [('gcode', 'gname','mnemoniccode', 'price','buyprc','brand'),('qty','unit','spec', 'goodsct'),]}),
           ('提成',{'fields':[('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint', 'secpoint','thrpoint')]}),
           ('管理',{'fields':[('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
                   'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),('pricechangeable','saleflag','valiflag')]}),
           ('其他',{'fields':[('storelist','tags')]})
        ]


    # filter_horizontal = ('brand',)
    inlines = [GoodspriceInline]
    # forms = GoodsForm
    actions = ['to_excel',]


    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     if db_field.name == "brand":
    #         currentuser = get_admin_username(request)
    #         COMPANY = get_admin_company(request)
    #         print('goods admin company',COMPANY)
    #         kwargs['choices'] =  Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
    #         print('goods admin kwargs[choices] ',kwargs )
    #     return super().formfield_for_choice_field(db_field, request, **kwargs)

    #
    # def changelist_view(self, request, extra_context=None):
    #     user = request.user
    #
    #     if user.is_superuser:
    #         self.list_display = [‘field1’, ‘field2’]
    #         else:
    #         self.list_display = [‘field1’]
    #         return super(MyModelAdmin, self).changelist_view(request, extra_context=None)

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

class ServiecegoodsInline(AdminInlineModel):
    model = Serviecegoods
    fields = ('goodsuuid','gcode','qty')
    list_display=('gcode','qty')
    raw_id_fields=['goodsuuid']
    # exclude =['creater','uuid']
    extra = 0

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     currentuser = request.user._wrapped.username
    #     COMPANY = get_admin_company(request)
    #     # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
    #     return qs.filter(flag='Y',company=COMPANY)

    def get_goodscost(self):
        return self.goodscost

class ServiecepriceInline(AdminInlineModel):
    model = Servieceprice
    fields = ('srvcode','qty','price','amount','saleflag','stype')
    list_display=('srvcode','qty','price','amount','saleflag')
    exclude =['creater','uuid']
    extra = 0

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     currentuser = request.user._wrapped.username
    #     COMPANY = get_admin_company(request)
    #     # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
    #     return qs.filter(flag='Y',company=COMPANY)

    def save_related(self, request, form, formsets, change):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        # obj.company=COMPANY
        self.company=COMPANY
        print('1',self.company)
        super().save_model(request, form, formsets, change)


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

class ServieceAdmin(ItemAdmin):
    fieldsets = [
         (None, {'fields': [('svrcdoe', 'svrname',  'price'),('qty','stdmins','intervalday','brand','srvrptypecode', 'topcode'),]}),
         ('提成',{'fields':[ ('pmguideperc', 'secguideperc', 'thrguideperc','secpoint'),]}),
         ('管理',{'fields':['storelist','displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4','after_sales_scheme','pricechangeable','saleflag','valiflag']}),
         ('标签',{'fields':['tags']})
     ]

    list_display = ('svrcdoe', 'svrname','saleflag','valiflag' , 'price')
    inlines = [ ServiecegoodsInline,]
    search_fields = ['displayclass1','displayclass2','qty','stdmins','brand','mnemoniccode','svrcdoe', 'svrname']

    list_filter = (BrandListFilter, Displayclass1ListFilter, Displayclass2ListFilter, 'qty','stdmins', 'topcode', 'saleflag', 'valiflag')
    list_per_page = 25
    list_editable = ('svrname','price','saleflag','valiflag')
    # date_hierarchy = 'create_time'
    ordering = ('displayclass1','displayclass2','brand','svrcdoe',)
    # list_filter = (BrandListFilter,)
    # yfy
    if COMPANY=='yfy':
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'topcode','saleflag','valiflag')
    # 伊人
    if COMPANY=='yiren':
        list_display = ( 'svrcdoe', 'svrname',  'qty', 'stdmins', 'saleflag', 'valiflag','price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','qty','topcode','saleflag','valiflag')
    # list_filter = (BrandListFilter,)

    if COMPANY in COMPANYGROUP1:
        fieldsets = [
            ('基本信息', {'fields': [('svrcdoe', 'svrname', 'price'),
                               ('qty', 'stdmins', 'intervalday','brand', 'topcode'), ]}),
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc','pmperc','secperc','thrperc','pmpoint','secpoint','thrpoint')]}),
            ('管理信息', {'fields': [( 'displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4',
                               'pricechangeable', 'saleflag', 'valiflag')]}),
            ('标签', {'fields': [('tags','storelist')]})
        ]
        list_display = ( 'svrcdoe', 'svrname',  'saleflag', 'valiflag', 'price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','topcode','saleflag','valiflag')
        list_per_page = 25
        list_editable = ('svrname','price','saleflag','valiflag')
        inlines = [ServiecegoodsInline,ServiecepriceInline, ]
        # date_hierarchy = 'create_time'
        ordering = ('brand','displayclass1','displayclass2','svrcdoe',)

    if COMPANY in COMPANYGROUP2:
        fieldsets = [
            ('基本信息', {'fields': [('svrcdoe', 'svrname', 'price'),
                               ('qty', 'stdmins', 'intervalday', 'brand','topcode'), ]}),
            ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc','pmperc','secperc','thrperc','pmpoint','secpoint','thrpoint')]}),
            ('管理信息', {'fields': [( 'displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1', 'archivementclass2',
          'marketclass1', 'marketclass2', 'marketclass3', 'marketclass4',
                               'pricechangeable', 'saleflag', 'valiflag')]}),
            ('其他', {'fields': [('storelist','tags')]})
        ]
        list_display = ( 'svrcdoe', 'svrname', 'saleflag', 'valiflag', 'price')
        list_filter = (BrandListFilter,Displayclass1ListFilter,Displayclass2ListFilter,'after_sales_scheme','topcode','saleflag','valiflag')
        list_per_page = 25
        list_editable = ('svrname','price','saleflag','valiflag')
        inlines = [ServiecegoodsInline,ServiecepriceInline, ]
        # date_hierarchy = 'create_time'
        ordering = ('brand','displayclass1','displayclass2','svrcdoe',)

    def save_model(self, request, obj, form, change):
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        # obj.company=COMPANY
        self.company=COMPANY
        print('1',self.company)
        super().save_model(request, obj, form, change)
        # super().save_model(self,request,obj,form,change)
        # super().save_model(self, request, obj, form, change)

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


class CardtypeAdmin(ItemAdmin):
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
    list_display = ('cardtype', 'cardname','suptype','saleflag','price','leftmoney')
    inlines = [CardvsdiInline]

    search_fields = ['mnemoniccode','cardtype', 'cardname']
    list_filter = ('suptype', Displayclass1ListFilter, Displayclass2ListFilter, 'marketclass1','marketclass2','marketclass3','marketclass4','financeclass1','financeclass2',)
    list_per_page = 25
    list_editable = ('cardname','price','leftmoney','saleflag',)
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
        list_display = ('cardtype', 'cardname','suptype','saleflag','price')
        list_filter = ('suptype', Displayclass1ListFilter, Displayclass2ListFilter,)
        list_editable = ( 'cardname', 'suptype', 'saleflag', 'price',)

    if COMPANY in COMPANYGROUP2:
        fieldsets = [('基础信息', {'fields': [('suptype', 'comptype'),('cardtype', 'cardname', 'mnemoniccode', 'price', 'leftmoney', 'brand'),
                                 ('valdatetype', 'validays', 'cardnote')]}),
                        ('提成', {'fields': [('pmguideperc', 'secguideperc', 'thrguideperc', 'pmperc', 'secperc', 'thrperc', 'pmpoint','secpoint', 'thrpoint')]}),
                        ('管理', {'fields': [('displayclass1', 'displayclass2', 'financeclass1', 'financeclass2', 'archivementclass1',
                                            'archivementclass2','marketclass1', 'marketclass2', 'marketclass3', 'marketclass4'),
                                           ('pricechangeable', 'saleflag', 'valiflag')]}),
                        ('其他', {'fields': [('storelist', 'tags')]})
                    ]
        list_display = ('cardtype', 'cardname','suptype','saleflag','price')
        list_filter = ('suptype', Displayclass1ListFilter, Displayclass2ListFilter,)
        list_editable = ('cardname', 'suptype', 'saleflag', 'price',)

admin.site.register(Cardtype, CardtypeAdmin)


class PaymodeAdmin(AdminModel):
    fieldsets = [
        (None, {'fields': ['pcode', 'pname']}),
        ('Advance Information', {'fields': ['iscash','visibleflag', 'currency', 'rate', 'guideperc'], 'classes': ['collapse']}),
    ]
    list_display = ('pcode', 'pname', 'iscash','visibleflag')


admin.site.register(Paymode, PaymodeAdmin)


class VipAdmin(AdminModel):
 #    def preview(self,obj):
 # #       return u'<img src="'+self.%s" height="256",width="256" />'
 #        return u'<img src="/%s" height="64",width="64" >' % (obj.photofile)
 #    preview.allow_tags = True
 #    preview.short_description = u'photofile'

    # fieldsets=[
    #     (None,  {'fields':['vcode','vname','mtcode','photofile',]}),
    #     ('Advance Information',{'fields':['telph','addr','birth','qq','wechat','weibo','email','indate'],'classes':['wide','extrapretty']}),
    #     ]
    fields = ( 'uuid','vcode', 'vname','indate', 'storecode','birth', 'ecode', 'ecode2', 'status','othercha','vipcode')
    list_display = ('uuid', 'vcode', 'vname', 'storecode', 'ecode', 'ecode2','othercha','vipcode')
    list_editable = ('ecode', 'ecode2')
    list_filter = ( 'storecode','status','ecode','ecode2')
    search_fields = ('vcode', 'vname', )
    ordering = ['storecode', 'vcode']

    readonly_fields = ('uuid','storecode','othercha','vipcode')
    exclude = ('uuid','storecode')

admin.site.register(Vip, VipAdmin)

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

class TeamAdmin(AdminModel):
    fields =( 'teamid', 'teamname')
    list_display = ['teamid', 'teamname']
    # list_filter = ('teamid')
    list_editable =  (  'teamname',)

admin.site.register(Team, TeamAdmin)

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
