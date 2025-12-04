from django.db import models
from django.contrib.auth.models import User

# ----------------------------
# COACH PROFILE MODEL
# ----------------------------
class CoachProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    SPORT_CHOICES = [
        ("Basketball", "Basketball"),
        ("Football", "Football"),
        ("Soccer", "Soccer"),
        ("Baseball", "Baseball"),
        ("Volleyball", "Volleyball"),
        ("Track & Field", "Track & Field"),
        ("Tennis", "Tennis"),
        ("Swimming", "Swimming"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sport = models.CharField(max_length=30, choices=SPORT_CHOICES)
    
    # Fields needed to resolve the previous AttributeErrors:
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} - {self.sport}"

# ... (Rest of models.py continues with Player, Team, and Event models)

# ----------------------------
# PLAYER MODEL
# ----------------------------
class Player(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    # We use "Team" in quotes because Team is defined further down in the file
    team = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    jersey_number = models.CharField(max_length=10, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None


# ----------------------------
# TEAM MODEL
# ----------------------------
class Team(models.Model):
    name = models.CharField(max_length=100)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")
    sport = models.CharField(max_length=100, default="")
    season = models.CharField(max_length=50, blank=True, null=True)

    max_players_allowed = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Inactive", "Inactive"),
            ("Archived", "Archived"),
        ],
        default="Active",
    )

    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# ----------------------------
# EVENT MODEL
# ----------------------------
class Event(models.Model):
    EVENT_TYPES = [
        ('Game', 'Game'),
        ('Practice', 'Practice'),
    ]

    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    opponent = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"


# ----------------------------
# ATTENDANCE MODEL
# ----------------------------
class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendances')
    present = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('event', 'player'),)

    def __str__(self):
        return f"{self.player.name} - {self.event.title}: {'Present' if self.present else 'Absent'}"


# ----------------------------
# GAME + PLAYER STAT MODELS
# ----------------------------
class Game(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    # Optional link to an Event so games saved from an Event modal can be associated
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='games')
    title = models.CharField(max_length=255, blank=True, null=True)
    opponent = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    is_win = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} vs {self.opponent or 'Opponent'} - {self.date}"


class PlayerStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_stats')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')

    two_pt_made = models.IntegerField(default=0)
    two_pt_att = models.IntegerField(default=0)
    three_pt_made = models.IntegerField(default=0)
    three_pt_att = models.IntegerField(default=0)
    ft_made = models.IntegerField(default=0)
    ft_att = models.IntegerField(default=0)
    rebound_off = models.IntegerField(default=0)
    rebound_def = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    steals = models.IntegerField(default=0)
    blocks = models.IntegerField(default=0)
    turnovers = models.IntegerField(default=0)
    fouls = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    class Meta:
        unique_together = (('game', 'player'),)

    def __str__(self):
        return f"{self.player.name} - {self.game}: {self.total_points} pts"