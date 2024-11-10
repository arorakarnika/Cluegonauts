from django.urls import re_path
import injector

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/clueless/gameroom/$", consumers.GamePlayersConsumer.as_asgi()),
    re_path(r"ws/clueless/gamestate/$", consumers.GameStateConsumer.as_asgi()),
    re_path(r"^ws/clueless/usersession/(?P<char_id>\w+)$", consumers.PlayerNotificationConsumer.as_asgi()),
]
