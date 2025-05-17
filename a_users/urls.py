from django.urls import path
from .views import (
     DashboardStatsView, LoginView, RegisterView, get_payments, get_user,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', get_user),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('payments/', get_payments, name='get-payments'),
]