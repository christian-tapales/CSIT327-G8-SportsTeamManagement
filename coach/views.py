from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Player

# -------------------------------
# Login / Logout Views
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")  # Redirect to dashboard
            else:
                form.add_error(None, "Invalid username or password")
        else:
            form.add_error(None, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

# -------------------------------
# Coach Dashboard View
# -------------------------------
def coach_dashboard(request):
    # If Player.coach is a ForeignKey to User, this works:
    players = Player.objects.filter(coach=request.user)
    return render(request, 'coach_dashboard.html', {'players': players})
