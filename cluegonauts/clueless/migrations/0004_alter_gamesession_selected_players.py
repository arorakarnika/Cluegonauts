# Generated by Django 5.1.1 on 2024-11-10 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clueless', '0003_gamesession_location_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='selected_players',
            field=models.JSONField(null=True),
        ),
    ]
