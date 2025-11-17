from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Player, Team, CoachProfile 


# -------------------------------
# Landing Page View
# -------------------------------
def landing_page(request):
    return render(request, "auth/landing_page.html")


# -------------------------------
# Login View
# -------------------------------
def login_view(request):

    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        actual_username = None

        # If identifier is email
        if "@" in identifier:
            u = User.objects.filter(email__iexact=identifier).first()
            if u:
                actual_username = u.username

        # Try username or fallback to email lookup
        if not actual_username:
            if User.objects.filter(username__iexact=identifier).exists():
                actual_username = identifier
            else:
                u = User.objects.filter(email__iexact=identifier).first()
                if u:
                    actual_username = u.username

        user = authenticate(request, username=actual_username or "", password=password)
        if user:
            login(request, user)
            return redirect("coach_dashboard")
        else:
            messages.error(request, "Invalid login credentials.")

    return render(request, "auth/login.html")


# -------------------------------
# Coach Dashboard
# -------------------------------
@login_required(login_url="login")
def coach_dashboard(request):

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
                sport=coach_profile.sport if coach_profile else "",
                location=location,
                max_players_allowed=max_players_allowed,
                status=status,
            )

            messages.success(request, f'Team "{name}" created successfully!')
            return redirect("coach_dashboard")

    teams = Team.objects.filter(coach=request.user)

    return render(
        request,
        "team_mgmt/coach_dashboard.html",
        {
            "teams": teams,
            "coach_profile": coach_profile,
        },
    )


# -------------------------------
# Register View
# -------------------------------
def register_view(request):

    if request.method == "POST":

        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""
        sport = (request.POST.get("sport") or "").strip()

        # VALIDATIONS
        if not all([username, first_name, last_name, email, password1, password2, sport]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})

        # CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )

        CoachProfile.objects.create(user=user, sport=sport)

        login(request, user)
        return redirect("coach_dashboard")

    return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})


# -------------------------------
# Team Detail View
# -------------------------------
@login_required(login_url="login")
def team_detail(request, team_id):

    team = get_object_or_404(Team, id=team_id, coach=request.user)

    # ✔ FIXED: Show only players assigned to this team
    players = Player.objects.filter(team=team)

    return render(
        request,
        "team_mgmt/team_detail.html",
        {
            "team": team,
            "players": players,
        },
    )


# -------------------------------
# Edit Team
# -------------------------------
@login_required(login_url="login")
def edit_team(request, team_id):

    team = get_object_or_404(Team, id=team_id, coach=request.user)

    if request.method == "POST":
        team.name = (request.POST.get("team_name") or "").strip()
        team.sport = (request.POST.get("sport") or "").strip()
        team.season = (request.POST.get("season") or "").strip()
        team.location = (request.POST.get("location") or "").strip()
        team.max_players_allowed = request.POST.get("max_players_allowed") or 0
        team.status = request.POST.get("status") or "Active"

        if not team.name:
            messages.error(request, "Team name is required.")
        else:
            team.save()
            messages.success(request, f'Team "{team.name}" updated successfully!')
            return redirect("team_detail", team_id=team.id)

    return redirect("team_detail", team_id=team_id)


# -------------------------------
# Add Player
# -------------------------------
@login_required(login_url="login")
def add_player(request, team_id):

    team = get_object_or_404(Team, id=team_id, coach=request.user)

    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        jersey_number = request.POST.get("jersey_number") or None
        position = (request.POST.get("position") or "").strip()

        if not first_name or not last_name:
            messages.error(request, "First name and last name are required.")
        else:
            Player.objects.create(
                coach=request.user,
                team=team,   # ⭐ FIXED: assign to team
                name=f"{first_name} {last_name}",
                first_name=first_name,
                last_name=last_name,
                email=email,
                jersey_number=jersey_number,
                position=position,
            )

            messages.success(request, f'Player "{first_name} {last_name}" added successfully!')
            return redirect("team_detail", team_id=team.id)

    return redirect("team_detail", team_id=team.id)


# -------------------------------
# Edit Player
# -------------------------------
@login_required(login_url="login")
def edit_player(request, team_id, player_id):

    team = get_object_or_404(Team, id=team_id, coach=request.user)
    player = get_object_or_404(Player, id=player_id, team=team)  # ✔ restrict to this team

    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        player.email = (request.POST.get("email") or "").strip()
        player.jersey_number = request.POST.get("jersey_number") or None
        player.position = (request.POST.get("position") or "").strip()

        if not first_name or not last_name:
            messages.error(request, "First name and last name are required.")
        else:
            player.first_name = first_name
            player.last_name = last_name
            player.name = f"{first_name} {last_name}"
            player.save()
            messages.success(request, f'Player "{player.name}" updated successfully!')
            return redirect("team_detail", team_id=team.id)

    return redirect("team_detail", team_id=team_id)


# -------------------------------
# Remove Player
# -------------------------------
@login_required(login_url="login")
def remove_player(request, team_id, player_id):

    team = get_object_or_404(Team, id=team_id, coach=request.user)
    player = get_object_or_404(Player, id=player_id, team=team)  # ✔ restrict deletion

    if request.method == "POST":
        player_name = player.name
        player.delete()
        messages.success(request, f'Player "{player_name}" removed successfully!')

    return redirect("team_detail", team_id=team.id)
