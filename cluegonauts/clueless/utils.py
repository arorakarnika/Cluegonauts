from .models import GameSession
from .classes import CharacterHandler


CHAR_ID_TO_NAME_DICT = {"ms_scarlet": "Miss Scarlet",
                        "prof_plum": "Professor Plum",
                        "mrs_peacock": "Mrs. Peacock",
                        "mr_green": "Mr. Green",
                        "mrs_white": "Mrs. White",
                        "col_mustard": "Colonel Mustard"}


def select_character(char_id: str, char_handler:CharacterHandler, game_session: GameSession, session_id: str = None) -> bool:
    """
    Store selected characters in session if the character is available

    :param char_id: The ID of the character to be selected
    :param session_id: The ID of the game session
    :return: True if the character was successfully selected, False otherwise
    """
    if char_handler.is_available(char_id):
        char_handler.set_selected(char_id)
        selected_array = char_handler.serialize_selected()
        session_id = game_session.update_selected_players(selected_players=selected_array, session_id=session_id)
        return True, session_id

    elif not char_handler.is_available(char_id):
        return False, session_id


def char_id_to_name(char_id: str):
    return CHAR_ID_TO_NAME_DICT[char_id]

def location_id_to_name(location_id: str):
    return location_id.replace("_", " ").title()
