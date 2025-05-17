from django.urls import path
from .views import (
    LoginView, RegisterView, get_user,
    PropertyListCreateView, PropertyRetrieveUpdateDestroyView,
    TenantListCreateView, TenantRetrieveUpdateDestroyView,
    UnitListCreateView, UnitRetrieveUpdateDestroyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    
    path('user/', get_user),
    
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyView.as_view(), name='property-detail'),
    
    path('units/', UnitListCreateView.as_view(), name='unit-list-create'),
    path('units/<int:pk>/', UnitRetrieveUpdateDestroyView.as_view(), name='unit-detail'),
    
    path('tenants/', TenantListCreateView.as_view(), name='tenant-list-create'),
    path('tenants/<int:pk>/', TenantRetrieveUpdateDestroyView.as_view(), name='tenant-detail'),
]