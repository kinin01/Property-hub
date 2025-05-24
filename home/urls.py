from django.urls import path
from .views import ( NotificationListView, NotificationMarkReadView, TenantNotificationListView, home, NotificationCreateView,
)


urlpatterns = [
    path('', home, name='home'),
    path('notifications/list/', NotificationListView.as_view(), name='list-notifications'),
    path('notifications/create/', NotificationCreateView.as_view(), name='create-notification'),

    path('tenant/notifications/', TenantNotificationListView.as_view(), name='tenant-list-notifications'),
    path('notifications/<int:notification_id>/mark-read/', NotificationMarkReadView.as_view(), name='mark-notification-read'),
]
