# team_mgmt/urls.py (The project-level file)

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from coach import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🎯 AUTH PATHS AT ROOT LEVEL (These are the ONLY place they should be defined)
    path('', views.landing_page, name='landing_page'), 
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'), 
    
    # 🔗 APPLICATION PATHS (Includes all non-auth paths under the /coach/ prefix)
    path('coach/', include('coach.urls')),
]