from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Player, Team
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer  # Assume these are defined

# -------------------------------
# Login View
# -------------------------------
@api_view(['GET', 'POST'])
def login_view(request):
    """
    Accepts either username OR email in the 'username' field.
    GET: Renders login template.
    POST: Authenticates user and returns JSON response.
    """
    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "")

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
            return JsonResponse({
                "status": "success",
                "message": "Login successful",
                "redirect": "/dashboard/"
            }, status=status.HTTP_200_OK)

        return JsonResponse({
            "status": "error",
            "message": "Invalid credentials. Check your email/username and password."
        }, status=status.HTTP_401_UNAUTHORIZED)

    return render(request, "auth/login.html")

# -------------------------------
# Coach Dashboard View
# (GET: show teams / POST: create team)
# -------------------------------
@login_required(login_url='login')
@api_view(['GET', 'POST'])
def coach_dashboard(request):
    """
    GET  -> show dashboard with user's teams
    POST -> create a Team from modal form (team_name, sport, season) and return JSON
    Template: team_mgmt/templates/team_mgmt/coach_dashboard.html
    """
    if request.method == "POST":
        name = (request.POST.get("team_name") or "").strip()
        sport = (request.POST.get("sport") or "").strip()
        season = (request.POST.get("season") or "").strip()

        valid_sports = {code for code, _ in Team.SPORT_CHOICES}
        if not name or not sport:
            return JsonResponse({
                "status": "error",
                "message": "Team name and sport are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        elif sport not in valid_sports:
            return JsonResponse({
                "status": "error",
                "message": "Please choose a valid sport."
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            team = Team.objects.create(
                coach=request.user,
                name=name,
                sport=sport,
                season=season
            )
            return JsonResponse({
                "status": "success",
                "message": f"Team “{name}” created.",
                "team_id": team.id
            }, status=status.HTTP_201_CREATED)

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
@api_view(['GET', 'POST'])
def register_view(request):
    """
    Expects: username, first_name, last_name, email, password1, password2
    On success: auto-login and return JSON with redirect.
    Template: coach/templates/auth/register.html
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        # --- validations ---
        if not all([username, first_name, last_name, email, password1, password2]):
            return JsonResponse({
                "status": "error",
                "message": "Please fill in all fields."
            }, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return JsonResponse({
                "status": "error",
                "message": "Passwords do not match."
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(password1) < 8:
            return JsonResponse({
                "status": "error",
                "message": "Password must be at least 8 characters."
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({
                "status": "error",
                "message": "Username is already taken."
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "An account with that email already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- create user with chosen username ---
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )

        login(request, user)
        return JsonResponse({
            "status": "success",
            "message": "Registration successful",
            "redirect": "/dashboard/"
        }, status=status.HTTP_201_CREATED)

    return render(request, "auth/register.html")