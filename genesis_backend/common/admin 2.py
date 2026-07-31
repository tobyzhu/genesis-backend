from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django import forms

from common.models import WifiList, GenesisUserProfile


class WifiListAdmin(admin.ModelAdmin):
    fields = ('SSID', 'BSSID', 'valiflag', 'storecode', 'company')
    list_display = ('SSID', 'BSSID', 'valiflag', 'storecode', 'company')


admin.site.register(WifiList, WifiListAdmin)


class GenesisUserProfileInline(admin.StackedInline):
    model = GenesisUserProfile
    can_delete = False
    verbose_name = 'Genesis 公司与门店'
    verbose_name_plural = verbose_name
    fk_name = 'user'
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'company',
                    'default_storecode',
                    'storelist',
                    'employee_code',
                    'display_name',
                    'is_company_admin',
                    'hdsysuser_uuid',
                    'costpriceflag',
                )
            },
        ),
    )


class GenesisUserAdmin(DjangoUserAdmin):
    inlines = (GenesisUserProfileInline,)

    list_display = DjangoUserAdmin.list_display + ('genesis_company', 'genesis_stores')

    def genesis_company(self, obj):
        try:
            return obj.genesis_profile.company
        except GenesisUserProfile.DoesNotExist:
            return '—'

    genesis_company.short_description = '公司'

    def genesis_stores(self, obj):
        try:
            p = obj.genesis_profile
            if p.is_company_admin:
                return '* 全部门店'
            return p.storelist or p.default_storecode or '—'
        except GenesisUserProfile.DoesNotExist:
            return '—'

    genesis_stores.short_description = '可用门店'


admin.site.unregister(User)
admin.site.register(User, GenesisUserAdmin)


@admin.register(GenesisUserProfile)
class GenesisUserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'company',
        'default_storecode',
        'employee_code',
        'display_name',
        'is_company_admin',
    )
    list_filter = ('company', 'is_company_admin')
    search_fields = ('user__username', 'employee_code', 'display_name')
    raw_id_fields = ('user',)
