from django.contrib import admin
from django.urls import path, include  # include lets you reference app URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('coach/', include('coach.urls')),  # Routes /coach/ to coach app URLs
]
