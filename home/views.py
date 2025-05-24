from django.shortcuts import render
from .models import Notification
from .serializers import NotificationSerializer,NotificationMarkReadSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from utils.permissions import IsAdminOrPropertyManager
from a_users.models import CustomUser
from rest_framework.response import Response
from rest_framework import status

def home(request):
    return render(request, 'home.html')


class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def create(self, request, *args, **kwargs):
        recipients_data = request.data.get('recipients', None)
        message = request.data.get('message', '')
        if not message:
            return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)
        notification = Notification.objects.create(message=message)
        if recipients_data == 'all_tenants':
            tenants = CustomUser.objects.filter(role='tenant')
            notification.recipients.set(tenants)
        elif isinstance(recipients_data, list):
            users = CustomUser.objects.filter(id__in=recipients_data, role='tenant')
            notification.recipients.set(users)
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

class TenantNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return notifications where the current user is a recipient
        return Notification.objects.filter(recipients=self.request.user)
    
class NotificationMarkReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationMarkReadSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'notification_id'

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        # Ensure the user is a recipient of the notification
        if request.user not in notification.recipients.all():
            return Response(
                {"error": "You are not authorized to mark this notification as read."},
                status=status.HTTP_403_FORBIDDEN
            )
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)