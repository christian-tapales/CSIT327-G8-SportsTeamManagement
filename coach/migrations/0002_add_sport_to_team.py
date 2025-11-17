from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='sport',
            field=models.CharField(max_length=100, default=""),
        ),
    ]
