from django.urls import path, include  # ✅ correct import
from .views import (
    TenantListCreateView, TenantRetrieveUpdateDestroyView,
)

urlpatterns = [
    
    path('tenants/', TenantListCreateView.as_view(), name='tenant-list-create'),
    path('tenants/<int:pk>/', TenantRetrieveUpdateDestroyView.as_view(), name='tenant-detail'),
]
