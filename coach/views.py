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
from django.db import models
from .models import Player, Team, CoachProfile, Event, Attendance, PlayerStat, Game


# ===============================
# AUTHENTICATION VIEWS
# ===============================

def landing_page(request):
    """Landing page view"""
    return render(request, "auth/landing_page.html")


def login_view(request):
    """Handle user login"""
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


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("landing_page")


def register_view(request):
    """Handle user registration"""
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""


        # VALIDATIONS
        if not all([username, first_name, last_name, email, password1, password2]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "auth/register.html")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, "auth/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/register.html")

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "auth/register.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "auth/register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, "auth/register.html")

        # CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )

        CoachProfile.objects.create(user=user, sport="Other")

        messages.success(request, "Account created successfully! Please sign in below.")
        return redirect("login")

    return render(request, "auth/register.html")


# ===============================
# PROFILE VIEWS
# ===============================

@login_required(login_url='login')
def profile_view(request):
    """Handle profile details view and edit"""
    coach_profile, created = CoachProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        print(f"DEBUG: Profile POST received. FILES keys: {request.FILES.keys()}")
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Helper to convert empty strings to None
        def clean_input(val):
            return val.strip() if val and val.strip() else None

        coach_profile.birthday = clean_input(request.POST.get('birthday'))
        coach_profile.gender = clean_input(request.POST.get('gender'))
        
        if 'profile_picture' in request.FILES:
            print("DEBUG: profile_picture found in request.FILES")
            coach_profile.profile_picture = request.FILES['profile_picture']
        else:
            print("DEBUG: profile_picture NOT in request.FILES")

        user.save()
        coach_profile.save()
        print(f"DEBUG: Profile saved. Current picture: {coach_profile.profile_picture}")
        
        messages.success(request, "Your profile has been updated.")
        return redirect('profile')

    print("DEBUG: Loading profile_view using auth/profile_v3.html")
    return render(request, 'auth/profile_v3.html', {
        'coach_profile': coach_profile,
        'user': request.user
    })


@login_required(login_url="login")
def change_password(request):
    """Handle password change"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'auth/change_password.html', {'form': form})


# ===============================
# DASHBOARD & MAIN VIEWS
# ===============================

@login_required(login_url="login")
def coach_dashboard(request):
    """Main dashboard view"""
    coach_profile = CoachProfile.objects.filter(user=request.user).first()

    today = timezone.now().date()
    
    # Handle Create Team Form
    if request.method == "POST":
        name = (request.POST.get("team_name") or "").strip()
        location = (request.POST.get("location") or "").strip()
        max_players_allowed = request.POST.get("max_players_allowed") or 0
        status = request.POST.get("status") or "Active"

        if not name:
            messages.error(request, "Team name is required.")
        else:
            sport_selection = request.POST.get("sport")
            Team.objects.create(
                coach=request.user,
                name=name,
                sport=sport_selection if sport_selection else (coach_profile.sport if coach_profile else ""),
                location=location,
                max_players_allowed=max_players_allowed,
                status=status,
            )
            messages.success(request, f'Team "{name}" created successfully!')
            return redirect("coach_dashboard")

    # Fetch Teams & Players
    teams = Team.objects.filter(coach=request.user)
    all_players = Player.objects.filter(team__in=teams).select_related('team').order_by('team__name', 'last_name')

    # Build latest attendance per player
    # Build Attendance Ratio & Latest Status
    player_attendance_map = {}
    if all_players.exists():
        # 1. Total Events per Team
        # We count ALL events (past and future) as requested
        team_event_counts = {}
        for t in teams:
            count = Event.objects.filter(team=t).count()
            team_event_counts[t.id] = count

        # 2. Player Attendance Counts (Present=True) - for ALL events
        player_present_counts = {}
        attendance_records = Attendance.objects.filter(
            player__in=all_players, 
            present=True
        )
        for att in attendance_records:
            player_present_counts[att.player_id] = player_present_counts.get(att.player_id, 0) + 1

        # 3. Latest Attendance (Existing Logic)
        player_attendance_map = {}
        att_qs = Attendance.objects.filter(player__in=all_players).select_related('player', 'event').order_by('player_id', '-recorded_at')
        seen_players = set()
        for att in att_qs:
            if att.player_id not in seen_players:
                player_attendance_map[att.player_id] = {
                    'present': att.present,
                    'event_id': att.event_id,
                    'event_title': att.event.title,
                }
                seen_players.add(att.player_id)

        # 4. Attach to Player Objects
        for p in all_players:
            p.latest_attendance = player_attendance_map.get(p.id)
            
            # Ratio Calculation
            total_events = team_event_counts.get(p.team_id, 0)
            present_count = player_present_counts.get(p.id, 0)
            p.attendance_ratio = f"{present_count}/{total_events}" if total_events > 0 else "0/0"


    # Fetch & Sort Events
    all_events = Event.objects.filter(coach=request.user).select_related('team')
    
    upcoming_events = all_events.filter(date__gte=today).order_by('date', 'time')
    past_events = all_events.filter(date__lt=today).order_by('-date', '-time')

    # Prepare Data for Calendar (JSON)
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

    # Prepare players grouped by team
    players_by_team = {}
    for t in teams:
        ps = Player.objects.filter(team=t).order_by('last_name', 'first_name')
        players_by_team[t.id] = [
            {'id': p.id, 'name': p.name, 'jersey': p.jersey_number or ''} for p in ps
        ]

    return render(
        request,
        "team_mgmt/coach_dashboard_v2.html",
        {
            "teams": teams,
            "coach_profile": coach_profile,
            "all_players": all_players,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "events_json": events_json,
            "player_attendance_map": player_attendance_map,
            "players_by_team": players_by_team,
        },
    )


@login_required(login_url="login")
def teams_view(request):
    """Teams view - redirects to dashboard"""
    return redirect('coach_dashboard')


@login_required(login_url="login")
def players_view(request):
    """Players list view"""
    teams = Team.objects.filter(coach=request.user)
    players = Player.objects.filter(team__in=teams)
    
    return render(request, "team_mgmt/players_list.html", {"players": players})


@login_required(login_url="login")
def schedule_view(request):
    """Schedule view - redirects to dashboard schedule tab"""
    return redirect(f"{reverse('coach_dashboard')}?tab=schedule")


# ===============================
# TEAM MANAGEMENT VIEWS
# ===============================

@login_required(login_url="login")
def team_detail(request, team_id):
    """Team detail view"""
    team = get_object_or_404(Team, id=team_id, coach=request.user)
    players = Player.objects.filter(team=team)
    practices = Event.objects.filter(team=team, event_type='Practice').order_by('-date', '-time')

    # Compute wins/losses from Game objects
    games = Game.objects.filter(team=team).order_by('-date')
    wins = games.filter(is_win=True).count()
    losses = games.filter(is_win=False).count()

    # Calculate Attendance Ratio
    total_events = Event.objects.filter(team=team).count()
    player_attendance = Attendance.objects.filter(event__team=team, present=True).values('player').annotate(count=models.Count('player'))
    attendance_map = {item['player']: item['count'] for item in player_attendance}

    for p in players:
        present_count = attendance_map.get(p.id, 0)
        p.attendance_ratio = f"{present_count}/{total_events}" if total_events > 0 else "0/0"

    return render(
        request,
        "team_mgmt/team_detail_final.html",
        {
            "team": team,
            "players": players,
            "practices": practices,
            "games": games,
            "wins": wins,
            "losses": losses,
        },
    )


@login_required(login_url="login")
def edit_team(request, team_id):
    """Edit team details"""
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


@login_required(login_url="login")
def delete_team(request, team_id):
    """Delete a team"""
    team = get_object_or_404(Team, id=team_id, coach=request.user)

    if request.method == "POST":
        team_name = team.name
        team.delete()
        messages.success(request, f"Team '{team_name}' has been successfully removed.")
        return redirect('coach_dashboard')
    
    return redirect('team_detail', team_id=team_id)


# ===============================
# PLAYER MANAGEMENT VIEWS
# ===============================

@login_required(login_url="login")
def add_player(request, team_id):
    """Add a player to a team"""
    team = get_object_or_404(Team, id=team_id, coach=request.user)

    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        jersey_number = request.POST.get("jersey_number") or None
        position = (request.POST.get("position") or "").strip()

        if not first_name or not last_name:
            messages.error(request, "First name and last name are required.")
        elif team.max_players_allowed > 0 and team.player_set.count() >= team.max_players_allowed:
            messages.error(request, f"Cannot add player. Team has reached max capacity of {team.max_players_allowed}.")
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


@login_required(login_url="login")
def edit_player(request, team_id, player_id):
    """Edit player details"""
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


@login_required(login_url="login")
def remove_player(request, team_id, player_id):
    """Remove a player from a team"""
    team = get_object_or_404(Team, id=team_id, coach=request.user)
    player = get_object_or_404(Player, id=player_id, team=team)

    if request.method == "POST":
        player_name = player.name
        player.delete()
        messages.success(request, f'Player "{player_name}" removed successfully!')

    return redirect("team_detail", team_id=team.id)


# ===============================
# EVENT MANAGEMENT VIEWS
# ===============================

@login_required(login_url="login")
def add_event(request):
    """Add a new event"""
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

        event = Event.objects.create(
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

        # Auto-create attendance records for all team players
        # Default to present=False (Absent) initially
        players = team.player_set.all()
        attendance_batch = [
            Attendance(event=event, player=player, present=False)
            for player in players
        ]
        Attendance.objects.bulk_create(attendance_batch)
        messages.success(request, "Event scheduled successfully!")
        
        return redirect(f"{reverse('coach_dashboard')}?tab=schedule")

    return redirect("coach_dashboard")


@login_required(login_url="login")
def edit_event(request, event_id):
    """Edit an event"""
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


@login_required(login_url="login")
def delete_event(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id, coach=request.user)
    
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event removed successfully!")
        return redirect(f"{reverse('coach_dashboard')}?tab=schedule")
        
    return redirect("coach_dashboard")


# ===============================
# ATTENDANCE VIEWS
# ===============================

@login_required(login_url="login")
def event_attendance(request, event_id):
    """Handle event attendance (GET players, POST to save)"""
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
        return JsonResponse({
            'event_id': event.id,
            'team_id': event.team.id,
            'players': players_data
        })

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


# ===============================
# STATISTICS VIEWS
# ===============================

@login_required(login_url="login")
def get_games_by_team(request, team_id):
    """API endpoint to get games and opponents for a specific team"""
    team = get_object_or_404(Team, id=team_id, coach=request.user)
    
    # Get all game events for this team
    game_events = Event.objects.filter(
        team=team, 
        event_type='Game'
    ).order_by('-date')
    
    # Build games list
    games = []
    opponents = set()
    
    for event in game_events:
        games.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'opponent': event.opponent or 'N/A'
        })
        if event.opponent:
            opponents.add(event.opponent)
    
    return JsonResponse({
        'games': games,
        'opponents': list(opponents),
        'sport': team.sport
    })


@login_required(login_url="login")
def stats_view(request):
    """Statistics page view"""
    teams = Team.objects.filter(coach=request.user)
    
    # Build players by team with jersey numbers
    players_by_team = {}
    for team in teams:
        players = Player.objects.filter(team=team).order_by('last_name', 'first_name')
        players_by_team[team.id] = [
            {
                'id': p.id,
                'name': f"{p.first_name} {p.last_name}",
                'jersey': p.jersey_number or ''
            }
            for p in players
        ]
    
        print("Loading template: team_mgmt/statistics.html")  # Add this line
    
    return render(request, 'team_mgmt/statistics.html', {
        'teams': teams,
        'players_by_team': json.dumps(players_by_team, cls=DjangoJSONEncoder)
    })

    return render(request, 'team_mgmt/statistics.html', {
        'teams': teams,
        'players_by_team': json.dumps(players_by_team, cls=DjangoJSONEncoder)
    })


@login_required(login_url="login")
def save_game_stats(request):
    """Save game statistics"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        game_data = data.get('game', {})
        stats_data = data.get('stats', {})
        
        team_id = game_data.get('team_id')
        event_id = game_data.get('event_id')
        
        team = get_object_or_404(Team, id=team_id, coach=request.user)
        event = get_object_or_404(Event, id=event_id, team=team, coach=request.user)
        
        # Create or update Game record
        game, created = Game.objects.update_or_create(
            team=team,
            event=event,
            defaults={
                'coach': request.user,
                'date': game_data.get('date'),
                'opponent': game_data.get('opponent', ''),
                'title': event.title,
                'is_win': game_data.get('is_win', False),
            }
        )
        
        # Delete existing stats for this game (in case of re-saving)
        PlayerStat.objects.filter(game=game).delete()
        
        # Save player stats
        saved_count = 0
        for player_id, stats in stats_data.items():
            try:
                player = Player.objects.get(id=int(player_id), team=team)
                
                # Create PlayerStat with all the stats from the form
                PlayerStat.objects.create(
                    player=player,
                    game=game,
                    **stats  # Unpack all stats from the dictionary
                )
                saved_count += 1
            except (Player.DoesNotExist, ValueError) as e:
                print(f"Error saving stats for player {player_id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Stats saved successfully for {saved_count} players',
            'game_id': game.id
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e)
        }, status=400)


@login_required(login_url='login')
def event_stats(request, event_id):
    """Return the Game (if any) associated with this Event and its player stats"""
    event = get_object_or_404(Event, id=event_id, coach=request.user)

    # Get the game linked to this event
    game = Game.objects.filter(event=event).order_by('-date', '-created_at').first()
    if not game:
        return JsonResponse({'game': None, 'stats': {}})

    stats = {}
    for ps in game.player_stats.select_related('player').all():
        stats[ps.player.id] = {
            'player_id': ps.player.id,
            'player_name': ps.player.name,
            'two_pt_made': ps.two_pt_made,
            'two_pt_attempt': ps.two_pt_attempt,
            'three_pt_made': ps.three_pt_made,
            'three_pt_attempt': ps.three_pt_attempt,
            'ft_made': ps.ft_made,
            'ft_attempt': ps.ft_attempt,
            'rebounds': ps.rebounds,
            'assists': ps.assists,
            'steals': ps.steals,
            'blocks': ps.blocks,
            'turnovers': ps.turnovers,
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
    """Get player statistics history"""
    player = get_object_or_404(Player, id=player_id, team__coach=request.user)
    stats_qs = PlayerStat.objects.filter(player=player).select_related('game').order_by('-game__date')
    
    data = []
    for s in stats_qs:
        data.append({
            'game_id': s.game.id,
            'date': s.game.date.strftime('%Y-%m-%d'),
            'opponent': s.game.opponent,
            'team': s.game.team.name,
            'two_pt_made': s.two_pt_made,
            'two_pt_attempt': s.two_pt_attempt,
            'three_pt_made': s.three_pt_made,
            'three_pt_attempt': s.three_pt_attempt,
            'ft_made': s.ft_made,
            'ft_attempt': s.ft_attempt,
            'rebounds': s.rebounds,
            'assists': s.assists,
            'steals': s.steals,
            'blocks': s.blocks,
            'turnovers': s.turnovers,
        })
    
    return JsonResponse({
        'player': {'id': player.id, 'name': player.name},
        'history': data
    })


@login_required(login_url='login')
def player_stats_page(request, player_id):
    """Render the player history HTML page"""
    player = get_object_or_404(Player, id=player_id, team__coach=request.user)
    return render(request, "team_mgmt/player_stats.html", {'player_id': player.id})

@login_required(login_url="login")
def get_event_details(request, event_id):
    """API to get event details and player attendance status"""
    event = get_object_or_404(Event, id=event_id, coach=request.user)
    
    # Get all players for this team
    players = Player.objects.filter(team=event.team).order_by('last_name')
    
    # Get existing attendance records for this event
    attendance_map = {
        att.player_id: att.present 
        for att in Attendance.objects.filter(event=event)
    }
    
    players_data = []
    for p in players:
        players_data.append({
            'id': p.id,
            'name': p.name,
            'jersey': p.jersey_number,
            'is_present': attendance_map.get(p.id, False) # Default to False if no record
        })
        
    data = {
        'id': event.id,
        'title': event.title,
        'event_type': event.event_type,
        'date': event.date.strftime('%B %d, %Y'), # e.g. November 15, 2025
        'time': event.time.strftime('%I:%M %p'),  # e.g. 7:00 PM
        'location': event.location,
        'opponent': event.opponent,
        'notes': event.notes,
        'players': players_data
    }
    return JsonResponse(data)


@login_required(login_url="login")
def mark_attendance(request, event_id):
    """API to save attendance"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
        
    event = get_object_or_404(Event, id=event_id, coach=request.user)
    
    try:
        data = json.loads(request.body)
        present_player_ids = set(data.get('present_player_ids', []))
        
        # Get all players for the team to ensure we handle "absent" ones too
        all_players = Player.objects.filter(team=event.team)
        
        for player in all_players:
            is_present = player.id in present_player_ids
            Attendance.objects.update_or_create(
                event=event,
                player=player,
                defaults={
                    'present': is_present,
                    'recorded_by': request.user
                }
            )
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
