from django.shortcuts import render
from injector import inject
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import GameSession
from .classes import CharacterHandler, LocationHandler, CardHandler
from .utils import select_character

@inject
def index(request, char_handler: CharacterHandler):
    char_choices = char_handler.get_all_characters()
    return render( 
        request, 
        "clueless/index.html",
        {"char_choices": char_choices}
        )

@inject
def gameb(request, char_id, loc_handler: LocationHandler):
    # Add char_id to the session
    request.session["char_id"] = char_id
    session_id = request.session.get("game_session", None)
    locations = loc_handler.locations
    blank_ids = ['blank_1', 'blank_2', "blank_3", "blank_4"]
    hallway_ids = [location.location_id for row in locations for location in row if location.name.startswith("Hallway")]
    # Get the selected character ID from the request
    return render(request, "clueless/gameb.html", 
                  {"char_id": char_id,
                   "locations": locations,
                   "blank_ids": blank_ids,
                   "hallway_ids": hallway_ids})

""" 

API views can be called by the websocket consumers to update the game state.

"""
class SelectCharacterView(APIView):
    @inject
    def setup(self, request, char_handler: CharacterHandler, game_session: GameSession):
        super().setup(request)
        self.char_handler = char_handler
        self.game_session = game_session

    def post(self, request):
        char_id = request.data.get('char_id')
        session_id = request.data.get('session_id', None)
        
        if not char_id:
            return Response({"message": "char_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        state, session_id = select_character(char_id, self.char_handler, self.game_session, session_id)
        
        if state:
            return Response({"message": "Character selected successfully", "session_id": session_id}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Character is not available"}, status=status.HTTP_200_OK)
        
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
              char_handler: CharacterHandler):
        super().setup(request)
        self.card_handler = card_handler
        self.game_session = game_session
        self.loc_handler = loc_handler
        self.char_handler = char_handler

    def post(self, request):
        session_id = request.data.get('session_id', None)
        # Deal cards to players
        selected_players = self.char_handler.serialize_selected()
        card_selection = self.card_handler.deal_cards(selected_players)
        self.char_handler.update_character_cards(card_selection)
        # Save the cards to the game session table
        self.game_session.set_case_file_cards([card.id for card in self.card_handler.case_file], session_id)

        # Return current turn
        return Response({"current_turn": selected_players[0], 'card_selection': {k : v.name for k,v in card_selection.items()}}, status=status.HTTP_200_OK)


class PlayerMove(APIView):
    @inject
    def setup(self, request, card_handler: CardHandler, 
              game_session: GameSession, loc_handler: LocationHandler,
              char_handler: CharacterHandler):
        super().setup(request)
        self.card_handler = card_handler
        self.game_session = game_session
        self.loc_handler = loc_handler
        self.char_handler = char_handler

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
        elif location_id not in current_location.connected_location:
            return Response({"message": "Invalid move"}, status=status.HTTP_400_BAD_REQUEST)
        elif self.loc_handler.get_location_by_id(location_id).occupied:
            return Response({"message": "Location is occupied"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Update player location
            self.char_handler.get_character_by_id(char_id).location = self.loc_handler.get_location_by_id(location_id)
            self.char_handler.get_character_by_id(char_id).save()

            return Response({"message": f"You have successfully moved to {self.loc_handler.get_location_by_id(location_id).name}"}, status=status.HTTP_200_OK)


