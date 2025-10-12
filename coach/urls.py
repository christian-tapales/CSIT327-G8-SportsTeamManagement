from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Default redirect (root → login page)
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),

    # Auth routes
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),

    # Coach dashboard
    path('dashboard/', views.coach_dashboard, name='coach_dashboard'),
]
