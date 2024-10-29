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
class Room:
    name: str
    id: str
    has_secret_passage: bool = False
    secret_passage_to: Optional[str] = None
    is_occupied: bool = False


class RoomHandler:
    def __init__(self):
        """
        Initialize rooms with properties like names, IDs, and secret passages.
        """
        self.rooms = [
            Room(name="Study", id="study", has_secret_passage=True, secret_passage_to="library"),
            Room(name="Ballroom", id="ballroom"),
            Room(name="Billiards Room", id="billiards_room", has_secret_passage=True, secret_passage_to="lounge"),
            Room(name="Dining Room", id="dining_room"),
            Room(name="Hall", id="hall"),
            Room(name="Kitchen", id="kitchen"),
            Room(name="Lounge", id="lounge", has_secret_passage=True, secret_passage_to="billiards_room"),
            Room(name="Conservatory", id="conservatory"),
            Room(name="Library", id="library", has_secret_passage=True, secret_passage_to="study")
        ]

@define
class Hallway:
    id: str
    name: str
    connected_rooms: List[str]  # Stores IDs of the two rooms this hallway connects
    is_occupied: bool = False  # Default to unoccupied

    def set_occupied(self, status: bool):
        """
        Set the occupancy status of the hallway.
        """
        self.is_occupied = status



class HallwayHandler:
    def __init__(self):
        """
        Initialize hallways with names, IDs, and connected rooms.
        """
        self.hallways = [
            Hallway(id="hallway_1", name="Hallway between Study and Dining Room", connected_rooms=["study", "dining_room"]),
            Hallway(id="hallway_2", name="Hallway between Dining Room and Lounge", connected_rooms=["dining_room", "lounge"]),
            Hallway(id="hallway_3", name="Hallway between Study and Ballroom", connected_rooms=["study", "ballroom"]),
            Hallway(id="hallway_4", name="Hallway between Dining Room and Hall", connected_rooms=["dining_room", "hall"]),
            Hallway(id="hallway_5", name="Hallway between Lounge and Conservatory", connected_rooms=["lounge", "conservatory"]),
            Hallway(id="hallway_6", name="Hallway between Ballroom and Hall", connected_rooms=["ballroom", "hall"]),
            Hallway(id="hallway_7", name="Hallway between Hall and Conservatory", connected_rooms=["hall", "conservatory"]),
            Hallway(id="hallway_8", name="Hallway between Ballroom and Billiards Room", connected_rooms=["ballroom", "billiards_room"]),
            Hallway(id="hallway_9", name="Hallway between Hall and Kitchen", connected_rooms=["hall", "kitchen"]),
            Hallway(id="hallway_10", name="Hallway between Conservatory and Library", connected_rooms=["conservatory", "library"]),
            Hallway(id="hallway_11", name="Hallway between Billiards Room and Kitchen", connected_rooms=["billiards_room", "kitchen"]),
            Hallway(id="hallway_12", name="Hallway between Kitchen and Library", connected_rooms=["kitchen", "library"]),
        ]

    def find_hallway(self, room_id_1: str, room_id_2: str) -> Hallway:
        """
        Find a hallway connecting two specific rooms, if it exists.
        """
        for hallway in self.hallways:
            if set(hallway.connected_rooms) == {room_id_1, room_id_2}:
                return hallway
        return None

    def set_hallway_occupied(self, hallway_id: str, status: bool):
        """
        Set a specific hallway's occupancy status by its ID.
        """
        hallway = next((h for h in self.hallways if h.id == hallway_id), None)
        if hallway:
            hallway.set_occupied(status)

