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
            # Room(name="Study", id="study", has_secret_passage=True, secret_passage_to="library"),
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
            # Hallway(id="hallway_1", name="Hallway between Study and Dining Room", connected_rooms=["study", "dining_room"]),
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
        self.locations = [[Location(location_id="study", name="Study", connected_location=["hallway_1", "hallway_3"], has_secret_passage=True, secret_passage_to="kitchen"), Location(location_id="hallway_1", name="Hallway 1", connected_location=["study", "hall"]), Location(location_id="hall", name="Hall", connected_location=["hallway_1", "hallway_2"]), Location(location_id="hallway_2", name="Hallway 2", connected_location=["hall", "lounge"]), Location(location_id="lounge", name="Lounge", connected_location=["hallway_2", "hallway_5"], has_secret_passage=True, secret_passage_to="conservatory")],
                      [Location(location_id="hallway_3", name="Hallway 3", connected_location=["study", "library"]), Location(location_id="blank_1", name="Blank 1", connected_location=["hallway_1", "hallway_6"]), Location(location_id="hallway_4", name="Hallway 4", connected_location=["hall", "billiard room"]), Location(location_id="blank_2", name="Blank 2", connected_location=["hallway_2", "hallway_7"]), Location(location_id="hallway_5", name="Hallway 5", connected_location=["lounge", "dining_room"])],
                      [Location(location_id="library", name="Library", connected_location=["hallway_3", "hallway_6", "hallway_8"]), Location(location_id="hallway_6", name="Hallway 6", connected_location=["library", "billiard_room"]), Location(location_id="billiard_room", name="Billiard Room", connected_location=["hallway_4", "hallway_7", "hallway_9", "hallway_6"]), Location(location_id="hallway_7", name="Hallway 7", connected_location=["billiard_room", "dining_room"]), Location(location_id="dining_room", name="Dining Room", connected_location=["hallway_5", "hallway_10", "hallway_7"])],
                      [Location(location_id="study", name="Study", connected_location=["hallway_1", "hallway_3"], has_secret_passage=True, secret_passage_to="kitchen"), Location(location_id="hallway_1", name="Hallway 1", connected_location=["study", "hall"]), Location(location_id="hall", name="Hall", connected_location=["hallway_1", "hallway_2"]), Location(location_id="hallway_2", name="Hallway 2", connected_location=["hall", "lounge"]), Location(location_id="lounge", name="Lounge", connected_location=["hallway_2", "hallway_5"], has_secret_passage=True, secret_passage_to="conservatory")],
                      [Location(location_id="study", name="Study", connected_location=["hallway_1", "hallway_3"], has_secret_passage=True, secret_passage_to="kitchen"), Location(location_id="hallway_1", name="Hallway 1", connected_location=["study", "hall"]), Location(location_id="hall", name="Hall", connected_location=["hallway_1", "hallway_2"]), Location(location_id="hallway_2", name="Hallway 2", connected_location=["hall", "lounge"]), Location(location_id="lounge", name="Lounge", connected_location=["hallway_2", "hallway_5"], has_secret_passage=True, secret_passage_to="conservatory")]]

        self.hallways = self.create_hallways()
        
    def lookup_adjacent(self, room_id: str) -> List[str]:
        """
        Lookup adjacent rooms for a given room
        """
        # Based on adjacency in the self.rooms matrix, return the adjacent rooms
        for i in range(3):
            for j in range(3):
                if self.rooms[i][j].room_id == room_id:
                    adjacent = []
                    if i > 0:
                        adjacent.append(self.rooms[i-1][j].id)
                    if i < 2:
                        adjacent.append(self.rooms[i+1][j].id)
                    if j > 0:
                        adjacent.append(self.rooms[i][j-1].id)
                    if j < 2:
                        adjacent.append(self.rooms[i][j+1].id)
        
                    return adjacent

    def create_hallways(self):
        """
        Create hallways between adjacent rooms, add them to the self.rooms matrix
        """
        hallways = []
        for i in range(3):
            for j in range(3):
                room = self.rooms[i][j]
                adjacent = self.lookup_adjacent(room.room_id)
                for adj in adjacent:
                    hallway = Hallway(id=f"{room.room_id}_{adj}", name=f"Hallway between {room.name} and {adj}", connected_rooms=[room.room_id, adj])

        return hallways

    def set_occupied(self, room_id: str):
        """
        Set the occupancy status of a room
        """
        for i in range(3):
            for j in range(3):
                if self.rooms[i][j].room_id == room_id:
                    self.rooms[i][j].is_occupied = True

    
