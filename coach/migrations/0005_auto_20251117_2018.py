from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0004_player_team_team_season'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[],
        ),
    ]
