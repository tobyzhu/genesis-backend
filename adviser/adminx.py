__author__ = 'yuyang'
from django.contrib import admin

# Register your models here.
import xadmin
from .models import Room
# from django.db.models import get_app, get_models


# app = get_app('shop')
# for model in get_models(app):
#     name = model._meta.verbose_name
#     xadmin.site.register(model)

class RoomAdmin(object):
    model = Room
#    fields = ('casename','creator', 'casetype', 'ecode','vname','contactmethod','vipsource','status','startdate','finishedate')
    fields= ( 'roomid','roomname','storecode','roomtype')
    list_display = [ 'roomid','roomname','storecode','roomtype']
    list_editable = [ 'roomid','roomname','storecode','roomtype']
    search_fields = ['roomid','roomname','storecode','roomtype']
    list_filter =  [ 'roomid','roomname','storecode','roomtype']
 #   inlines = [VipInline]
#    relfield_style='fk-ajax'
#     extra = 1
    # def save_models(self):
    #     self.new_obj.creater = self.request.user.username
    #     super().save_models()
    #
    # def queryset(self):
    #     qs = super(VipCaseDetailAdmin, self).queryset()
    #     if self.request.user.is_superuser:  # 超级用户可查看所有数据
    #         return qs
    #     else:
    #         return qs.filter(creater=self.request.user.username)  # creater是Case Model的creater字段

xadmin.site.register(Room,RoomAdmin)