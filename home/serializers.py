from rest_framework import serializers
from .models import Notification
from a_users.serializers import CustomUserSerializer


from rest_framework import serializers
from .models import Notification
from a_users.serializers import CustomUserSerializer
from a_users.models import CustomUser

class NotificationSerializer(serializers.ModelSerializer):
    recipients = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role='tenant'),
        many=True,
        required=False  
    )

    class Meta:
        model = Notification
        fields = ['id', 'message', 'recipients', 'timestamp', 'is_read', ]
        read_only_fields = ['timestamp', 'is_read']
class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'recipients', 'timestamp', 'is_read']
        read_only_fields = ['id', 'message', 'recipients', 'timestamp']
