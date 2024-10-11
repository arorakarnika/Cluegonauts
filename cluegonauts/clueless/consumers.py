import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "select.player", "message": message}
        )

    def select_player(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))

