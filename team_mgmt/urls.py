from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("coach/", include("coach.urls")),  # ✅ ensures coach URLs are recognized
]
