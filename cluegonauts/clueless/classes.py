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
    

@define
class Location:
    location_id: str
    name: str
    connected_location: List[str] #Stores location_id of the locations connected to this location
    is_occupied: bool = False # Default to unoccupied
    has_secret_passage: bool = False # Default to no secret passage
    secret_passage_to: Optional[str] = None # Default to no secret passage locations

class LocationHandler:
    def __init__(self):
        """
        Initialize the location handler with a matrix of the locations (rooms and hallways)
        """
        # Matrix with locations
        # Rows 1 and 3 have only 3 hallways each; created Location objects "Blank_X" as placeholders for columns 1 and 3 in these rows
        # Connected locations are read clockwise beginning at the 12 o'clock location
        self.locations = [[Location(location_id="study", name="Study", connected_location=["hallway_1", "hallway_3"], has_secret_passage=True, secret_passage_to="kitchen"), Location(location_id="hallway_1", name="Hallway 1", connected_location=["study", "hall"]), Location(location_id="hall", name="Hall", connected_location=["hallway_2", "hallway_4", "hallway_1"]), Location(location_id="hallway_2", name="Hallway 2", connected_location=["hall", "lounge"]), Location(location_id="lounge", name="Lounge", connected_location=["hallway_5", "hallway_2"], has_secret_passage=True, secret_passage_to="conservatory")],
                      [Location(location_id="hallway_3", name="Hallway 3", connected_location=["study", "library"]), Location(location_id="blank_1", name="Blank 1", connected_location=["hallway_1", "hallway_6"]), Location(location_id="hallway_4", name="Hallway 4", connected_location=["hall", "billiard room"]), Location(location_id="blank_2", name="Blank 2", connected_location=["hallway_2", "hallway_7"]), Location(location_id="hallway_5", name="Hallway 5", connected_location=["lounge", "dining_room"])],
                      [Location(location_id="library", name="Library", connected_location=["hallway_3", "hallway_6", "hallway_8"]), Location(location_id="hallway_6", name="Hallway 6", connected_location=["library", "billiard_room"]), Location(location_id="billiard_room", name="Billiard Room", connected_location=["hallway_4", "hallway_7", "hallway_9", "hallway_6"]), Location(location_id="hallway_7", name="Hallway 7", connected_location=["billiard_room", "dining_room"]), Location(location_id="dining_room", name="Dining Room", connected_location=["hallway_5", "hallway_10", "hallway_7"])],
                      [Location(location_id="hallway_8", name="Hallway 8", connected_location=["library", "conservatory"]), Location(location_id="blank_3", name="Blank 3", connected_location=["hallway_6", "hallway_8"]), Location(location_id="hallway_9", name="Hallway 9", connected_location=["billiard_room", "ballroom"]), Location(location_id="blank_4", name="Blank 4", connected_location=["hallway_7", "hallway_12"]), Location(location_id="hallway_10", name="Hallway 10", connected_location=["dining_room", "kitchen"])],
                      [Location(location_id="conservatory", name="Conservatory", connected_location=["hallway_8", "hallway_11"], has_secret_passage=True, secret_passage_to="lounge"), Location(location_id="hallway_11", name="Hallway 11", connected_location=["conservatory", "ballroom"]), Location(location_id="ballroom", name="Ballroom", connected_location=["hallway_9", "hallway_12", "hallway_11"]), Location(location_id="hallway_12", name="Hallway 12", connected_location=["ballroom", "kitchen"]), Location(location_id="kitchen", name="Kitchen", connected_location=["hallway_10", "hallway_12"], has_secret_passage=True, secret_passage_to="study")]]

    def set_occupied(self, location_id: str):
        """
        Set the occupancy status of a location to "occupied"
        """
        for i in range(5):
            for j in range(5):
                if self.locations[i][j].location_id == location_id:
                    self.locations[i][j].is_occupied = True

    def set_unoccupied(self, location_id: str):
        """
        Set the occupancy status of a location to "unoccupied"
        """
        for i in range(5):
            for j in range(5):
                if self.locations[i][j].location_id == location_id:
                    self.locations[i][j].is_occupied = False

    def find_connected_locations(self, location_id: str):
        """
        Identify what locations are connected to the selected location
        """
        # Purpose is to return the list of locations connected to the specified location
        for i in range(5):
            for j in range(5):
                if self.locations[i][j].location_id == location_id:
                    return self.locations[i][j].connected_location  # Return list of connected location_ids

    def find_available_moves(self, location_id: str):
        """
        Identify available moves from the selected location
        """
        # Purpose is to identify which of the connected locations can actually be moved to
        selected_location = location_id
        possible_moves = self.find_connected_locations(selected_location)  # Generate list of connected location_ids

        # Iterate through list and find locations that are not already occupied (i.e. is_occupied == False)

        for item in possible_moves:
            for i in range(5):
                for j in range(5):
                    if self.locations[i][j].location_id == item:
                        if self.locations[i][j].is_occupied is False:
                            return self.locations[i][j].location_id


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
