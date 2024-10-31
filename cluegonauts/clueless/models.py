# Use noqa: F401 to ignore unused import error
from django.db import models  # noqa: F401
import uuid
import json

# Create your models here.


class GameSession(models.Model):
    """
    A model to store the game session information
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    selected_players = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    case_file_cards = models.JSONField(default=None, null=True)
    player_cards = models.JSONField(default=None, null=True)
    current_turn = models.JSONField(default=None, null=True)

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

    def set_case_file_cards(self, case_file_cards, session_id):
        """
        Set the case file cards for a game session
        """
        GameSession.objects.filter(session_id=session_id).update(case_file_cards=case_file_cards)

    def get_case_file_cards(self, session_id):
        """
        Get the case file cards for a game session
        """
        return GameSession.objects.get(session_id=session_id).case_file_cards

    def set_player_cards(self, player_cards, session_id):
        """
        Set each player's cards for a game session
        """
        GameSession.objects.filter(session_id=session_id).update(
            player_cards=json.dumps(player_cards, default=lambda card: card.id))

    def get_player_cards(self, session_id):
        """
        Get each player's cards for a game session
        """
        return json.loads(GameSession.objects.get(session_id=session_id).player_cards)

    def set_current_turn(self, current_turn, session_id):
        """
        Set the current turn for a game session
        """
        GameSession.objects.filter(session_id=session_id).update(current_turn=current_turn)

    def get_current_turn(self, session_id):
        """
        Get the current turn for a game session
        """
        return GameSession.objects.get(session_id=session_id).current_turn
