from rest_framework import serializers
from .models import TrialLead

class TrialLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrialLead
        fields = ['uuid', 'store_name', 'contact_name', 'phone', 'store_count',
                  'current_system', 'remark', 'status', 'created_at']
        read_only_fields = ['uuid', 'status', 'created_at']

    def validate_phone(self, value):
        import re
        if not re.match(r'^1\d{10}$', value):
            raise serializers.ValidationError('请填写正确的手机号')
        return value
