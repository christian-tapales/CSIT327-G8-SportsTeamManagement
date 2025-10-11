from django.contrib import admin
from django.urls import path, include  # include lets you reference app URLs
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('coach/', include('coach.urls')),  # Routes /coach/ to coach app URLs
    path('', RedirectView.as_view(url='/coach/', permanent=False)),
]
