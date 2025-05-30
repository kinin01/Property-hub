from rest_framework import serializers
from .models import Notification
from a_users.serializers import CustomUserSerializer


from rest_framework import serializers
from .models import Notification
from a_users.models import CustomUser

class PropertyCollectionStatsSerializer(serializers.Serializer):
    property_id = serializers.IntegerField()
    property_name = serializers.CharField()
    total_units = serializers.IntegerField()
    occupied_units = serializers.IntegerField()
    amount_due = serializers.FloatField()
    amount_paid = serializers.FloatField()
    balance = serializers.FloatField()
    collection_percentage = serializers.FloatField()
    payment_count = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    occupied_units = serializers.IntegerField()
    non_occupied_units = serializers.IntegerField()
    occupancy_percentage = serializers.FloatField()
    total_payments = serializers.IntegerField()
    total_amount_due = serializers.FloatField()
    total_amount_paid = serializers.FloatField()
    total_balance = serializers.FloatField()
    collection_percentage = serializers.FloatField()
    property_collection_stats = PropertyCollectionStatsSerializer(many=True)

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
