from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Player, Team, CoachProfile 

from .models import Player, Team


# -------------------------------
# Landing Page View
# -------------------------------
def landing_page(request):
    """
    Displays the home landing page with buttons for Login and Register.
    """
    return render(request, "auth/landing_page.html")


# -------------------------------
# Login View
# -------------------------------
def login_view(request):
    """
    Accepts either username OR email in the 'username' field.
    """
    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "")

        actual_username = None

        # If it's an email, find username via email lookup
        if "@" in identifier:
            u = User.objects.filter(email__iexact=identifier).first()
            if u:
                actual_username = u.username

        # Otherwise, try username or fallback to email lookup
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
            return redirect("coach_dashboard")  # ✅ redirect to dashboard
        else:
            messages.error(request, "Invalid credentials. Check your email/username and password.")

    return render(request, "auth/login.html")


# -------------------------------
# Coach Dashboard View
# -------------------------------
@login_required(login_url="login")
def coach_dashboard(request):


    """
    GET  -> show dashboard with user's teams
    POST -> create a Team from modal form (team_name, sport, season)
    """

    coach_profile = CoachProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        name = (request.POST.get("team_name") or "").strip()
        location = (request.POST.get("location") or "").strip()
        max_players_allowed = request.POST.get("max_players_allowed") or 0
        status = request.POST.get("status") or "Active"

        if not name:
            messages.error(request, "Team name is required.")
        else:
            Team.objects.create(
                coach=request.user,
                name=name,
                sport=coach_profile.sport if coach_profile else "",  # auto-fill from profile
                location=location,
                max_players_allowed=max_players_allowed,
                status=status,
            )


            messages.success(request, f'Team "{name}" created successfully!')
            return redirect("coach_dashboard")  # ✅ clean redirect after POST

            messages.success(request, f"Team “{name}” created successfully.")
            return redirect("coach_dashboard")

    teams = Team.objects.filter(coach=request.user)
    players = Player.objects.filter(coach=request.user)

    return render(
        request,
        "team_mgmt/coach_dashboard.html",
        {
            "players": players,
            "teams": teams,
            "coach_profile": coach_profile,
        },
    )



# -------------------------------
# Register View
# -------------------------------
def register_view(request):
    """

    Expects: username, first_name, last_name, email, password1, password2

    Register a new coach with a chosen sport.
    Expects: username, first_name, last_name, email, password1, password2, sport
    On success: auto-login and redirect to dashboard
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""
        sport = (request.POST.get("sport") or "").strip()  # ✅ new

        # --- validations ---
        if not all([username, first_name, last_name, email, password1, password2, sport]):
            messages.error(request, "Please fill in all fields, including sport.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        try:
            validate_email(email)
        except ValidationError:


            messages.error(request, "Please enter a valid email address.")
            return render(request, "auth/register.html")

            messages.error(request, "Please enter a valid email address (e.g., user@example.com).")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with that email already exists.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})


        # --- create user and login ---

        # --- create user ---
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )

        # create CoachProfile with sport
        CoachProfile.objects.create(user=user, sport=sport)

        login(request, user)
        return redirect("coach_dashboard")

    # GET request
    return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})