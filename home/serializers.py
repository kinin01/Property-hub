from rest_framework import serializers
from .models import Notification
from a_users.serializers import CustomUserSerializer


from rest_framework import serializers
from .models import Notification
from a_users.serializers import CustomUserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Notification
        fields = ['message', 'user', 'is_read', 'timestamp']
