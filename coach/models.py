from django.db import models
from django.contrib.auth.models import User


# ----------------------------
# COACH PROFILE MODEL
# ----------------------------
class CoachProfile(models.Model):
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

    gender = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.sport}"



# ----------------------------
# PLAYER MODEL (MATCHES DATABASE)
# ----------------------------
class Player(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, blank=True)

    # DB fields
    name = models.CharField(max_length=100)
    jersey_number = models.CharField(max_length=10, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)

    # New fields (safe to add)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # ⭐ REQUIRED: exists in DB but missing before
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
