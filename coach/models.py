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
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sport}"


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
# PLAYER MODEL
# ----------------------------
class Player(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    jersey_number = models.CharField(max_length=10, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
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

    class Meta:
        ordering = ['-date', '-time']

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
# GAME MODEL
# ----------------------------
class Game(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='games')
    title = models.CharField(max_length=255, blank=True, null=True)
    opponent = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    is_win = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        result = "Win" if self.is_win else "Loss"
        return f"{self.team.name} vs {self.opponent or 'Opponent'} - {result} ({self.date})"


# ----------------------------
# PLAYER STAT MODEL
# ----------------------------
class PlayerStat(models.Model):
    """Stores statistics for a player in a specific game - supports multiple sports"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_stats')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')

    # Basketball stats
    two_pt_made = models.IntegerField(default=0, null=True, blank=True)
    two_pt_attempt = models.IntegerField(default=0, null=True, blank=True)
    three_pt_made = models.IntegerField(default=0, null=True, blank=True)
    three_pt_attempt = models.IntegerField(default=0, null=True, blank=True)
    ft_made = models.IntegerField(default=0, null=True, blank=True)
    ft_attempt = models.IntegerField(default=0, null=True, blank=True)
    rebounds = models.IntegerField(default=0, null=True, blank=True)
    assists = models.IntegerField(default=0, null=True, blank=True)
    steals = models.IntegerField(default=0, null=True, blank=True)
    blocks = models.IntegerField(default=0, null=True, blank=True)
    turnovers = models.IntegerField(default=0, null=True, blank=True)

    # Soccer stats
    goals = models.IntegerField(default=0, null=True, blank=True)
    shots = models.IntegerField(default=0, null=True, blank=True)
    shots_on_target = models.IntegerField(default=0, null=True, blank=True)
    saves = models.IntegerField(default=0, null=True, blank=True)
    tackles = models.IntegerField(default=0, null=True, blank=True)
    fouls = models.IntegerField(default=0, null=True, blank=True)
    yellow_cards = models.IntegerField(default=0, null=True, blank=True)
    red_cards = models.IntegerField(default=0, null=True, blank=True)

    # Football stats
    pass_completions = models.IntegerField(default=0, null=True, blank=True)
    pass_attempts = models.IntegerField(default=0, null=True, blank=True)
    passing_yards = models.IntegerField(default=0, null=True, blank=True)
    touchdowns = models.IntegerField(default=0, null=True, blank=True)
    interceptions = models.IntegerField(default=0, null=True, blank=True)
    rushing_yards = models.IntegerField(default=0, null=True, blank=True)
    receptions = models.IntegerField(default=0, null=True, blank=True)
    receiving_yards = models.IntegerField(default=0, null=True, blank=True)
    sacks = models.IntegerField(default=0, null=True, blank=True)

    # Baseball stats
    at_bats = models.IntegerField(default=0, null=True, blank=True)
    hits = models.IntegerField(default=0, null=True, blank=True)
    runs = models.IntegerField(default=0, null=True, blank=True)
    rbis = models.IntegerField(default=0, null=True, blank=True)
    home_runs = models.IntegerField(default=0, null=True, blank=True)
    strikeouts = models.IntegerField(default=0, null=True, blank=True)
    walks = models.IntegerField(default=0, null=True, blank=True)
    stolen_bases = models.IntegerField(default=0, null=True, blank=True)

    # Volleyball stats
    kills = models.IntegerField(default=0, null=True, blank=True)
    attacks = models.IntegerField(default=0, null=True, blank=True)
    aces = models.IntegerField(default=0, null=True, blank=True)
    digs = models.IntegerField(default=0, null=True, blank=True)
    errors = models.IntegerField(default=0, null=True, blank=True)

    # Track & Field stats
    time_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attempts = models.IntegerField(default=0, null=True, blank=True)

    # Tennis stats
    double_faults = models.IntegerField(default=0, null=True, blank=True)
    winners = models.IntegerField(default=0, null=True, blank=True)
    unforced_errors = models.IntegerField(default=0, null=True, blank=True)
    break_points_won = models.IntegerField(default=0, null=True, blank=True)

    # Swimming stats
    strokes = models.IntegerField(default=0, null=True, blank=True)
    splits = models.CharField(max_length=200, null=True, blank=True)
    place = models.IntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('game', 'player')
        ordering = ['-game__date']

    def __str__(self):
        return f"{self.player.name} - {self.game}"

    def calculate_basketball_points(self):
        """Calculate total points for basketball"""
        return (
            (self.two_pt_made or 0) * 2 +
            (self.three_pt_made or 0) * 3 +
            (self.ft_made or 0)
        )