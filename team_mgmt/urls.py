# team_mgmt/urls.py (The project-level file)

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from coach import views
from django.conf import settings
from django.conf.urls.static import static

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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Force serve media files in production (Use with caution, for simple deployments)
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]