from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0002_add_sport_to_team'),  # OR 0001_initial IF 0002 does not exist
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='first_name',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='last_name',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='email',
            field=models.EmailField(max_length=254, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
