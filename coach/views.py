import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.urls import reverse
from .models import Player, Team, CoachProfile, Event, Attendance
from .models import PlayerStat, Game

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

        # Logic to look up user by email or username
        if "@" in identifier:
            u = User.objects.filter(email__iexact=identifier).first()
            if u:
                actual_username = u.username

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
# Logout View
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

    # --- 3a. Build latest attendance per player (most recently recorded attendance)
    player_attendance_map = {}
    if all_players.exists():
        # Get Attendance entries for these players ordered by player then newest recorded_at
        att_qs = Attendance.objects.filter(player__in=all_players).select_related('player', 'event').order_by('player_id', '-recorded_at')
        for att in att_qs:
            pid = att.player_id
            if pid not in player_attendance_map:
                player_attendance_map[pid] = {
                    'present': att.present,
                    'event_id': att.event_id,
                    'event_title': att.event.title,
                    'event_date': att.event.date.strftime('%Y-%m-%d') if att.event.date else None,
                    'recorded_at': att.recorded_at,
                }
        # Attach latest attendance as attribute on player objects for easy template access
        for p in all_players:
            p.latest_attendance = player_attendance_map.get(p.id)

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

    # prepare players grouped by team for dashboard (same shape as stats view expects)
    players_by_team = {}
    for t in teams:
        ps = Player.objects.filter(team=t).order_by('last_name', 'first_name')
        players_by_team[t.id] = [
            { 'id': p.id, 'name': p.name, 'jersey': p.jersey_number or '' } for p in ps
        ]

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
            "player_attendance_map": player_attendance_map,
            "players_by_team": json.dumps(players_by_team),
        },
    )

# -------------------------------
# Teams View (For URL tab)
# -------------------------------
@login_required(login_url="login")
def teams_view(request):
    # This view redirects to the dashboard to show the teams list.
    return redirect('coach_dashboard') 

# -------------------------------
# Players View (For URL tab)
# -------------------------------
@login_required(login_url="login")
def players_view(request):
    teams = Team.objects.filter(coach=request.user)
    players = Player.objects.filter(team__in=teams)
    
    return render(request, "team_mgmt/players_list.html", {"players": players})

# -------------------------------
# Schedule View (For URL tab)
# -------------------------------
@login_required(login_url="login")
def schedule_view(request):
    # This view redirects to the dashboard to show the schedule list.
    return redirect(f"{reverse('coach_dashboard')}?tab=schedule")

# -------------------------------
# Stats View (For URL tab)
# -------------------------------
@login_required(login_url="login")
def stats_view(request):
    # Render the statistics page where coaches can enter per-game stats
    teams = Team.objects.filter(coach=request.user)

    # Prepare players grouped by team for client-side rendering
    players_by_team = {}
    for t in teams:
        ps = Player.objects.filter(team=t).order_by('last_name', 'first_name')
        players_by_team[t.id] = [
            { 'id': p.id, 'name': p.name, 'jersey': p.jersey_number or '' } for p in ps
        ]

    return render(request, "team_mgmt/statistics.html", {"teams": teams, "players_by_team": json.dumps(players_by_team)})


@login_required(login_url='login')
def save_game_stats(request):
    # Expects JSON payload with game info and player stats
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    game_info = payload.get('game') or {}
    stats = payload.get('stats') or {}

    team_id = game_info.get('team_id')
    date = game_info.get('date')
    title = game_info.get('title')
    opponent = game_info.get('opponent')
    is_win = bool(game_info.get('is_win'))

    if not team_id or not date:
        return JsonResponse({'error': 'team_id and date required'}, status=400)

    team = get_object_or_404(Team, id=team_id, coach=request.user)

    # Optionally link this Game to an existing Event (if saving from an Event modal)
    event_id = game_info.get('event_id')
    event_obj = None
    if event_id:
        try:
            event_obj = Event.objects.get(id=int(event_id), coach=request.user)
        except Exception:
            event_obj = None

    # If no explicit event_id provided, try to associate by team+date for Game events
    if not event_obj:
        try:
            match_event = Event.objects.filter(team=team, date=date, event_type='Game').first()
            if match_event:
                event_obj = match_event
        except Exception:
            event_obj = None

    game = Game.objects.create(
        coach=request.user,
        team=team,
        event=event_obj,
        title=title,
        opponent=opponent,
        date=date,
        is_win=is_win,
    )

    saved = 0
    for pid_str, row in stats.items():
        try:
            pid = int(pid_str)
        except Exception:
            continue
        try:
            player = Player.objects.get(id=pid, team=team)
        except Player.DoesNotExist:
            continue

        ps_obj = PlayerStat.objects.create(
            game=game,
            player=player,
            two_pt_made=int(row.get('two_pt_made') or 0),
            two_pt_att=int(row.get('two_pt_att') or 0),
            three_pt_made=int(row.get('three_pt_made') or 0),
            three_pt_att=int(row.get('three_pt_att') or 0),
            ft_made=int(row.get('ft_made') or 0),
            ft_att=int(row.get('ft_att') or 0),
            rebound_off=int(row.get('rebound_off') or 0),
            rebound_def=int(row.get('rebound_def') or 0),
            assists=int(row.get('assists') or 0),
            steals=int(row.get('steals') or 0),
            blocks=int(row.get('blocks') or 0),
            turnovers=int(row.get('turnovers') or 0),
            fouls=int(row.get('fouls') or 0),
            total_points=int(row.get('total_points') or 0),
        )
        saved += 1

    return JsonResponse({'success': True, 'saved': saved, 'game_id': game.id})


@login_required(login_url='login')
def event_stats(request, event_id):
    # Return the Game (if any) associated with this Event and its player stats
    event = get_object_or_404(Event, id=event_id, coach=request.user)

    # There may be zero or more games linked; pick the most recent by date/created
    game = Game.objects.filter(event=event).order_by('-date', '-created_at').first()
    if not game:
        return JsonResponse({'game': None, 'stats': {} })

    stats = {}
    for ps in game.player_stats.select_related('player').all():
        stats[ps.player.id] = {
            'player_id': ps.player.id,
            'player_name': ps.player.name,
            'two_pt_made': ps.two_pt_made,
            'two_pt_att': ps.two_pt_att,
            'three_pt_made': ps.three_pt_made,
            'three_pt_att': ps.three_pt_att,
            'ft_made': ps.ft_made,
            'ft_att': ps.ft_att,
            'rebound_off': ps.rebound_off,
            'rebound_def': ps.rebound_def,
            'assists': ps.assists,
            'steals': ps.steals,
            'blocks': ps.blocks,
            'turnovers': ps.turnovers,
            'fouls': ps.fouls,
            'total_points': ps.total_points,
        }

    game_data = {
        'id': game.id,
        'team_id': game.team.id,
        'date': game.date.strftime('%Y-%m-%d'),
        'opponent': game.opponent,
        'title': game.title,
        'is_win': game.is_win,
    }

    return JsonResponse({'game': game_data, 'stats': stats})


@login_required(login_url='login')
def player_stats_history(request, player_id):
    player = get_object_or_404(Player, id=player_id, coach=request.user)
    stats_qs = PlayerStat.objects.filter(player=player).select_related('game').order_by('-game__date')
    data = []
    for s in stats_qs:
        data.append({
            'game_id': s.game.id,
            'date': s.game.date.strftime('%Y-%m-%d'),
            'opponent': s.game.opponent,
            'team': s.game.team.name,
            'two_pt_made': s.two_pt_made,
            'two_pt_att': s.two_pt_att,
            'three_pt_made': s.three_pt_made,
            'three_pt_att': s.three_pt_att,
            'ft_made': s.ft_made,
            'ft_att': s.ft_att,
            'rebound_off': s.rebound_off,
            'rebound_def': s.rebound_def,
            'assists': s.assists,
            'steals': s.steals,
            'blocks': s.blocks,
            'turnovers': s.turnovers,
            'fouls': s.fouls,
            'total_points': s.total_points,
        })
    return JsonResponse({'player': {'id': player.id, 'name': player.name}, 'history': data})


@login_required(login_url='login')
def player_stats_page(request, player_id):
    # Render the player history HTML page
    player = get_object_or_404(Player, id=player_id, coach=request.user)
    return render(request, 'team_mgmt/player_stats.html', {'player_id': player.id})

# -------------------------------
# Profile View (Handles Profile Details Edit)
# -------------------------------
@login_required(login_url='login')
def profile_view(request):
    # Ensure a CoachProfile exists for the user
    coach_profile, created = CoachProfile.objects.get_or_create(user=request.user) 

    if request.method == "POST":
        # Handle form submission, saving updated profile data
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Update coach profile fields (assuming they exist in models.py)
        coach_profile.birthday = request.POST.get('birthday', coach_profile.birthday)
        coach_profile.gender = request.POST.get('gender', coach_profile.gender)
        
        if 'profile_picture' in request.FILES:
            coach_profile.profile_picture = request.FILES['profile_picture']

        # Save the updated information
        user.save()
        coach_profile.save()
        
        messages.success(request, "Your profile has been updated.")
        return redirect('profile')

    # Render the profile details template
    return render(request, 'auth/profile.html', {'coach_profile': coach_profile, 'user': request.user})

# -------------------------------
# Change Password View (Handles dedicated password change form)
# -------------------------------
@login_required(login_url="login")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for keeping user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect back to the main profile page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    # Render the dedicated password change template
    return render(request, 'auth/change_password.html', {'form': form})

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

        # Redirect to login page after successful registration
        messages.success(request, "Account created successfully! Please sign in below.")
        return redirect("login") 

    return render(request, "auth/register.html", {"sport_choices": CoachProfile.SPORT_CHOICES})


# -------------------------------
# Team Detail View
# -------------------------------
@login_required(login_url="login")
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id, coach=request.user)
    players = Player.objects.filter(team=team)
    practices = Event.objects.filter(team=team, event_type='Practice').order_by('-date', '-time')

    # Compute wins/losses from Game objects (simple on-demand computation)
    games = Game.objects.filter(team=team).order_by('-date')
    wins = games.filter(is_win=True).count()
    losses = games.filter(is_win=False).count()

    return render(
        request,
        "team_mgmt/team_detail.html",
        {
            "team": team,
            "players": players,
            "practices": practices,
            "games": games,
            "wins": wins,
            "losses": losses,
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


# -------------------------------
# Event Attendance (GET players + existing attendance, POST to save)
# -------------------------------
@login_required(login_url="login")
def event_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id, coach=request.user)

    if request.method == 'GET':
        players = list(Player.objects.filter(team=event.team).order_by('last_name', 'first_name'))
        existing = Attendance.objects.filter(event=event)
        att_map = {a.player_id: a.present for a in existing}
        players_data = []
        for p in players:
            players_data.append({
                'id': p.id,
                'name': p.name,
                'jersey_number': p.jersey_number,
                'present': att_map.get(p.id, False),
            })
        return JsonResponse({'event_id': event.id, 'team_id': event.team.id, 'players': players_data})

    # POST: save attendance payload (expects JSON { attendance: { player_id: true/false } })
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        attendance = payload.get('attendance', {})
        updated = 0
        for pid_str, present_val in attendance.items():
            try:
                pid = int(pid_str)
            except Exception:
                continue
            try:
                player = Player.objects.get(id=pid, team=event.team)
            except Player.DoesNotExist:
                continue

            obj, created = Attendance.objects.update_or_create(
                event=event, player=player,
                defaults={'present': bool(present_val), 'recorded_by': request.user}
            )
            updated += 1

        return JsonResponse({'success': True, 'updated': updated})

    return JsonResponse({'error': 'Method not allowed'}, status=405)