import json
import threading
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .classes import CardHandler
from .models import GameSession
from .utils import select_character, connect_game_state_consumer


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
            status, session_id = select_character(char_id, session_id) # returns true if character is successfully selected, false if character is already selected or unavailable
            if status:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "status_update", "subtype": "select_player", "message":  message,
                                           "char_selected": char_id, "session_id": str(session_id)}
                )

                if "game_session" not in self.scope["session"] and status:
                    thread = threading.Thread(target=connect_game_state_consumer, daemon=True)
                    thread.start()
                    # convert uuid to string and store in session
                    self.scope["session"]["game_session"] = str(session_id)
                    self.scope["session"].save()
        elif text_data_json["subtype"] == "start_game":
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "status_update", "subtype": "start_game", "message": message,
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

    def unlock_start(self, session_id):
        game_session = GameSession()
        session_player_list = game_session.get_selected_players(session_id)
        if len(session_player_list) >= 2:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {"type": "status.update", "subtype": "unlock_start"}
            )

    def status_update(self, event):
        if "send_to" in event and event["send_to"] != "gamestate":
            return
        match event["subtype"]:
            case "select_player":
                session_id = self.scope["session"].get("game_session")
                if session_id is not None:
                    self.unlock_start(session_id)
            case "session_id":
                if "game_session" not in self.scope["session"]:
                    session_id = event["message"]
                    self.scope["session"]["game_session"] = session_id
                    self.scope["session"].save()

                    self.unlock_start(session_id) # check if enough players joined before GameStateConsumer started
            case "start_game":
                self.setup_game()

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

        card_handler = CardHandler()
        selected_cards = [card.id for card in card_handler.select_case_file()]
        game_session = GameSession()
        game_session.set_case_file_cards(selected_cards, session_id)

        self.player_card_dict = card_handler.deal_cards(game_session.get_selected_players(session_id))
        game_session.set_player_cards(self.player_card_dict, session_id)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "status.update", "subtype": "redirect_game"}
        )

        game_session.set_current_turn("ms_scarlet", session_id)
