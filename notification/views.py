from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from .serializers import NotificationSerializer
from lexeme.pagination import MyPagination
from .models import Notification
from rest_framework.response import Response
from rest_framework import status


class NotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = MyPagination
    pagination_class.page_size = 10
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user:
            user = self.request.user
        return Notification.objects.filter(Q(user=user) & Q(active=True))


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def unset_active_for_all(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.update(active=False)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def unset_active(request,notificationId):
    try:
        notification = Notification.objects.get(id=notificationId)
    except Notification.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.user != notification.user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    notification.active=False
    notification.save()
    return Response(status=status.HTTP_200_OK)

