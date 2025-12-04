import os
import django
import json
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_mgmt.settings')
# Ensure project root is on sys.path so Django can import project settings
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_mgmt.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from coach.models import Team, Player, Event, Game, PlayerStat
from coach.views import event_stats
from datetime import date, time

# Find a coach user (fall back to first user)
user = User.objects.filter(is_active=True).first()
if not user:
    print('NO_USER_FOUND')
    raise SystemExit(1)

# Create or get a team for this user
team, _ = Team.objects.get_or_create(name='Test Team (Auto)', coach=user, defaults={'sport': 'Basketball'})

# Create two players if not present
p1, _ = Player.objects.get_or_create(coach=user, team=team, name='Player One', defaults={'first_name': 'Player', 'last_name': 'One'})
p2, _ = Player.objects.get_or_create(coach=user, team=team, name='Player Two', defaults={'first_name': 'Player', 'last_name': 'Two'})

# Create or get an Event for today
today = date.today()
try:
    ev, created = Event.objects.get_or_create(coach=user, team=team, date=today, event_type='Game', defaults={'title': 'Auto Test Game', 'time': time(12, 0), 'location': 'Gym', 'opponent': 'Opponents', 'notes': 'Auto-created for test'})
except Exception as e:
    # In case a required field prevents get_or_create, create explicitly
    ev = Event.objects.create(coach=user, team=team, title='Auto Test Game', event_type='Game', date=today, time=time(12,0), location='Gym', opponent='Opponents')

# Create or get a Game linked to the Event
game, _ = Game.objects.get_or_create(coach=user, team=team, event=ev, date=ev.date, defaults={'title': ev.title, 'opponent': ev.opponent, 'is_win': True})

# Ensure player stats exist for the game
for p in (p1, p2):
    total_points = 2 * 1 + 3 * 0 + 1  # 2PT made =1, 3PT made =0, FT made =1
    PlayerStat.objects.update_or_create(
        game=game, player=p,
        defaults={
            'two_pt_made': 1, 'two_pt_att': 2,
            'three_pt_made': 0, 'three_pt_att': 0,
            'ft_made': 1, 'ft_att': 1,
            'rebound_off': 1, 'rebound_def': 2,
            'assists': 3, 'steals': 0, 'blocks': 0,
            'turnovers': 1, 'fouls': 2, 'total_points': total_points,
        }
    )

# Call the view via RequestFactory as the user
rf = RequestFactory()
req = rf.get(f'/coach/event/{ev.id}/stats/')
req.user = user
resp = event_stats(req, ev.id)

# Print JSON decoded
print(resp.content.decode('utf-8'))
