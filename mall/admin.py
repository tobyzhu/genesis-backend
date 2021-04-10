#coding = utf-8

from django.contrib import admin
from django import forms
import xadmin

from baseinfo.admin import companylist
from mall.models import Banner,onlineShowType,onlineShowItem,onlineItemImage
from baseinfo.admin import COMPANY,AdminModel
# Register your models here.

class onlineAdminModel(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        return qs.filter(flag='Y',company=COMPANY)

    def save_model(self, request, obj, form, change):
        # qs = super().get_queryset(request)
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        obj.company = COMPANY
        obj.creater = currentuser
        obj.save()

class bannerAdmin(onlineAdminModel,admin.ModelAdmin):
    fields =   ('appcode', 'apppage','linkURL', 'bannerimage','orderno')
    list_display = ('id','appcode', 'apppage','linkURL', 'bannerimage','orderno')
    list_editable = ( 'linkURL', 'bannerimage','orderno')

    search_fields = ['apppage']
    ordering = ('orderno',)
admin.site.register(Banner, bannerAdmin)

class onlineShowTypeAdmin(onlineAdminModel,admin.ModelAdmin):
    fields =   ('showtypecode', 'showtypename','ttype', 'showtypeimage','showtypeurl','orderno')
    list_display = ('showtypecode', 'showtypename','ttype',  'showtypeimage','showtypeurl','orderno')
    list_editable = ( 'showtypename','ttype',  'showtypeimage','showtypeurl','orderno')

    search_fields = ['ttype']
    ordering = ('orderno','showtypecode',)

admin.site.register(onlineShowType, onlineShowTypeAdmin)

class onlineItemImageAdmin(admin.TabularInline):
# class GoodspriceInline(admin.TabularInline):
    model = onlineItemImage
    fields = ['onlineshowitem', 'imagetype', 'image_url', 'orderno']
    extra = 1

class onlineShowItemAdmin(onlineAdminModel,admin.ModelAdmin):
    fields =   ('onlineShowType', 'serviece','goods', 'itemdesc','small_showimage','onlineprice','orderno')
    list_display = ('onlineShowType', 'serviece','goods', 'itemdesc','small_showimage','onlineprice','orderno')
    list_editable = ( 'itemdesc','onlineprice','orderno')
    list_filter = ('onlineShowType',)
    search_fields = ['onlineShowType','itemdesc']
    ordering = ('orderno','serviece','goods',)
    inlines = [onlineItemImageAdmin]

    def formfield_for_foreignkey(self,db_field,request=None,**kwargs):
        currentuser = request.user._wrapped.username
        COMPANY = companylist[currentuser]
        field = super(onlineShowItemAdmin,self).formfield_for_foreignkey(db_field,request,**kwargs)
        if db_field.name == 'goods':
            # if request._obj_ is not None:
                field.queryset = field.queryset.filter(company = COMPANY)
            # else:
            #     field.queryset = field.queryset.none()
        if db_field.name == 'serviece':
            field.queryset = field.queryset.filter(company=COMPANY)

        return field

admin.site.register(onlineShowItem, onlineShowItemAdmin)
