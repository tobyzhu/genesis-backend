from django.contrib import admin

from .models import CrmSubReport,CrmInfoItem,CrmInfoItemChoice
from baseinfo.admin import AdminModel
# Register your models here.

class CrmSubReportAdmin(AdminModel):
    fields = ('crmsubreportName',)
    list_display = ('crmsubreportName',)

admin.site.register(CrmSubReport, CrmSubReportAdmin)

class CrmInfoItemChoiceInlineAdmin(admin.TabularInline):
    model = CrmInfoItemChoice
    fields = ('choiceitemname','orderno')
    list_display =  ('choiceitemname','orderno')
    extra = 1

class CrmInfoItemAdmin(AdminModel):
    fields = ('crmsubreport','itemid','itemname','itemtype','requireflag')
    list_display =  ('crmsubreport','itemid','itemname','itemtype','requireflag')
    inlines = [CrmInfoItemChoiceInlineAdmin]

admin.site.register(CrmInfoItem, CrmInfoItemAdmin)


class CrmInfoItemChoiceAdmin(AdminModel):
    fields = ('crminfoitem','choiceitemname','orderno')
    list_display =  ('crminfoitem','choiceitemname','orderno')
    list_filter = ['crminfoitem',]

admin.site.register(CrmInfoItemChoice, CrmInfoItemChoiceAdmin)
