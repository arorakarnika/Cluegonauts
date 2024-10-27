from django.shortcuts import render
from .models import GameSession

from .classes import CharacterHandler

def index(request):
    session_id = request.session.get("game_session", None)
    if session_id:
        game_session = GameSession()
        selected_players = game_session.get_selected_players(session_id)
        char_handler = CharacterHandler(selected=selected_players)
    else:
        char_handler = CharacterHandler()
    char_choices = char_handler.get_all_characters()
    return render( 
        request, 
        "clueless/index.html",
        {"char_choices": char_choices}
        )

def gameb(request):
    session_id = request.session.get("game_session", None)
    # Get the selected character ID from the request
    return render(request, "clueless/gameb.html")