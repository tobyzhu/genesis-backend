from django.contrib import admin

# Register your models here..
from baseinfo.admin import AdminModel
from .models import WechatAppFunctions



class WechatAppFunctionsAdmin(AdminModel):
    fields = ('functiontype','functionid','functionname','wxusertype','id','text','url','image','parentfunction','valiflag',)
    list_display = ('functiontype','functionid','wxusertype','id','text','url','image','parentfunction','valiflag',)
    list_filter = ( 'functiontype','functionid','wxusertype','valiflag')
    list_editable = ('functionid','wxusertype','id','text','url','image','parentfunction','valiflag')
    search_fields = ['functionid','wxusertype','id','text','url','image','parentfunction', ]
    ordering = ('functiontype','functionid','id')

admin.site.register(WechatAppFunctions, WechatAppFunctionsAdmin)

