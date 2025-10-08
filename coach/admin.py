from django.contrib import admin
from .models import Player  # Import your Player model

# Register the Player model
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'jersey_number', 'coach')  # Columns to display in admin
