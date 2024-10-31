import random
from collections import defaultdict
from attrs import define
from typing import List, Optional


@define
class Character:
    name: str
    id: str
    image: Optional[str]
    selected: bool = False

@define
class Card:
    name: str
    id: str
    image: Optional[str]

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

    def is_available(self, char_id: str) -> bool:
        """
        Check if a character is available for selection
        """
        # Find character with id
        character = list(filter(lambda x: x.id == char_id, self.characters))[0]

        return not character.selected # Negate the selected property to check if the character is available


    def set_selected(self, char_id: str):
        """
        Set a character as selected
        """
        # Find character with id and set selected to True
        for character in self.characters:
            if character.id == char_id:
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

class CardHandler:
    def __init__(self):
        """
        Initialize the card handler with the list of card
        which characters are available for selection
        The image property is optional and can be used to display the card image in the UI
        It should correspond to the filename of the image in the cluegonauts/static/clueless/images/ directory
        """
        self.character_card: List[Card] = [Card(name="Miss Scarlet", image="card_scarlet.png", id="ms_scarlet"),
                                            Card(name="Colonel Mustard", image="card_mustard.png", id="col_mustard"),
                                            Card(name="Mrs. White", image="card_white.png", id="mrs_white"),
                                            Card(name="Mr. Green", image="card_green.png", id="mr_green"),
                                            Card(name="Mrs. Peacock", image="card_peacock.png", id="mrs_peacock"),
                                            Card(name="Professor Plum", image="_cardplum.png", id="prof_plum")]
        self.weapon_card: List[Card] = [Card(name="Candlestick", image="candlestick.png", id="candlestick"),
                                        Card(name="Knife", image="knife.png", id="knife"),
                                        Card(name="Lead pipe", image="lead_pipe.png", id="lead_pipe"),
                                        Card(name="Revolver", image="revolver.png", id="revolver"),
                                        Card(name="Rope", image="rope.png", id="rope"),
                                        Card(name="Wrench", image="wrench.png", id="wrench")]
        self.location_card: List[Card] = [Card(name="Study", image="study.png", id="study"),
                                        Card(name="Library", image="library.png", id="library"),
                                        Card(name="Conservatory", image="conservatory.png", id="conservatory"),
                                        Card(name="Hall", image="hall.png", id="hall"),
                                        Card(name="Billiard Room", image="billiard_room.png", id="billiard_room"),
                                        Card(name="Ballroom", image="ballroom.png", id="ballroom"),
                                        Card(name="Lounge", image="lounge.png", id="lounge"),
                                        Card(name="Dining Room", image="dining_room.png", id="dining_room"),
                                        Card(name="Kitchen", image="kitchen.png", id="kitchen")]


    def select_case_file(self):
        random.shuffle(self.character_card)
        random.shuffle(self.weapon_card)
        random.shuffle(self.location_card)
        case_file_char = self.character_card.pop(-1)
        case_file_weapon = self.weapon_card.pop(-1)
        case_file_location = self.location_card.pop(-1)
        return case_file_char, case_file_weapon, case_file_location

    def deal_cards(self, player_list):
        card_pool = []
        card_pool.extend(self.character_card)
        card_pool.extend(self.weapon_card)
        card_pool.extend(self.location_card)
        random.shuffle(card_pool)

        player_card_dict = defaultdict(list)

        player_index = 0
        while len(card_pool) > 0:
            player_card_dict[player_list[player_index]].append(card_pool.pop(0))
            player_index = (player_index + 1) % len(player_list)

        return player_card_dict
