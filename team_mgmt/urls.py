from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

def home_redirect(request):
    return HttpResponseRedirect("/coach/login/")

urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('coach/', include('coach.urls')),
]
