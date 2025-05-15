from django.urls import path, include  # ✅ correct import
from .views import (
    TenantListCreateView, TenantRetrieveUpdateDestroyView,VisitorListCreateView,VisitorRetrieveUpdateDestroyView
)

urlpatterns = [
    
    path('tenants/', TenantListCreateView.as_view(), name='tenant-list-create'),
    path('tenants/<int:pk>/', TenantRetrieveUpdateDestroyView.as_view(), name='tenant-detail'),
    
    path('visitors/', VisitorListCreateView.as_view(), name='visitor-list-create'),
    path('visitors/<int:pk>/', VisitorRetrieveUpdateDestroyView.as_view(), name='visitor-retrieve-update-destroy'),
]
