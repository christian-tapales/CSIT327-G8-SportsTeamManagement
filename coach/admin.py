from django.contrib import admin
from .models import Player, Team

# -------------------------------
# Team in Admin
# -------------------------------
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display  = ("name", "coach", "status", "location", "created_at")
    list_filter   = ("status", "coach")
    search_fields = (
        "name", "coach__username", "coach__email",
        "coach__first_name", "coach__last_name"
    )
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        if not change and not obj.coach_id:
            obj.coach = request.user
        super().save_model(request, obj, form, change)


# -------------------------------
# Player in Admin
# -------------------------------
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display  = ("name", "jersey_number", "coach")
    list_filter   = ("coach",)
    search_fields = ("name", "jersey_number", "coach__username", "coach__email")
