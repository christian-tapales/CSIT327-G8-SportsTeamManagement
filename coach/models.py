from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    name = models.CharField(max_length=100)
    jersey_number = models.IntegerField()
    coach = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Team(models.Model):
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

    name = models.CharField(max_length=100)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")
    sport = models.CharField(max_length=30, choices=SPORT_CHOICES)
    season = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
