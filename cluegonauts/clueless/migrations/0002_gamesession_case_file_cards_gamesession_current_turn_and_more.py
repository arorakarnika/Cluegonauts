# Generated by Django 5.1.1 on 2024-10-31 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clueless', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='case_file_cards',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='current_turn',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='player_cards',
            field=models.JSONField(default=None, null=True),
        ),
    ]
