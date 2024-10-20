import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .utils import select_character

class GamePlayersConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "gameroom"
        self.room_group_name = f"gameroom_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        char_id  = text_data_json["char_selected"]
        session_id = self.scope["session"].get("game_session", None)

        status, session_id = select_character(char_id, session_id) # returns true if character is successfully selected, false if character is already selected or unavailable
        if status:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "select.player", "message":  message, "char_selected": char_id}
            )

        # convert uuid to string and store in session
        self.scope["session"]["game_session"] = str(session_id)
        self.scope["session"].save()

    def select_player(self, event):
        message = event["message"]
        char_id = event["char_selected"]
        self.send(text_data=json.dumps({"message": message, "char_selected": char_id}))

