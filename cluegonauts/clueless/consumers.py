import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .classes import CharacterHandler


class GamePlayersConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "gameroom"
        self.room_group_name = f"gameroom_{self.room_name}"
        self.char_handler = CharacterHandler(selected=self.scope['session'].get("char_handler", None)) if self.scope['session'].get("char_handler", None) else CharacterHandler()
        # Save character handler to session
        self.scope["session"]["char_handler"] = self.char_handler.serialize_selected()
        self.scope["session"].save()
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

        if self.char_handler.is_available(char_id):
            self.char_handler.set_selected(char_id)
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "select.player", "message":  message, "char_selected": char_id}
            )

    def select_player(self, event):
        message = event["message"]
        char_id = event["char_selected"]
        self.send(text_data=json.dumps({"message": message, "char_selected": char_id}))

