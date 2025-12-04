import os
import sys
import django
import json
from datetime import date, time

# Setup Django environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_mgmt.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from coach.models import Team, Player, Event, Game, PlayerStat
from coach.views import save_game_stats, event_stats

# use first active user
user = User.objects.filter(is_active=True).first()
if not user:
    print('NO_USER')
    raise SystemExit(1)

# Ensure team and players
team, _ = Team.objects.get_or_create(name='SaveFlow Team', coach=user, defaults={'sport': 'Basketball'})
p1, _ = Player.objects.get_or_create(coach=user, team=team, name='SaveFlow Player A', defaults={'first_name':'A','last_name':'Player'})
p2, _ = Player.objects.get_or_create(coach=user, team=team, name='SaveFlow Player B', defaults={'first_name':'B','last_name':'Player'})

# Create an Event for today
today = date.today()
ev, created = Event.objects.get_or_create(coach=user, team=team, date=today, event_type='Game', defaults={'title':'SaveFlow Game','time':time(15,0),'location':'Court','opponent':'Rivals'})

# Build payload to save stats linked to the event
payload = {
    'game': {
        'team_id': team.id,
        'date': today.isoformat(),
        'title': 'SaveFlow Game',
        'opponent': 'Rivals',
        'is_win': True,
        'event_id': ev.id,
    },
    'stats': {}
}

# Stats for players
for p in (p1, p2):
    payload['stats'][str(p.id)] = {
        'two_pt_made': 2,
        'two_pt_att': 4,
        'three_pt_made': 1,
        'three_pt_att': 2,
        'ft_made': 0,
        'ft_att': 0,
        'rebound_off': 1,
        'rebound_def': 3,
        'assists': 5,
        'steals': 1,
        'blocks': 0,
        'turnovers': 2,
        'fouls': 1,
        'total_points': 2*2 + 1*3 + 0,
    }

# Call save_game_stats view via RequestFactory
rf = RequestFactory()
req = rf.post('/coach/stats/save/', data=json.dumps(payload), content_type='application/json')
req.user = user
resp = save_game_stats(req)
print('save_game_stats response:')
print(resp.content.decode('utf-8'))

# Call event_stats to verify
req2 = rf.get(f'/coach/event/{ev.id}/stats/')
req2.user = user
resp2 = event_stats(req2, ev.id)
print('\nevent_stats response:')
print(resp2.content.decode('utf-8'))
