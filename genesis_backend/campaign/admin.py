from django.contrib import admin
from .models import TrialLead

@admin.register(TrialLead)
class TrialLeadAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'contact_name', 'phone', 'store_count',
                    'status', 'created_at', 'contacted_at']
    list_filter = ['status', 'created_at']
    search_fields = ['store_name', 'contact_name', 'phone']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    actions = ['mark_contacted']

    def mark_contacted(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='contacted', contacted_at=timezone.now())
        self.message_user(request, f'已将 {queryset.count()} 条线索标记为已联系')
    mark_contacted.short_description = '标记为已联系'
