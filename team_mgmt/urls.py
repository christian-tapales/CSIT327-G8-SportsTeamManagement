from django.contrib import admin
from django.urls import path, include
from coach import views  # import your landing page view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('coach/', include('coach.urls')),
    path('', views.landing_page, name='landing_page'),  # 👈 show landing page at root URL
]
