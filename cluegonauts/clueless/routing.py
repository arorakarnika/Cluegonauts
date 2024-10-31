from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/clueless/gameroom/$", consumers.GamePlayersConsumer.as_asgi()),
    re_path(r"ws/clueless/gamestate/$", consumers.GameStateConsumer.as_asgi()),
]
