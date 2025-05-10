from django.urls import path
from .views import LoginView,RegisterView,get_user

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
     path('user/', get_user),
]
