
import decimal
from venv import logger

from a_users import models
from property.models import Property, Unit
from tenant.models import Payment
from .models import Notification
from .serializers import DashboardStatsSerializer, NotificationSerializer,NotificationMarkReadSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from utils.permissions import IsAdminOrPropertyManager
from a_users.models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count



  
class DashboardStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]
    serializer_class = DashboardStatsSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            logger.debug(f"Fetching dashboard stats for user {user.email}")
            if user.role == 'admin':
                properties = Property.objects.filter(is_active=True)
                units = Unit.objects.all()
                payments = Payment.objects.all()
            else:
                # Filter by properties owned or managed by the user
                properties = Property.objects.filter(is_active=True).filter(
                    models.Q(owner=user) | models.Q(manager=user)
                )
                units = Unit.objects.filter(
                    models.Q(property__owner=user) | models.Q(property__manager=user)
                )
                payments = Payment.objects.filter(
                    models.Q(unit__property__owner=user) | models.Q(unit__property__manager=user)
                )

            # Property metrics
            total_properties = properties.count()
            logger.debug(f"Total properties: {total_properties}")

            # Unit metrics
            total_units = units.count()
            occupied_units = units.filter(is_occupied=True).count()
            non_occupied_units = total_units - occupied_units
            occupancy_percentage = (
                (occupied_units / total_units * 100) if total_units > 0 else 0.0
            )
            logger.debug(f"Unit metrics: total={total_units}, occupied={occupied_units}, non_occupied={non_occupied_units}")

            # Payment metrics with type casting
            payment_aggregates = payments.aggregate(
                total_due=Sum('amount_due'),
                total_paid=Sum('amount_paid'),
                total_payments=Count('id')
            )
            total_amount_due = decimal.Decimal(str(payment_aggregates['total_due'] or 0))
            total_amount_paid = decimal.Decimal(str(payment_aggregates['total_paid'] or 0))
            total_payments = payment_aggregates['total_payments'] or 0
            total_balance = total_amount_due - total_amount_paid
            collection_percentage = (
                (total_amount_paid / total_amount_due * 100) if total_amount_due > 0 else 0.0
            )
            logger.debug(f"Payment metrics: due={total_amount_due}, paid={total_amount_paid}, balance={total_balance}")
            stats = {
                'total_properties': total_properties,
                'total_units': total_units,
                'occupied_units': occupied_units,
                'non_occupied_units': non_occupied_units,
                'occupancy_percentage': round(occupancy_percentage, 1),
                'total_payments': total_payments,
                'total_amount_due': float(total_amount_due),
                'total_amount_paid': float(total_amount_paid),
                'total_balance': float(total_balance),
                'collection_percentage': round(collection_percentage, 1),
            }

            serializer = self.get_serializer(stats)
            logger.info(f"Dashboard stats retrieved for user {user.email}: {stats}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving dashboard stats for user {user.email}: {str(e)}")
            return Response(
                {'detail': 'Failed to retrieve dashboard statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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