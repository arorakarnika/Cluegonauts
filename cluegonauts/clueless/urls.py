from django.urls import path

from . import views

app_name = 'clueless'
urlpatterns = [
    path("", views.index, name="index"),
    path("game/<str:char_id>", views.gameb, name="game"),
    path('api/select_character/', views.SelectCharacterView.as_view(), name='select_character'),
    path('api/get_characters/', views.GetCharactersView.as_view(), name='get_characters'),
    path('api/setup_game/', views.SetupGame.as_view(), name='setup_game'),
    path('api/player_cards/', views.PlayerCards.as_view(), name='player_cards'),
    path('api/player_move/', views.PlayerMove.as_view(), name='player_move'),
    path('api/suggest/', views.PlayerSuggestionView.as_view(), name='suggest'),
]