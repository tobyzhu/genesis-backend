#coding = utf-8

from django.contrib import admin
from django import forms

from common.admin_utils import get_admin_company, GenesisCompanyAdminMixin
from mall.models import Banner, onlineShowType, onlineShowItem, onlineItemImage


class onlineAdminModel(GenesisCompanyAdminMixin, admin.ModelAdmin):
    pass


class bannerAdmin(onlineAdminModel, admin.ModelAdmin):
    fields = ('appcode', 'apppage', 'linkURL', 'bannerimage', 'orderno')
    list_display = ('id', 'appcode', 'apppage', 'linkURL', 'bannerimage', 'orderno')
    list_editable = ('linkURL', 'bannerimage', 'orderno')
    search_fields = ['apppage']
    ordering = ('orderno',)


admin.site.register(Banner, bannerAdmin)


class onlineShowTypeAdmin(onlineAdminModel, admin.ModelAdmin):
    fields = ('showtypecode', 'showtypename', 'ttype', 'showtypeimage', 'showtypeurl', 'orderno')
    list_display = ('showtypecode', 'showtypename', 'ttype', 'showtypeimage', 'showtypeurl', 'orderno')
    list_editable = ('showtypename', 'ttype', 'showtypeimage', 'showtypeurl', 'orderno')
    search_fields = ['ttype']
    ordering = ('orderno', 'showtypecode',)


admin.site.register(onlineShowType, onlineShowTypeAdmin)


class onlineItemImageAdmin(admin.TabularInline):
    model = onlineItemImage
    fields = ['onlineshowitem', 'imagetype', 'image_url', 'orderno']
    extra = 1


class onlineShowItemAdmin(onlineAdminModel, admin.ModelAdmin):
    fields = ('onlineShowType', 'serviece', 'goods', 'itemdesc', 'small_showimage', 'onlineprice', 'orderno')
    list_display = ('onlineShowType', 'serviece', 'goods', 'itemdesc', 'small_showimage', 'onlineprice', 'orderno')
    list_editable = ('itemdesc', 'onlineprice', 'orderno')
    list_filter = ('onlineShowType',)
    search_fields = ['onlineShowType', 'itemdesc']
    ordering = ('orderno', 'serviece', 'goods',)
    inlines = [onlineItemImageAdmin]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        COMPANY = get_admin_company(request)
        field = super(onlineShowItemAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )
        if db_field.name == 'goods':
            field.queryset = field.queryset.filter(company=COMPANY)
        if db_field.name == 'serviece':
            field.queryset = field.queryset.filter(company=COMPANY)
        return field


admin.site.register(onlineShowItem, onlineShowItemAdmin)
