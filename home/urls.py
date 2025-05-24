from django.urls import path
from .views import (
     NotificationListView,NotificationDetailView , home
)


urlpatterns = [
    path('', home, name='home'),
    path('notification/', NotificationListView.as_view(), name='login'),
    path('notification/<int:pk>/', NotificationDetailView.as_view(), name='tenant-detail'),
    
]
