import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash # Added update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm # Added PasswordChangeForm
from django.utils import timezone
from django.urls import reverse
from .models import Player, Team, CoachProfile, Event 

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
# Logout View (New/Restored)
# -------------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("landing_page")


# -------------------------------
# Coach Dashboard
# -------------------------------
@login_required(login_url="login")
def coach_dashboard(request):
    coach_profile = CoachProfile.objects.filter(user=request.user).first()

    # --- 1. Handle Create Team Form ---
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

    # --- 2. Fetch Teams & Players ---
    teams = Team.objects.filter(coach=request.user)
    all_players = Player.objects.filter(team__in=teams).select_related('team').order_by('team__name', 'last_name')

    # --- 3. Fetch & Sort Events ---
    today = timezone.now().date()
    all_events = Event.objects.filter(coach=request.user).select_related('team')
    
    upcoming_events = all_events.filter(date__gte=today).order_by('date', 'time')
    past_events = all_events.filter(date__lt=today).order_by('-date', '-time')

    # --- 4. Prepare Data for Calendar (JSON) ---
    events_json = []
    for event in all_events:
        events_json.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'), 
            'time': event.time.strftime('%H:%M'), 
            'type': event.event_type,
            'location': event.location,
            'opponent': event.opponent,
            'notes': event.notes,
            'team_id': event.team.id
        })

    return render(
        request,
        "team_mgmt/coach_dashboard.html",
        {
            "teams": teams,
            "coach_profile": coach_profile,
            "all_players": all_players,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "events_json": json.dumps(events_json, cls=DjangoJSONEncoder),
        },
    )

# -------------------------------
# Teams View (New/Restored for URL tab)
# -------------------------------
@login_required(login_url="login")
def teams_view(request):
    # This view redirects to the dashboard to show the teams list.
    return redirect('coach_dashboard') 

# -------------------------------
# Players View (New/Restored for URL tab)
# -------------------------------
@login_required(login_url="login")
def players_view(request):
    teams = Team.objects.filter(coach=request.user)
    players = Player.objects.filter(team__in=teams)
    
    # In a full multi-tab dashboard, you'd render a dedicated players template here.
    return render(request, "team_mgmt/players_list.html", {"players": players})

# -------------------------------
# Schedule View (New/Restored for URL tab)
# -------------------------------
@login_required(login_url="login")
def schedule_view(request):
    # This view redirects to the dashboard to show the schedule list.
    return redirect(f"{reverse('coach_dashboard')}?tab=schedule")

# -------------------------------
# Stats View (New/Restored for URL tab)
# -------------------------------
@login_required(login_url="login")
def stats_view(request):
    # Placeholder for a dedicated stats page or redirect to dashboard with tab
    stats_data = "Statistics overview will be displayed here." 
    return render(request, "team_mgmt/stats.html", {"stats_data": stats_data})

# -------------------------------
# Profile View (New/Restored - FIXES ATTRIBUTE ERROR)
# -------------------------------
@login_required(login_url='login')
def profile_view(request):
    # 🎯 FIX FOR SYNTAX ERROR (Cleaned whitespace on this line)
    coach_profile, created = CoachProfile.objects.get_or_create(user=request.user) 

    if request.method == "POST":
        # Handle form submission, saving updated profile data
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # 🎯 FIXED LINE (coach_profile must have 'birthday' field in models.py)
        coach_profile.birthday = request.POST.get('birthday', coach_profile.birthday)
        coach_profile.gender = request.POST.get('gender', coach_profile.gender)
        
        if 'profile_picture' in request.FILES:
            coach_profile.profile_picture = request.FILES['profile_picture']

        # Save the updated information
        user.save()
        coach_profile.save()
        
        messages.success(request, "Your profile has been updated.")
        return redirect('profile')

    return render(request, 'auth/profile.html', {'coach_profile': coach_profile, 'user': request.user})

# -------------------------------
# Change Password View (New/Restored)
# -------------------------------
@login_required(login_url="login")
def change_password(request): # ❌ Removed the duplicate @login_required decorator
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for keeping user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect to profile or dashboard
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'auth/change_password.html', {'form': form})

# -------------------------------
# Register View
# -------------------------------
def register_view(request):
    # ... (Register logic is long, assume it's correctly placed here) ...
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

        # 🎯 FIX: REMOVE AUTOMATIC LOGIN AND REDIRECT TO LOGIN PAGE
        messages.success(request, "Account created successfully! Please sign in below.")
        return redirect("login") # 👈 Redirect to the login page
        # END FIX

    return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})


# -------------------------------
# Team Detail View
# -------------------------------
@login_required(login_url="login")
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id, coach=request.user)
    players = Player.objects.filter(team=team)
    practices = Event.objects.filter(team=team, event_type='Practice').order_by('-date', '-time')

    return render(
        request,
        "team_mgmt/team_detail.html",
        {
            "team": team,
            "players": players,
            "practices": practices,
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
                team=team,
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
    player = get_object_or_404(Player, id=player_id, team=team)

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
    player = get_object_or_404(Player, id=player_id, team=team)

    if request.method == "POST":
        player_name = player.name
        player.delete()
        messages.success(request, f'Player "{player_name}" removed successfully!')

    return redirect("team_detail", team_id=team.id)


# -------------------------------
# Delete Team
# -------------------------------
@login_required(login_url="login")
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id, coach=request.user)

    if request.method == "POST":
        team_name = team.name
        team.delete()
        messages.success(request, f"Team '{team_name}' has been successfully removed.")
        return redirect('coach_dashboard') 
    
    # If someone tries to access this via GET, just send them back
    return redirect('team_detail', team_id=team_id)


# -------------------------------
# Add Event View
# -------------------------------
@login_required(login_url="login")
def add_event(request):
    if request.method == "POST":
        team_id = request.POST.get("team_id")
        title = request.POST.get("title")
        event_type = request.POST.get("event_type")
        date = request.POST.get("date")
        time = request.POST.get("time")
        location = request.POST.get("location")
        opponent = request.POST.get("opponent")
        notes = request.POST.get("notes")

        team = get_object_or_404(Team, id=team_id, coach=request.user)

        Event.objects.create(
            coach=request.user,
            team=team,
            title=title,
            event_type=event_type,
            date=date,
            time=time,
            location=location,
            opponent=opponent,
            notes=notes
        )
        messages.success(request, "Event scheduled successfully!")
        
        return redirect(f"{reverse('coach_dashboard')}?tab=schedule")

    return redirect("coach_dashboard")

# -------------------------------
# Edit Event
# -------------------------------
@login_required(login_url="login")
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, coach=request.user)
    
    if request.method == "POST":
        event.title = request.POST.get("title")
        event.event_type = request.POST.get("event_type")
        event.date = request.POST.get("date")
        event.time = request.POST.get("time")
        event.location = request.POST.get("location")
        event.opponent = request.POST.get("opponent")
        event.notes = request.POST.get("notes")
        
        team_id = request.POST.get("team_id")
        if team_id:
            event.team = get_object_or_404(Team, id=team_id, coach=request.user)

        event.save()
        messages.success(request, "Event updated successfully!")
        return redirect(f"{reverse('coach_dashboard')}?tab=schedule")
        
    return redirect("coach_dashboard")

# -------------------------------
# Delete Event
# -------------------------------
@login_required(login_url="login")
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, coach=request.user)
    
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event removed successfully!")
        return redirect(f"{reverse('coach_dashboard')}?tab=schedule")
        
    return redirect("coach_dashboard")


# Schedule View
def schedule_view(request):
    # Your logic for fetching and rendering the schedule
    return render(request, 'team_mgmt/schedule.html')

# Stats View
def stats_view(request):
    # Your logic for fetching and rendering the statistics
    return render(request, 'team_mgmt/stats.html')