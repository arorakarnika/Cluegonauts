import json
import threading
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
import uuid
import requests
from django.urls import reverse
from .utils import connect_game_state_consumer
import asyncio

class GamePlayersConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "gameroom"
        self.room_group_name = f"gameroom_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code): # noqa: ARG002 ; ignore ruff warning for unused parameter
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        """
        Receive a message from the websocket and process it
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        char_id  = text_data_json.get("char_selected", None)
        session_id = self.scope["session"].get("game_session", None)

        if text_data_json["subtype"] == "select_player":
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "status.update", "subtype": "select_player", "message": message,
                                           "char_selected": char_id, "session_id": session_id}
                )
        elif text_data_json["subtype"] == "start_game":
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", "subtype": "start_game", "message": message,
                                       "char_selected": char_id}
            )
        elif text_data_json["subtype"] == "player_move":
            self.player_move(text_data_json)
        elif text_data_json["subtype"] == "player_suggestion":
            self.handle_suggestion(text_data_json)
        elif text_data_json["subtype"] == "disprove_suggestion":
            async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{text_data_json['data']['actor']}_session", 
                    {"type": "status.update", 
                     "message": f'{text_data_json["char_id"]} showed you a card: {text_data_json["data"]["card"]}', 
                     "success": True}
                )
            self.send(text_data=json.dumps({"message": f"{text_data_json['char_id']} disproved the suggestion"}))

        elif text_data_json["subtype"] == "player_accusation":
            self.handle_accusation(text_data_json)

        elif text_data_json["subtype"] == "character_locations":
            self.get_char_locations()

        elif text_data_json["subtype"] == "end_turn":
            self.turn_handoff(text_data_json)

    def status_update(self, event):
        """
        Receive a status update from another consumer and process it
        """
        if "send_to" in event and event["send_to"] != "gameplayer":
            return
        match event["subtype"]:
            case "select_player":
                self.select_player(event)
            case "start_game":
                message = event["message"]
                char_id = event["char_selected"]
                self.setup_game()
                self.send(text_data=json.dumps({"message": message, "char_selected": char_id}))
            case "session_id":
                if "game_session" not in self.scope["session"]:
                    session_id = event["message"]
                    self.scope["session"]["game_session"] = session_id
                    self.scope["session"].save()
            case "unlock_start":
                self.send(text_data=json.dumps({"message": "unlock_start"}))
            case "redirect_game":
                self.send(text_data=json.dumps({"message": "redirect_game"}))
            case "send_game_message":
                self.send(text_data=json.dumps({"message": event["message"]}))
            case "game_over":
                self.send(text_data=json.dumps({"message": "game_over", "message_text": event["message"], "winner": event["actor"]}))
            case "character_locations":
                self.send(text_data=json.dumps({"message": "character_locations", "char_loc_icons": event["char_loc_icons"]}))


    def select_player(self, event):
        if "game_session" not in self.scope["session"]:
            self.scope["session"]["game_session"] = event["session_id"]
            self.scope["session"].save()
        message = event["message"]
        char_id = event["char_selected"]
        # dynamically get the url for the select character view
        select_character_url = reverse("clueless:select_character")
        response = requests.post(f"http://localhost:8000/{select_character_url}", json={
            'char_id': char_id,
            'session_id': self.scope["session"].get("game_session", None)
        })
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            self.scope["session"]["game_session"] = session_id
 
        self.send(text_data=json.dumps({"message": message, "char_selected": char_id}))
        self.unlock_start(session_id)

    def unlock_start(self, session_id = None):
        get_characters_url = reverse("clueless:get_characters")
        response = requests.get(f"http://localhost:8000/{get_characters_url}")
        if response.status_code == 200:
            data = response.json()
            selected_player_list = data["selected_characters"]
            if len(selected_player_list) >= 2:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "status.update", "subtype": "unlock_start"}
                )

    def setup_game(self):
        """
        This is called when someone clicks the start game button
        """
        session_id = self.scope["session"].get("game_session", None)

        setup_game_url = reverse("clueless:setup_game")
        response = requests.post(f"http://localhost:8000/{setup_game_url}", json={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            current_turn = data["current_turn"]
            card_selection = data["card_selection"]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", 
                                       "subtype": "redirect_game",
                                       "current_turn": current_turn,
                                       "card_selection": card_selection}
            )
    def get_char_locations(self):
        """
        Called to get the character locations to display on the game board
        """
        get_char_loc_url = reverse("clueless:setup_game")
        response = requests.get(f"http://localhost:8000/{get_char_loc_url}")
        if response.status_code == 200:
            data = response.json()
            char_loc_icons = data["char_loc_icons"]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", "subtype": "character_locations", "char_loc_icons": char_loc_icons}
            )

    def handle_suggestion(self, event):
        actor = event["char_id"]
        form_data = event["data"]
        message = event["message"]
        moved_player = form_data["character"]
        location = form_data["location"]
        weapon = form_data["weapon"]
        response = requests.post(f"http://localhost:8000/{reverse('clueless:suggest')}", 
                                 json={
                                        "character": moved_player,
                                        "location": location,
                                        "weapon": weapon,
                                        "actor": actor
                                    })
        if response.status_code == 200:
            data = response.json()
            success = True
            message = data["message"]
            actor_name = data["actor_name"]
            suggestion_correct = data["suggestion_correct"]
            # Notify all players of the suggestion
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", 
                {"type": "status.update", 
                 "message": message,
                 "subtype": "send_game_message",
                 }
            )
            # Move the player on the game board
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", {"type": "status.update",
                                        "subtype": "character_locations",
                                        "char_loc_icons": data["char_loc_icons"]}
            )
            if suggestion_correct:
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_gameroom", 
                    {"type": "status.update", 
                     "message": f"{actor_name} has won the game!",
                     "subtype": "game_over",
                     "actor": actor}
                )
            else:
                # Notify the player who was moved to the suggested location
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{moved_player}_session", {"type": "status.update", 
                                                        "message": f"{actor_name} moved you to {location}", 
                                                        "success": success}
                )
                # Notify players who can disprove the suggestion
                for char_id in data["chars_can_disprove"]:
                    async_to_sync(self.channel_layer.group_send)(
                        f"gameroom_{char_id}_session", 
                        {
                            "type": "status.update", 
                            "message": "disprove_suggestion", 
                            "char_id": char_id,
                            "actor": actor
                        })
        elif response.status_code == 400:
            message = response.json()["error"]
            success = False
            # Send an error message to the player who made the suggestion
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{actor}_session", {"type": "status.update", "message": message, "success": success}
            )

    def handle_accusation(self, event):
        actor = event["char_id"]
        form_data = event["data"]
        moved_player = form_data["character"]
        location = form_data["location"]
        weapon = form_data["weapon"]
        response = requests.post(f"http://localhost:8000/{reverse('clueless:accuse')}", 
                                 json={
                                        "character": moved_player,
                                        "location": location,
                                        "weapon": weapon,
                                        "actor": actor
                                    })
        if response.status_code == 200:
            data = response.json()
            success = data["success"]
            message = data["message"]
            actor = data["actor"]
            actor_name = data["actor_name"]
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", 
                {"type": "status.update", 
                 "message": message,
                 "subtype": "send_game_message",
                 }
            )
            if success:
                # Send accuser a message that they have won
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{actor}_session", {"type": "status.update", "message": "You have won!", "success": success}
                )
                # Send all other players a message that the game is over
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_gameroom", 
                    {"type": "status.update", 
                     "message": f"{actor_name} has won the game!",
                     "subtype": "game_over",
                     "actor": actor}
                )
            elif not success:
                # Send accuser a message that they cannot make more accusations
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{actor}_session", {"type": "accusation.fail", 
                                                  "message": "You cannot make any more accusations.", 
                                                  "success": success}
                )


    def player_move(self, event):
        """
        Handle player moves - check that the move is valid and update the game state

        """
        move_location = event["location_id"]
        char_id = event["char_id"]
        player_move_url = reverse("clueless:player_move")
        response = requests.post(f"http://localhost:8000/{player_move_url}", json={"location_id": move_location,
                                                                                     "char_id": char_id})
        
        if response.status_code == 200:
            data = response.json()
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{char_id}_session", 
                {"type": "status.update", 
                 "message": data["message"],
                 "success": True}
            )
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", {
                    "type": "status.update",
                    "subtype": "send_game_message",
                    "message": f"{char_id} has moved to {move_location}"
                }
            )
            # Move the player on the game board
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", {"type": "status.update", 
                                       "subtype": "character_locations",
                                       "char_loc_icons": data["char_loc_icons"]}
            )

        elif response.status_code == 400:
            data = response.json()
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{char_id}_session", 
                {"type": "status.update", 
                 "message": data["message"],
                 "success": False}
            )

    def turn_handoff(self, event):
        """
        Handle the handoff of turns between players
        message from websocket:             
        'message': "End Turn",
            'subtype': 'end_turn',
            'char_id': charID
        """
        char_id = event["char_id"]
        response = requests.post(f"http://localhost:8000/{reverse('clueless:turn_handler')}", 
                                 json={
                                        "current_turn": char_id,
                                    })
        if response.status_code == 200:
            data = response.json()
            current_turn = data["current_turn"]
            # Unlock the turn for the next player
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{current_turn}_session", {"type": "unlock.turn", "message": data["message"]}
            )
            # Notify all players of the next player
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_gameroom", {"type": "status.update", "subtype": "send_game_message",
                                        "message":  data["message"]}
            )

class PlayerNotificationConsumer(WebsocketConsumer):
    def connect(self):
        char_id = self.scope['url_route']['kwargs']['char_id']
        self.room_name = f"{char_id}_session"
        self.room_group_name = f"gameroom_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({"message": f"Welcome to the game room, {(char_id.replace('_', ' ')).title()}"}))

        # for each room_group_name, send a message to the game player consumer to show player cards and send a message to the player whose turn it is
        self.player_init(char_id=char_id)

    def disconnect(self, close_code): # noqa: ARG002 ; ignore ruff warning for unused parameter
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def unlock_turn(self, event):
        self.send(text_data=json.dumps({"message": "It is your turn", "unlock_turn": True}))

    def player_init(self, char_id):
        # get the player cards
        game_setup_url = reverse("clueless:setup_game")
        response = requests.get(f"http://localhost:8000/{game_setup_url}")
        if response.status_code == 200:
            data = response.json()
            card_selection = data["card_selection"][char_id]
            self.send(text_data=json.dumps({"message": f"Your cards are: {", ".join(card_selection)}. Click on the 'View Your Cards' button to see them at any time.", 
                                            "success": True
                                            }))
            current_turn = data["current_turn"] 
            if current_turn == char_id:
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{current_turn}_session", {"type": "unlock.turn", "char_id": current_turn}
                )
            async_to_sync(self.channel_layer.group_send)(
                "gameroom_gameroom", {"type": "status.update", "subtype": "send_game_message", "message": f"{current_turn} is up next"}
            )


    def status_update(self, event):
        success = event.get("success") or True
        text_data = {"message": event["message"], "success": success}
        if event.get('card_selection'):
            text_data.update({"card_selection": event["card_selection"]})
        if event.get("char_id"):
            text_data.update({"char_id": event["char_id"]})
        if event.get("actor"):
            text_data.update({"actor": event["actor"]})
        self.send(text_data=json.dumps(text_data))

    def accusation_fail(self, event):
        self.send(text_data=json.dumps({"message": event["message"], "success": False, "accusation_fail": True}))