from attrs import define
from typing import List, Optional


@define
class Character:
    name: str
    id: str
    image: Optional[str]
    selected: bool = False


class CharacterHandler:
    def __init__(self, selected: List[str] = []):
        """
        Initialize the character handler with the list of characters
        The selected property is set to False for all characters on initialization, but will used to track 
        which characters are available for selection
        The image property is optional and can be used to display the character image in the UI
        It should correspond to the filename of the image in the cluegonauts/static/clueless/images/ directory
        """
        self.characters: List[Character] = [Character(name="Miss Scarlet", image="scarlet.png", id="ms_scarlet"),
                                            Character(name="Colonel Mustard", image="mustard.png", id="col_mustard"),
                                            Character(name="Mrs. White", image="white.png", id="mrs_white"),
                                            Character(name="Mr. Green", image="green.png", id="mr_green"),
                                            Character(name="Mrs. Peacock", image="peacock.png", id="mrs_peacock"),
                                            Character(name="Professor Plum", image="plum.png", id="prof_plum")]
        # Set selected property to True for characters that are already selected
        for char_id in selected:
            self.set_selected(char_id)

    def is_available(self, id: str) -> bool:
        """
        Check if a character is available for selection
        """
        # Find character with id
        character = list(filter(lambda x: x.id == id, self.characters))[0]

        return not character.selected # Negate the selected property to check if the character is available


    def set_selected(self, id: str):
        """
        Set a character as selected
        """
        # Find character with id and set selected to True
        for character in self.characters:
            if character.id == id:
                character.selected = True

    def get_all_characters(self) -> List[Character]:
        """
        Get a list of available characters
        """
        return self.characters

    def serialize_selected(self) -> List[str]:
        """
        Serialize the selected characters
        """
        return [char.id for char in self.characters if char.selected]
