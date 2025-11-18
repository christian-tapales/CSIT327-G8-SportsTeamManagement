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
    
    # Edit team
    path('team/<int:team_id>/edit/', views.edit_team, name='edit_team'),
    
    # Add player
    path('team/<int:team_id>/add-player/', views.add_player, name='add_player'),
    
    # Edit player
    path('team/<int:team_id>/player/<int:player_id>/edit/', views.edit_player, name='edit_player'),
    
    # Remove player
    path('team/<int:team_id>/player/<int:player_id>/remove/', views.remove_player, name='remove_player'),

    #delete
    path('team/<int:team_id>/delete/', views.delete_team, name='delete_team'),

    #addevent
    path('event/add/', views.add_event, name='add_event'),

    #editevent
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),

    #deleteevent
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
]