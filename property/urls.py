from django.urls import path, include  # ✅ correct import
from .views import (
    PropertyListCreateView, PropertyRetrieveUpdateDestroyView,
    UnitListCreateView, UnitRetrieveUpdateDestroyView
)

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyView.as_view(), name='property-detail'),
    
    path('units/', UnitListCreateView.as_view(), name='unit-list-create'),
    path('units/<int:pk>/', UnitRetrieveUpdateDestroyView.as_view(), name='unit-detail'),
]
