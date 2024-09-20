from attrs import define
from typing import List, Optional


@define
class Character:
    self.name: str
    self.id: str
    self.image: Optional[str]
    self.selected: bool = False


class CharacterHandler:
    def __init__(self, game_session):
        """
        Initialize the character handler with the list of characters
        The selected property is set to False for all characters on initialization, but will used to track 
        which characters are available for selection
        The image property is optional and can be used to display the character image in the UI
        It should correspond to the filename of the image in the cluegonauts/static/clueless/images/ directory
        """
        self.game_session = game_session
        self.characters: List[Character] = [Character(name="Miss Scarlet", image="scarlet.png", id="ms_scarlet"),
                                            Character(name="Colonel Mustard", image="mustard.png", id="col_mustard"),
                                            Character(name="Mrs. White", image="white.png", id="mrs_white"),
                                            Character(name="Mr. Green", image="green.png", id="mr_green"),
                                            Character(name="Mrs. Peacock", image="peacock.png", id="mrs_peacock"),
                                            Character(name="Professor Plum", image="plum.png", id="prof_plum")]

    def is_available(self, id: str) -> bool:
        """
        Check if a character is available for selection
        """
        # Find character with id
        character = Character(filter(lambda x: x.id == id, self.characters))

        return not self.characters[id].selected # Negate the selected property to check if the character is available


    def set_selected(self, id: str):
        """
        Set a character as selected
        """
        # Find character with id
        character = Character(filter(lambda x: x.id == id, self.characters))

        character.selected = True

    def get_all_characters(self) -> List[Character]:
        """
        Get a list of available characters
        """
        return self.characters
