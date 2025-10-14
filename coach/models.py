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

    def __str__(self):
        return f"{self.user.username} - {self.sport}"


# ----------------------------
# PLAYER MODEL
# ----------------------------
class Player(models.Model):
    name = models.CharField(max_length=100)
    jersey_number = models.IntegerField()
    coach = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# ----------------------------
# TEAM MODEL (NO SPORT FIELD)
# ----------------------------
class Team(models.Model):
    name = models.CharField(max_length=100)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")
    sport = models.CharField(max_length=100, default="")
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
