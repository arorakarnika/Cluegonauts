from .models import GameSession
from .classes import CharacterHandler
import websocket

def select_character(char_id: str, session_id: str = None) -> bool:
    """
    Store selected characters in session if the character is available

    :param char_id: The ID of the character to be selected
    :param session_id: The ID of the game session
    :return: True if the character was successfully selected, False otherwise
    """
    game_session = GameSession()
    if session_id is not None:
        current_session = game_session.get_selected_players(session_id=session_id)
        char_handler = CharacterHandler(selected=current_session)

    else:
        char_handler = CharacterHandler()

    if char_handler.is_available(char_id):
        char_handler.set_selected(char_id)
        selected_array = char_handler.serialize_selected()
        session_id = game_session.update_selected_players(selected_players=selected_array, session_id=session_id)
        return True, session_id

    elif not char_handler.is_available(char_id):
        return False, session_id

def connect_game_state_consumer():
    game_state_consumer_socket = websocket.WebSocketApp('ws://localhost:8000/ws/clueless/gamestate/')
    game_state_consumer_socket.run_forever()
