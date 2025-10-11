from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.coach_dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),   
]
