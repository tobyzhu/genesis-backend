from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from .models import TrialLead
from .serializers import TrialLeadSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def trial_signup(request):
    """公开 API：收集试用申请"""
    serializer = TrialLeadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': '申请已提交，我们将在 24 小时内与你联系。',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class TrialLeadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """后台管理：查看/更新试用线索"""
    queryset = TrialLead.objects.all()
    serializer_class = TrialLeadSerializer
    permission_classes = [IsAdminUser]
