from django.contrib import admin
from django.contrib.admin import SimpleListFilter
import datetime
from django.db.models import Sum,Avg,Count

# Register your models here.
from .models import Expvstoll,Expense,Toll,TollCash,ExpvstollCash, Paymode,BankAccount
from baseinfo.models import *
from baseinfo.admin import AdminModel, COMPANYGROUP2, COMPANYGROUP1
from common.admin_utils import get_admin_company, get_admin_username


# admin.site.register(Enactmen,EnactmenAdmin)
class CashierAdminModel(admin.ModelAdmin):
    actions = ['export_as_excel',]
    # list_per_page = 25
    # 列表页每页展示的条数
    list_per_page = 100
    # 分页,显示全部,真是数据小于该值时才会显示全部
    list_max_show_all = 200

    List_display_links = None  # 禁用编辑链接

    def has_add_permission(self, request, obj=None):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

    def get_actions(self, request):
        # 在actions中去掉‘删除'操作
        actions = super(CashierAdminModel, self).get_actions(request)
        if request.user.username[0].upper() != 'J':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

# class Filter(SimpleListFilter):
#     title = 'node'  # or use _('country') for translated title
#     parameter_name = 'node'
#
#     def lookups(self, request, model_admin):
#         # 查出 node 的 id 和 name 值 用来显示在网页上的筛选条件
#         nodes = Node.objects.all()
#         return [(node.id, node.name + "-自定义") for node in nodes]
#
#     def queryset(self, request, queryset):
#         if self.value():
#             # 筛选条件有值时, 查询对应的 node 的文章，用 title 正排序
#             return queryset.filter(node__id=self.value()).order_by("title")
#         else:
#             # 筛选条件没有值时，全部的时候是没有值的
#             return queryset
class ExpvstollAdmin(AdminModel,CashierAdminModel):
    # 禁用编辑链接
    List_display_links = None

class TollAdmin(AdminModel,CashierAdminModel):
    # 禁用编辑链接
    list_display_links = None

    fields = ( 'exptxserno','expvssvern','pcode','totmount','tnote','bankaccount','confirm_ecode')
    list_display = [ 'storecode','vsdate','vip','exptxserno','pcode','totmount','tnote','bankaccount','confirm_ecode']
    list_filter = ('storecode','pcode','transuuid__vsdate','transuuid__vipuuid__vname')
    list_editable =  ( 'bankaccount','confirm_ecode')
    readonly_fields = ('exptxserno','expvssvern','pcode','totmount')
    search_fields = ('vsdate','exptxserno')

    def vsdate(self,object):
        return object.transuuid.vsdate

    def vip(self,object):
        return object.transuuid.vipuuid.vname +'('+object.transuuid.vcode+')' +'-'+object.transuuid.ccode

    def get_queryset(self,request):
        return super().get_queryset(request).order_by('storecode','-transuuid__vsdate','transuuid__vipuuid__vcode','exptxserno')

admin.site.register(Toll, TollAdmin)

class TollCashAdmin(AdminModel,CashierAdminModel):
    models=TollCash
    # 禁用编辑链接
    list_display_links = None

    fields = ( 'exptxserno','expvssvern','pcode','totmount','tnote','bankaccount','confirm_ecode')
    list_display = [ 'storecode','vsdate','vip','exptxserno','pcode','totmount','tnote','bankaccount','confirm_ecode']
    list_filter = ('storecode','pcode','transuuid__vsdate','transuuid__vipuuid__vname')
    list_editable =  ( 'bankaccount','confirm_ecode')
    readonly_fields = ('exptxserno','expvssvern','pcode','totmount')
    search_fields = ('vsdate','exptxserno')

    def vsdate(self,object):
        return object.transuuid.vsdate

    def vip(self,object):
        return object.transuuid.vipuuid.vname +'('+object.transuuid.vcode+')' +'-'+object.transuuid.ccode

    def get_queryset(self,request):
        return super().get_queryset(request).order_by('storecode','-transuuid__vsdate','transuuid__vipuuid__vcode','exptxserno')

admin.site.register(TollCash, TollCashAdmin)

class TollCashInline(admin.TabularInline):
    model = TollCash
    fields = ( 'exptxserno','expvssvern','pcode','totmount','tnote','bankaccount','confirm_ecode')
    readonly_fields = ('exptxserno','expvssvern','pcode','totmount')
    extra = 0

    def has_add_permission(self, request, obj=None):
        # 禁用添加按钮
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

class ExpvstollCashAdmin(AdminModel,CashierAdminModel):
    models=ExpvstollCash
    # list_display_links = None
    fields = ('storecode','vsdate','vcode','ccode','exptxserno','totmount','leftmoney')
    list_display = ['storecode','vsdate','vcode','ccode','exptxserno','totmount','leftmoney']
    list_filter = ('storecode','vsdate','vcode')
    readonly_fields = ('storecode','vsdate','vcode','ccode','exptxserno','totmount','leftmoney')
    date_hierarchy = 'create_time'
    inlines = [TollCashInline,]

    def get_queryset(self,request):
        qs = super().get_queryset(request)
        currentuser = get_admin_username(request)
        COMPANY = get_admin_company(request)
        import datetime as pydatetime
        fromdate = pydatetime.datetime.today() - pydatetime.timedelta(days=300)
        fromdate_string = fromdate.strftime('%Y%m%d')
        print('1',fromdate, fromdate_string)
        transuuids = TollCash.objects.filter(flag='Y',company=COMPANY,create_time__gte=fromdate).values_list('transuuid')
        # qs = Expvstoll.objects.filter(company=COMPANY,flag='Y',vsdate__gte=fromdate_string,uuid__in=transuuids).values('storecode','vipuuid__vname','vsdate').annotate(sumamount=Sum('totmount'))
        return Expvstoll.objects.filter(flag='Y',company=COMPANY, valiflag='Y',vsdate__gte=fromdate_string, uuid__in=transuuids).order_by('storecode','vsdate','vcode')
        # return qs

    # @property
    def leftmoney(self,obj=None):
        leftmoney=0
        if len(obj.ccode) >= 0:
            leftmoney=obj.cardleftmoney
        return  leftmoney
    leftmoney.allow_tags =True
    leftmoney.short_description = u'卡余额'

admin.site.register(ExpvstollCash, ExpvstollCashAdmin)