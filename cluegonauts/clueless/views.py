from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from injector import inject
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .models import GameSession
from .classes import CharacterHandler, LocationHandler, CardHandler, currentGameSession
from .utils import select_character
from .forms import SuggestAccuseForm, DisproveSuggestionForm



@inject
def index(request, char_handler: CharacterHandler):
    char_choices = char_handler.get_all_characters()
    return render( 
        request, 
        "clueless/index.html",
        {"char_choices": char_choices}
        )

@inject
@csrf_exempt
def gameb(request, char_id, loc_handler: LocationHandler, card_handler: CardHandler, char_handler: CharacterHandler):
    # Add char_id to the session
    request.session["char_id"] = char_id
    session_id = request.session.get("game_session", None)
    locations = loc_handler.locations
    rooms = card_handler.location_card
    characters = card_handler.character_card
    weapons = card_handler.weapon_card
    blank_ids = ['blank_1', 'blank_2', "blank_3", "blank_4"]
    hallway_ids = [location.location_id for row in locations for location in row if location.name.startswith("Hallway")]
    form = SuggestAccuseForm()
    form.fields['character'].choices = [(card.id, card.name) for card in card_handler.character_card]
    form.fields['location'].choices = [(card.id, card.name) for card in card_handler.location_card]
    form.fields['weapon'].choices = [(card.id, card.name) for card in card_handler.weapon_card]
    form.fields['actor'].initial = char_id
    disprove_form = DisproveSuggestionForm()
    disprove_form.fields['card'].choices = [(card.id, card.name) for card in char_handler.get_character_by_id(char_id).cards]
    # Get the selected character ID from the request
    return render(request, "clueless/gameb.html", 
                  {"char_id": char_id,
                   "locations": locations,
                   "characters": characters,
                   "weapons": weapons,
                   "rooms": rooms,
                   "blank_ids": blank_ids,
                   "hallway_ids": hallway_ids,
                   "player_action_form": form,
                   "disprove_form": disprove_form,
                   "player_cards": char_handler.get_character_by_id(char_id).cards,
                   "current_location": char_handler.get_character_by_id(char_id).location,
                   "current_char": char_handler.get_character_by_id(char_id),
                   })

def game_end(request, winner, char_handler: CharacterHandler):
    winner_name = char_handler.get_character_by_id(winner).name
    return render(request, "clueless/end_game.html", {"winner": winner_name})

""" 

API views can be called by the websocket consumers to update the game state.

"""
class SelectCharacterView(APIView):
    @inject
    def setup(self, request, char_handler: CharacterHandler, game_session: GameSession, current_game_session: currentGameSession):
        super().setup(request)
        self.char_handler = char_handler
        self.game_session = game_session
        self.current_game_session = current_game_session

    def post(self, request):
        char_id = request.data.get('char_id')
        session_id = self.current_game_session.session_id
        
        if not char_id:
            return Response({"message": "char_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        state, session_id = select_character(char_id, self.char_handler, self.game_session, session_id)
        
        if state:
            return Response({"message": "Character selected successfully", "session_id": str(session_id)}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Character is not available", "session_id": str(session_id)}, status=status.HTTP_200_OK)
        
class GetCharactersView(APIView):
    @inject
    def setup(self, request, char_handler: CharacterHandler, game_session: GameSession):
        super().setup(request)
        self.char_handler = char_handler
        self.game_session = game_session

    def get(self, request):
        characters = self.char_handler.serialize_selected()
        return Response({"selected_characters": characters}, status=status.HTTP_200_OK)

class SetupGame(APIView):
    @inject
    def setup(self, request, card_handler: CardHandler, 
              game_session: GameSession, loc_handler: LocationHandler,
              char_handler: CharacterHandler, current_game_session: currentGameSession):
        super().setup(request)
        self.card_handler = card_handler
        self.game_session = game_session
        self.loc_handler = loc_handler
        self.char_handler = char_handler
        self.current_game_session = current_game_session

    def post(self, request):
        session_id = self.current_game_session.session_id
        # Deal cards to players
        selected_players = self.char_handler.serialize_selected()
        card_selection = self.card_handler.deal_cards(selected_players)
        self.char_handler.update_character_cards(card_selection)
        # Save the cards to the game session table, creates a new session if session_id is None
        session_id = self.game_session.update_selected_players(selected_players, session_id)
        self.game_session.set_case_file_cards([card.id for card in self.card_handler.case_file], session_id)
        print(f"Case file cards: {[card.name for card in self.card_handler.case_file]}".center(100, "+")) # noqa:T201
        self.game_session.set_current_turn(selected_players[0], session_id)
        request.session["game_session"] = str(session_id)

        # Add current player to the request session
        request.session["current_turn"] = selected_players[0]
        # Return current turn and card selection
        return Response({"current_turn": selected_players[0], 'card_selection': {k : [card.name for card in v] for k,v in card_selection.items()}}, status=status.HTTP_200_OK)
    
    def get(self, request):
        session_id = self.current_game_session.session_id
        selected_chars = self.char_handler.get_selected_characters()
        return Response({
            "case_file": self.game_session.get_case_file_cards(session_id),
            "card_selection": { char.char_id: [card.name for card in char.cards] for char in selected_chars },
            "char_loc_icons": {char.char_id: (char.location.location_id, char.image) for char in selected_chars},
            "current_turn": self.game_session.get_current_turn(session_id)
            }, status=status.HTTP_200_OK)


class PlayerMove(APIView):
    @inject
    def setup(self, request, card_handler: CardHandler, 
              game_session: GameSession, loc_handler: LocationHandler,
              char_handler: CharacterHandler, current_game_session: currentGameSession):
        super().setup(request)
        self.card_handler = card_handler
        self.game_session = game_session
        self.loc_handler = loc_handler
        self.char_handler = char_handler
        self.current_game_session = current_game_session

    def post(self, request):
        """
        Handle player moves - check that the move is valid and update the game state
        Update player location
        """

        location_id = request.data.get('location_id')
        char_id = request.data.get('char_id')

        # Check current player location
        current_location = self.char_handler.get_character_by_id(char_id).location
        if current_location.location_id == location_id:
            return Response({"message": "Player is already in this location"}, status=status.HTTP_400_BAD_REQUEST)
        elif location_id not in current_location.connected_location and location_id != current_location.secret_passage_to:
                connected_location_names = [self.loc_handler.get_location_by_id(connected_id).name for connected_id in current_location.connected_location]
                return Response({"message": f"Invalid move from {current_location.name} to {self.loc_handler.get_location_by_id(location_id).name}, your choices are {connected_location_names} ",
                                 "valid_locations": [connected_id for connected_id in current_location.connected_location]}, status=status.HTTP_400_BAD_REQUEST)
        elif self.loc_handler.get_location_by_id(location_id).is_occupied:
            return Response({"message": "Location is occupied"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Update player location
            self.char_handler.get_character_by_id(char_id).location = self.loc_handler.get_location_by_id(location_id)

            return Response({"message": f"You have successfully moved to {self.loc_handler.get_location_by_id(location_id).name}",
                             "char_loc_icons": {char_id: (location_id, self.char_handler.get_character_by_id(char_id).image)}}, status=status.HTTP_200_OK)


class PlayerCards(APIView):
    @inject
    def setup(self, request, card_handler: CardHandler, 
              game_session: GameSession, loc_handler: LocationHandler,
              char_handler: CharacterHandler):
        super().setup(request)
        self.card_handler = card_handler
        self.game_session = game_session
        self.loc_handler = loc_handler
        self.char_handler = char_handler

    def get(self, request):
        """
        Get the cards of the current player
        """
        char_id = request.data.get('char_id')
        player_cards = self.char_handler.get_character_by_id(char_id).cards
        return Response({"player_cards": [card.name for card in player_cards]}, status=status.HTTP_200_OK)
    
class PlayerSuggestionView(APIView):
    @inject
    def setup(self, request, game_session: GameSession, 
              char_handler: CharacterHandler, 
              loc_handler: LocationHandler,
              card_handler: CardHandler):
        super().setup(request)
        self.game_session = game_session
        self.char_handler = char_handler
        self.loc_handler = loc_handler
        self.card_handler = card_handler

    def post(self, request):
        character = request.data.get('character')
        location = request.data.get('location')
        weapon = request.data.get('weapon')
        actor = request.data.get('actor')
        actor_name = self.char_handler.get_character_by_id(actor).name
        char_name = self.char_handler.get_character_by_id(character).name

        if not character or not location or not weapon:
            return Response({"error": "Character, location, and weapon are required."}, status=status.HTTP_400_BAD_REQUEST)
        

        message = f"{actor_name} suggested {char_name} with a {weapon} in the {location}"

        # Move the suggested character to the suggested location
        self.char_handler.get_character_by_id(character).location = self.loc_handler.get_location_by_id(location)

        # Find char ids who have the suggested cards
        char_ids_can_disprove = []
        for char in self.char_handler.get_selected_characters():
            if char.char_id != actor and any(card.id in [character, location, weapon] for card in char.cards):
                char_ids_can_disprove.append(char.char_id)

        # Check if the suggestion is correct
        case_file = self.card_handler.case_file
        suggestion_correct = True
        for card_id in [character, location, weapon]:
            if card_id not in [card.id for card in case_file]:
                suggestion_correct = False
                break
        if suggestion_correct:
            message += " and it was correct!"

        return Response({"success": True, 
                         "message": message, 
                         "chars_can_disprove": char_ids_can_disprove,
                         "suggestion_correct": suggestion_correct,
                         "actor_name": actor_name,
                         "char_loc_icons": {character: (location, self.char_handler.get_character_by_id(character).image)}}, status=status.HTTP_200_OK)
    
class PlayerAccusationView(APIView):
    @inject
    def setup(self, request, game_session: GameSession, 
              char_handler: CharacterHandler, 
              loc_handler: LocationHandler,
              card_handler: CardHandler):
        super().setup(request)
        self.game_session = game_session
        self.char_handler = char_handler
        self.loc_handler = loc_handler
        self.card_handler = card_handler


    def post(self, request):
        character = request.data.get('character')
        location = request.data.get('location')
        weapon = request.data.get('weapon')
        actor = request.data.get('actor')
        actor_name = self.char_handler.get_character_by_id(actor).name
        char_name = self.char_handler.get_character_by_id(character).name
        
        # Check if the accusation is correct
        case_file = self.card_handler.case_file
        correct_accusation = True
        for card_id in [character, location, weapon]:
            if card_id not in [card.id for card in case_file]:
                correct_accusation = False
                break
        message = f"{actor_name} accused {char_name} with a {weapon} in the {location}"
        if correct_accusation:
            message += " and it was correct!"
        else:
            message += " and it was incorrect."

        return Response({
            "success": correct_accusation, 
            "message": message,
            "actor_name": actor_name,
            "actor": actor}, status=status.HTTP_200_OK)

class TurnHandler(APIView):
    @inject
    def setup(self, request, game_session: GameSession, 
              char_handler: CharacterHandler, current_game_session: currentGameSession):
        super().setup(request)
        self.game_session = game_session
        self.char_handler = char_handler
        self.current_game_session = current_game_session

    def post(self, request):
        current_turn = request.data.get('current_turn')
        session_id = self.current_game_session.session_id
        selected_players = self.char_handler.serialize_selected()
        current_turn_index = selected_players.index(current_turn)
        next_turn_index = (current_turn_index + 1) % len(selected_players)
        next_turn = selected_players[next_turn_index]
        self.game_session.set_current_turn(next_turn, session_id)
        message = f"It is {self.char_handler.get_character_by_id(next_turn).name}'s turn"
        return Response({"current_turn": next_turn, "message": message, "char_name": self.char_handler.get_character_by_id(next_turn).name }, status=status.HTTP_200_OK)
    
    def get(self, request):
        session_id = self.current_game_session.session_id
        return Response({"current_turn": self.game_session.get_current_turn(session_id)}, status=status.HTTP_200_OK)