from django.urls import path

from . import views

app_name = 'clueless'
urlpatterns = [
    path("", views.index, name="index"),
    path("game/<str:char_id>", views.gameb, name="game"),
    path('api/select_character/', views.SelectCharacterView.as_view(), name='select_character'),
    path('api/get_characters/', views.GetCharactersView.as_view(), name='get_characters'),
    path('api/setup_game/', views.SetupGame.as_view(), name='setup_game'),
]