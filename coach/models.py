from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    name = models.CharField(max_length=100)
    jersey_number = models.IntegerField()
    coach = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
