from django.urls import path, include  # ✅ correct import
from .views import (
    PaymentListCreateView, PaymentRetrieveUpdateDestroyView, TenantListCreateView, TenantRetrieveUpdateDestroyView, TenantVisitorListCreateView,VisitorRetrieveUpdateDestroyView, 
)

urlpatterns = [
    
    path('tenants/', TenantListCreateView.as_view(), name='tenant-list-create'),
    # path('tenants/me/', get_current_tenant, name='current_tenant'),
    path('tenants/<int:pk>/', TenantRetrieveUpdateDestroyView.as_view(), name='tenant-detail'),
    
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentRetrieveUpdateDestroyView.as_view(), name='payment-detail'),
    
    path('visitors/', TenantVisitorListCreateView.as_view(), name='visitor-list-create'),
    path('visitors/<int:pk>/', VisitorRetrieveUpdateDestroyView.as_view(), name='visitor-retrieve-update-destroy'),
]
