from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing_page'),

    # Auth routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    # Logout → Redirects to landing page
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'),

    # Dashboard
    path('dashboard/', views.coach_dashboard, name='coach_dashboard'),
    
    # Team detail page
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
]