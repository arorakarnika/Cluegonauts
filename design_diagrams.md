## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant Session as Django Session
    participant CH as CharacterHandler
    participant RH as RoomHandler
    participant HH as HallwayHandler
    participant LH as LocationHandler

    User ->> Session: Access session data
    Session ->> CH: Initialize CharacterHandler
    CH ->> CH: __init__(selected: List[str])
    User ->> CH: Select character
    CH ->> CH: set_selected(char_id: str)
    CH ->> Session: Update session data

    User ->> RH: Initialize RoomHandler
    RH ->> RH: __init__()

    User ->> HH: Initialize HallwayHandler
    HH ->> HH: __init__()

    User ->> LH: Initialize LocationHandler
    LH ->> LH: __init__()
    LH ->> LH: create_hallways()

    User ->> LH: Lookup adjacent rooms
    LH ->> LH: lookup_adjacent(room_id: str)

    User ->> LH: Set room occupied
    LH ->> LH: set_occupied(room_id: str)
    LH ->> RH: Update room status
    LH ->> HH: Update hallway status

```

## Class Diagram

```mermaid
classDiagram
    class Character {
        +name: str
        +id: str
        +image: Optional[str]
        +selected: bool = False
    }

    class CharacterHandler {
        +characters: List~Character~
        +__init__(selected: List~str~)
        +is_available(char_id: str): bool
        +set_selected(char_id: str)
        +get_all_characters(): List~Character~
        +serialize_selected(): List~str~
    }

    class Room {
        +name: str
        +id: str
        +has_secret_passage: bool = False
        +secret_passage_to: Optional[str]
        +is_occupied: bool = False
    }

    class RoomHandler {
        +rooms: List~Room~
        +__init__()
    }

    class Hallway {
        +id: str
        +name: str
        +connected_rooms: List~str~
        +is_occupied: bool = False
        +set_occupied(status: bool)
    }

    class HallwayHandler {
        +hallways: List~Hallway~
        +__init__()
        +find_hallway(room_id_1: str, room_id_2: str): Hallway
        +set_hallway_occupied(hallway_id: str, status: bool)
    }

    class LocationHandler {
        +rooms: List~List~Room~~
        +hallways: List~Hallway~
        +__init__()
        +lookup_adjacent(room_id: str): List~str~
        +create_hallways()
        +set_occupied(room_id: str)
    }

    CharacterHandler --> Character
    RoomHandler --> Room
    HallwayHandler --> Hallway
    LocationHandler --> Room
    LocationHandler --> Hallway

```