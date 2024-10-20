# Use noqa: F401 to ignore unused import error
from django.db import models  # noqa: F401
import uuid

# Create your models here.


class GameSession(models.Model):
    """
    A model to store the game session information
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    selected_players = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_id

    def get_selected_players(self, session_id):
        """
        Get the selected players for a game session
        """
        return GameSession.objects.get(session_id=session_id).selected_players

    def update_selected_players(self, selected_players, session_id=None):
        """
        Update the selected players for a game session or create a new session if session_id is None
        """
        if session_id:
            GameSession.objects.filter(session_id=session_id).update(selected_players=selected_players)
        else:
            session_id = uuid.uuid4()
            GameSession.objects.create(selected_players=selected_players, session_id=session_id)

        return session_id