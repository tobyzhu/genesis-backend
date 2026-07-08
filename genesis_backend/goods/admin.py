from django.contrib import admin

# Register your models here.
# from .models import Serviecegoods
from baseinfo.admin import AdminModel, COMPANY, BrandListFilter, Displayclass1ListFilter, Displayclass2ListFilter

# class ServiecegoodsInline(admin.StackedInline):
#     model = Serviecegoods
#     fields = ('goodsuuid','gcode','qty')
#     list_display=('gcode','qty',)
#     raw_id_fields=['goodsuuid']
#     # exclude =['creater','uuid']
#     extra = 0
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         currentuser = request.user._wrapped.username
#         COMPANY = companylist[currentuser]
#         # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
#         return qs.filter(flag='Y',company=COMPANY)

# class ServiecegoodsAdmin(AdminModel):
#     model = Serviecegoods
#     fields = ('srvuuid__srvname','srvcode','goodsuuid','gcode','qty')
#     list_display=('gcode','qty',)
#     raw_id_fields=['srvuuid','goodsuuid']
#     # exclude =['creater','uuid']
#     extra = 0
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         currentuser = request.user._wrapped.username
#         COMPANY = companylist[currentuser]
#         # BRAND = Appoption.objects.filter(company=COMPANY, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
#         return qs.filter(flag='Y',company=COMPANY)
#
# admin.site.register(Serviecegoods, ServiecegoodsAdmin)

