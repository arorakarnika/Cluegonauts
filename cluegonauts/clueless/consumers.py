import json
import threading
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
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
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "status.request", "message": "session_id", "send_to": "gamestate",
                                   "reply_to": "gameplayer"}
        )

    def disconnect(self, close_code): # noqa: ARG002 ; ignore ruff warning for unused parameter
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        char_id  = text_data_json.get("char_selected", None)
        session_id = self.scope["session"].get("game_session", None)

        if text_data_json["subtype"] == "select_player":
            # dynamically get the url for the select character view
            select_character_url = reverse("clueless:select_character")
            response = requests.post(f"http://localhost:8000/{select_character_url}", json={
                'char_id': char_id,
                'session_id': session_id
            })
            if response.status_code == 200:
                data = response.json()
                session_id = data['session_id']
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "status.update", "subtype": "select_player", "message":  message,
                                           "char_selected": char_id, "session_id": str(session_id)}
                )

                if "game_session" not in self.scope["session"]:
                    thread = threading.Thread(target=connect_game_state_consumer, daemon=True)
                    thread.start()
                    # convert uuid to string and store in session
                    self.scope["session"]["game_session"] = str(session_id)
                    self.scope["session"].save()
        elif text_data_json["subtype"] == "start_game":
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", "subtype": "start_game", "message": message,
                                       "char_selected": char_id}
            )

    def status_update(self, event):
        if "send_to" in event and event["send_to"] != "gameplayer":
            return
        match event["subtype"]:
            case "select_player":
                self.select_player(event)
            case "start_game":
                message = event["message"]
                char_id = event["char_selected"]
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

    def status_request(self, event):
        if "send_to" in event and event["send_to"] != "gameplayer":
            return
        event_message = event["message"]
        if event_message == "session_id":
            session_id = self.scope["session"].get("game_session", None)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", "subtype": "session_id", "message": session_id,
                                       "send_to": event["reply_to"]}
            )

    def select_player(self, event):
        if "game_session" not in self.scope["session"]:
            self.scope["session"]["game_session"] = event["session_id"]
            self.scope["session"].save()
        message = event["message"]
        char_id = event["char_selected"]
        self.send(text_data=json.dumps({"message": message, "char_selected": char_id}))
        # Unlock the start game button if there are at least 2 players


class GameStateConsumer(WebsocketConsumer):
    player_card_dict = None

    def connect(self):
        self.room_name = "gameroom"
        self.room_group_name = f"gameroom_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "status.request", "message": "session_id", "send_to": "gameplayer",
                                   "reply_to": "gamestate"}
        )

    def disconnect(self, close_code):  # noqa: ARG002 ; ignore ruff warning for unused parameter
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

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

    def status_update(self, event):
        if "send_to" in event and event["send_to"] != "gamestate":
            return
        match event["subtype"]:
            case "select_player":
                session_id = self.scope["session"].get("game_session", None)
                self.unlock_start(session_id)
            case "session_id":
                if "game_session" not in self.scope["session"]:
                    session_id = event["message"]
                    self.scope["session"]["game_session"] = session_id
                    self.scope["session"].save()

                    self.unlock_start(session_id) # check if enough players joined before GameStateConsumer started
            case "start_game":
                self.setup_game()
            case "player_move":
                self.player_move(event)     

    def status_request(self, event):
        if "send_to" in event and event["send_to"] != "gamestate":
            return
        match event["message"]:
            case "session_id":
                session_id = self.scope["session"].get("game_session", None)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "status.update", "subtype": "session_id" ,"message": session_id,
                                           "send_to": event["reply_to"]}
                )
    def setup_game(self):
        session_id = self.scope["session"].get("game_session", None)

        setup_game_url = reverse("clueless:setup_game")
        response = requests.post(f"http://localhost:8000/{setup_game_url}", json={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            current_turn = data["current_turn"]
            card_selection = data["card_selection"]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status.update", "subtype": "redirect_game"}
            )
            # send message to the player that it is their turn
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{current_turn}_session", 
                {"type": "unlock.turn", "char_id": current_turn}
            )
            # send message to each player with their cards
            for char_id, cards in card_selection.items():
                async_to_sync(self.channel_layer.group_send)(
                    f"gameroom_{char_id}_session", 
                    {"type": "status.update", "message": f"Your cards are: {[card.id for card in cards]}"}
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
        elif response.status_code == 400:
            data = response.json()
            async_to_sync(self.channel_layer.group_send)(
                f"gameroom_{char_id}_session", 
                {"type": "status.update", 
                 "message": data["message"],
                 "success": False}
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
        self.send(text_data=json.dumps({"message": f"You have joined the game, {char_id}"}))

    def disconnect(self, close_code): # noqa: ARG002 ; ignore ruff warning for unused parameter
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def unlock_turn(self, event):
        self.send(text_data=json.dumps({"message": "It is your turn", "unlock": "turn"}))

    def status_update(self, event):
        self.send(text_data=json.dumps({"message": event["message"], "success": event["success"]}))
