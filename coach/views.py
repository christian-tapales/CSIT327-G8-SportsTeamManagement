from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Player, Team


# -------------------------------
# Login View
# -------------------------------
def login_view(request):
    """
    Accepts either username OR email in the 'username' field.
    """
    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password   = (request.POST.get("password") or "")

        actual_username = None

        # If it looks like an email, map to username via email lookup
        if "@" in identifier:
            u = User.objects.filter(email__iexact=identifier).first()
            if u:
                actual_username = u.username

        # Otherwise try as username, or fall back to email lookup
        if not actual_username:
            if User.objects.filter(username__iexact=identifier).exists():
                actual_username = identifier
            else:
                u = User.objects.filter(email__iexact=identifier).first()
                if u:
                    actual_username = u.username

        user = authenticate(request, username=actual_username or "", password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid credentials. Check your email/username and password.")
        return render(request, "auth/login.html")

    return render(request, "auth/login.html")


# -------------------------------
# Coach Dashboard View
# (GET: show teams / POST: create team)
# -------------------------------
@login_required(login_url='login')
def coach_dashboard(request):
    """
    GET  -> show dashboard with user's teams
    POST -> create a Team from modal form (team_name, sport, season)
    Template: team_mgmt/templates/team_mgmt/coach_dashboard.html
    """
    if request.method == "POST":
        name   = (request.POST.get("team_name") or "").strip()
        sport  = (request.POST.get("sport") or "").strip()
        season = (request.POST.get("season") or "").strip()

        valid_sports = {code for code, _ in Team.SPORT_CHOICES}
        if not name or not sport:
            messages.error(request, "Team name and sport are required.")
        elif sport not in valid_sports:
            messages.error(request, "Please choose a valid sport.")
        else:
            Team.objects.create(
                coach=request.user,
                name=name,
                sport=sport,
                season=season
            )
            messages.success(request, f'Team "{name}" created.')
            return redirect("dashboard")  # Post/Redirect/Get to avoid resubmits

    teams = Team.objects.filter(coach=request.user)
    players = Player.objects.filter(coach=request.user)

    return render(
        request,
        "team_mgmt/coach_dashboard.html",
        {
            "players": players,
            "teams": teams,
            "sport_choices": Team.SPORT_CHOICES,
        },
    )


# -------------------------------
# Register View (create user → login → go dashboard)
# -------------------------------
def register_view(request):
    """
    Expects: username, first_name, last_name, email, password1, password2
    On success: auto-login and redirect to 'dashboard'
    Template: coach/templates/auth/register.html
    """
    if request.method == "POST":
        username   = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name  = (request.POST.get("last_name") or "").strip()
        email      = (request.POST.get("email") or "").strip().lower()
        password1  = request.POST.get("password1") or ""
        password2  = request.POST.get("password2") or ""

        # --- validations ---
        if not all([username, first_name, last_name, email, password1, password2]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "auth/register.html")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address (e.g., user@example.com).")
            return render(request, "auth/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/register.html")

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "auth/register.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "auth/register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with that email already exists.")
            return render(request, "auth/register.html")

        # --- create user with chosen username ---
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "auth/register.html")