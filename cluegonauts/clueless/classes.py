import random
from collections import defaultdict
from attrs import define
from typing import List, Optional, Dict
from uuid import UUID

@define
class currentGameSession:
    session_id: UUID
@define
class Card:
    name: str
    id: str
    image: Optional[str]

@define
class Location:
    location_id: str
    name: str
    connected_location: List[str] #Stores location_id of the locations connected to this location
    is_occupied: bool = False # Default to unoccupied
    has_secret_passage: bool = False # Default to no secret passage
    secret_passage_to: Optional[str] = None # Default to no secret passage locations
    image: Optional[str] = None  # Path to the image file

@define
class Character:
    name: str
    char_id: str
    image: Optional[str]
    selected: bool = False
    user_id: Optional[str] = None
    cards: List[Card] = []
    location: Location = None

class CharacterHandler:
    def __init__(self, selected: List[str] = []):
        """
        Initialize the character handler with the list of characters
        The selected property is set to False for all characters on initialization, but will used to track 
        which characters are available for selection
        The image property is optional and can be used to display the character image in the UI
        It should correspond to the filename of the image in the cluegonauts/static/clueless/images/ directory
        """
        self.characters: List[Character] = [
            Character(name="Miss Scarlet", image="scarlet_iconv2.png", char_id="ms_scarlet", location=LocationHandler().get_location_by_id("hallway_2")),
            Character(name="Professor Plum", image="plum_iconv2.png", char_id="prof_plum", location=LocationHandler().get_location_by_id("hallway_3")),
            Character(name="Mrs. Peacock", image="peacock_iconv2.png", char_id="mrs_peacock", location=LocationHandler().get_location_by_id("hallway_8")),
            Character(name="Mr. Green", image="green_iconv2.png", char_id="mr_green", location=LocationHandler().get_location_by_id("hallway_11")),
            Character(name="Mrs. White", image="white_iconv2.png", char_id="mrs_white", location=LocationHandler().get_location_by_id("hallway_12")),
            Character(name="Colonel Mustard", image="mustard_iconv2.png", char_id="col_mustard", location=LocationHandler().get_location_by_id("hallway_5"))
            ]
        # Set selected property to True for characters that are already selected
        for char_id in selected:
            self.set_selected(char_id)

    def is_available(self, char_id: str) -> bool:
        """
        Check if a character is available for selection
        """
        # Find character with id
        character = list(filter(lambda x: x.char_id == char_id, self.characters))[0]

        return not character.selected # Negate the selected property to check if the character is available


    def set_selected(self, char_id: str, user_id: Optional[str] = None):
        """
        Set a character as selected
        """
        # Find character with id and set selected to True
        for character in self.characters:
            if character.char_id == char_id:
                character.selected = True
                character.user_id = user_id

    def get_all_characters(self) -> List[Character]:
        """
        Get a list of available characters
        """
        return self.characters
    
    def get_selected_characters(self) -> List[Character]:
        """
        Get a list of selected characters
        """
        return [char for char in self.characters if char.selected is True]
    
    def get_character_by_id(self, char_id: str) -> Optional[Character]:
        """
        Get a character by ID
        """
        # Find character with id
        return next((char for char in self.characters if char.char_id == char_id), None)

    def serialize_selected(self) -> List[str]:
        """
        Serialize the selected characters
        """
        return [char.char_id for char in self.characters if char.selected]

    def update_character_cards(self, card_selection: Dict[str, List[Card]]):
        """
        Update the cards of a character
        """
        # Find character with id and append card to cards list
        for char_id, cards in card_selection.items():
            for character in self.characters:
                if character.char_id == char_id:
                    character.cards = cards
    


class LocationHandler:
    def __init__(self, locations: List[Dict] = []):
        """
        Initialize the location handler with a matrix of the locations (rooms and hallways)
        """
        # Matrix with locations
        # Rows 1 and 3 have only 3 hallways each; created Location objects "Blank_X" as placeholders for columns 1 and 3 in these rows
        # Connected locations are read clockwise beginning at the 12 o'clock location
        if locations:
            self.locations = [locations]
        self.locations = [
            [
                Location(location_id="study", name="Study", connected_location=["hallway_1", "hallway_3"], has_secret_passage=True, secret_passage_to="kitchen", image= "study_gv.png"), 
                Location(location_id="hallway_1", name="Hallway 1", connected_location=["study", "hall"], image= "hallway_vertical_gv.png"), 
                Location(location_id="hall", name="Hall", connected_location=["hallway_2", "hallway_4", "hallway_1"], image="hall_gv.png"), 
                Location(location_id="hallway_2", name="Hallway 2", connected_location=["hall", "lounge"], image= "hallway_vertical_gv.png"), 
                Location(location_id="lounge", name="Lounge", connected_location=["hallway_5", "hallway_2"], has_secret_passage=True, secret_passage_to="conservatory", image="lounge_gv.png")
            ],
            [
                Location(location_id="hallway_3", name="Hallway 3", connected_location=["study", "library"], image= "hallway_horizontal_gv.png"),
                Location(location_id="blank_1", name="Blank 1", connected_location=["hallway_1", "hallway_6"]), 
                Location(location_id="hallway_4", name="Hallway 4", connected_location=["hall", "billiard_room"], image= "hallway_horizontal_gv.png"), 
                Location(location_id="blank_2", name="Blank 2", connected_location=["hallway_2", "hallway_7"]), 
                Location(location_id="hallway_5", name="Hallway 5", connected_location=["lounge", "dining_room"], image= "hallway_horizontal_gv.png")
            ],
            [
                Location(location_id="library", name="Library", connected_location=["hallway_3", "hallway_6", "hallway_8"], image= "library_gv.png"), 
                Location(location_id="hallway_6", name="Hallway 6", connected_location=["library", "billiard_room"], image= "hallway_vertical_gv.png"), 
                Location(location_id="billiard_room", name="Billiard Room", connected_location=["hallway_4", "hallway_7", "hallway_9", "hallway_6"], image= "billiard_room_gv.png"), 
                Location(location_id="hallway_7", name="Hallway 7", connected_location=["billiard_room", "dining_room"], image= "hallway_vertical_gv.png"), 
                Location(location_id="dining_room", name="Dining Room", connected_location=["hallway_5", "hallway_10", "hallway_7"], image= "dining_room_gv.png")
            ],
            [ 
                Location(location_id="hallway_8", name="Hallway 8", connected_location=["library", "conservatory"], image= "hallway_horizontal_gv.png"), 
                Location(location_id="blank_3", name="Blank 3", connected_location=["hallway_6", "hallway_8"]), 
                Location(location_id="hallway_9", name="Hallway 9", connected_location=["billiard_room", "ballroom"], image= "hallway_horizontal_gv.png"), 
                Location(location_id="blank_4", name="Blank 4", connected_location=["hallway_7", "hallway_12"]), 
                Location(location_id="hallway_10", name="Hallway 10", connected_location=["dining_room", "kitchen"], image= "hallway_horizontal_gv.png")
            ],
            [
                Location(location_id="conservatory", name="Conservatory", connected_location=["hallway_8", "hallway_11"], has_secret_passage=True, secret_passage_to="lounge", image="conservatory_gv.png"), 
                Location(location_id="hallway_11", name="Hallway 11", connected_location=["conservatory", "ballroom"], image= "hallway_vertical_gv.png"), 
                Location(location_id="ballroom", name="Ballroom", connected_location=["hallway_9", "hallway_12", "hallway_11"], image="ballroom_gv.png"), 
                Location(location_id="hallway_12", name="Hallway 12", connected_location=["ballroom", "kitchen"], image= "hallway_vertical_gv.png"), 
                Location(location_id="kitchen", name="Kitchen", connected_location=["hallway_10", "hallway_12"], has_secret_passage=True, secret_passage_to="study", image="kitchen_gv.png")
            ]
        ]

    def set_occupied(self, location_id: str, char: Character):
        """
        Set the occupancy status of a location to "occupied"
        """
        for i in range(5):
            for j in range(5):
                if self.locations[i][j].location_id == location_id:
                    self.locations[i][j].is_occupied = True
                    self.locations[i][j].chars.append(char)

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
                        
    def get_all_locations(self) -> List[Location]:
        """
        Get a list of all locations, without the matrix structure
        """
        # Unpack the matrix structure into a single list and serialize the locations into dictionaries
        return [location for row in self.locations for location in row]
    
    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        """
        Get a location by ID
        """
        # Find location with id
        for row in self.locations:
            for location in row:
                if location.location_id == location_id:
                    return location
        return None


class CardHandler:
    def __init__(self):
        """
        Initialize the card handler with the list of card
        which characters are available for selection
        The image property is optional and can be used to display the card image in the UI
        It should correspond to the filename of the image in the cluegonauts/static/clueless/images/ directory
        """
        self.character_card: List[Card] = [Card(name="Miss Scarlet", image="card_scarletv2.png", id="ms_scarlet"),
                                            Card(name="Colonel Mustard", image="card_mustardv2.png", id="col_mustard"),
                                            Card(name="Mrs. White", image="card_whitev2.png", id="mrs_white"),
                                            Card(name="Mr. Green", image="card_greenv2.png", id="mr_green"),
                                            Card(name="Mrs. Peacock", image="card_peacockv2.png", id="mrs_peacock"),
                                            Card(name="Professor Plum", image="card_plumv2.png", id="prof_plum")]
        self.weapon_card: List[Card] = [Card(name="Candlestick", image="candlestickv2.png", id="candlestick"),
                                        Card(name="Knife", image="knifev2.png", id="knife"),
                                        Card(name="Lead pipe", image="lead_pipev2.png", id="lead_pipe"),
                                        Card(name="Revolver", image="revolverv2.png", id="revolver"),
                                        Card(name="Rope", image="ropev2.png", id="rope"),
                                        Card(name="Wrench", image="wrenchv2.png", id="wrench")]
        self.location_card: List[Card] = [Card(name="Study", image="studyv2.png", id="study"),
                                        Card(name="Library", image="libraryv2.png", id="library"),
                                        Card(name="Conservatory", image="conservatoryv2.png", id="conservatory"),
                                        Card(name="Hall", image="hallv2.png", id="hall"),
                                        Card(name="Billiard Room", image="billiard_roomv2.png", id="billiard_room"),
                                        Card(name="Ballroom", image="ballroomv2.png", id="ballroom"),
                                        Card(name="Lounge", image="loungev2.png", id="lounge"),
                                        Card(name="Dining Room", image="dining_roomv2.png", id="dining_room"),
                                        Card(name="Kitchen", image="kitchenv2.png", id="kitchen")]
        
        self.case_file = self.select_case_file()


    def select_case_file(self):
        random.shuffle(self.character_card)
        random.shuffle(self.weapon_card)
        random.shuffle(self.location_card)
        case_file_char = self.character_card[-1]
        case_file_weapon = self.weapon_card[-1]
        case_file_location = self.location_card[-1]
        return case_file_char, case_file_weapon, case_file_location

    def deal_cards(self, player_list):
        card_pool = []
        card_pool.extend(self.character_card)
        card_pool.extend(self.weapon_card)
        card_pool.extend(self.location_card)
        # remove case file cards from card pool
        card_pool = [card for card in card_pool if card not in self.case_file]
        random.shuffle(card_pool)

        player_card_dict = defaultdict(list)

        player_index = 0
        while len(card_pool) > 0:
            player_card_dict[player_list[player_index]].append(card_pool.pop(0))
            player_index = (player_index + 1) % len(player_list)

        return player_card_dict
