# coach/urls.py (The app-level file)

from django.urls import path
from . import views

urlpatterns = [
    # DELETE ALL LOGIN/LOGOUT/REGISTER PATHS FROM THIS FILE
    
    # Dashboard path (keep this)
    path('dashboard/', views.coach_dashboard, name='coach_dashboard'),
    
    # Team paths (keep these)
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/edit/', views.edit_team, name='edit_team'),
    path('team/<int:team_id>/add-player/', views.add_player, name='add_player'),
    path('team/<int:team_id>/player/<int:player_id>/edit/', views.edit_player, name='edit_player'),
    path('team/<int:team_id>/player/<int:player_id>/remove/', views.remove_player, name='remove_player'),
    path('teams/', views.teams_view, name='teams'),
    path('team/<int:team_id>/delete/', views.delete_team, name='delete_team'),

    # Event paths (keep these)
    path('event/add/', views.add_event, name='add_event'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:event_id>/attendance/', views.event_attendance, name='event_attendance'),
    path('event/<int:event_id>/stats/', views.event_stats, name='event_stats'),

    # Profile paths (keep these)
    path('profile/', views.profile_view, name='profile'),
    path('players/', views.players_view, name='players'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('stats/', views.stats_view, name='stats'),
    path('stats/save/', views.save_game_stats, name='save_game_stats'),
    path('player/<int:player_id>/stats/', views.player_stats_history, name='player_stats_history'),
    path('player/<int:player_id>/history/', views.player_stats_page, name='player_stats_page'),
    path('password-change/', views.change_password, name='change_password'),
]