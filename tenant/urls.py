from django.urls import path, include  # ✅ correct import
from .views import (
    PaymentListCreateView, PaymentRetrieveUpdateDestroyView, TenantListCreateView, TenantRetrieveUpdateDestroyView,VisitorListCreateView,VisitorRetrieveUpdateDestroyView, 
)

urlpatterns = [
    
    path('tenants/', TenantListCreateView.as_view(), name='tenant-list-create'),
    path('tenants/<int:pk>/', TenantRetrieveUpdateDestroyView.as_view(), name='tenant-detail'),
    
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentRetrieveUpdateDestroyView.as_view(), name='payment-detail'),
    
    path('visitors/', VisitorListCreateView.as_view(), name='visitor-list-create'),
    path('visitors/<int:pk>/', VisitorRetrieveUpdateDestroyView.as_view(), name='visitor-retrieve-update-destroy'),
]
