from .classes import CharacterHandler, LocationHandler, CardHandler
from .models import GameSession
import injector

class GameStateModule(injector.Module):
    """
    Allows for injection in view functions using the @inject decorator
    """
    @injector.singleton
    @injector.provider
    def provide_location_handler(self) -> LocationHandler:
        return LocationHandler()

    @injector.singleton
    @injector.provider
    def provide_character_handler(self) -> CharacterHandler:
        return CharacterHandler()
    
    @injector.singleton
    @injector.provider
    def provide_card_handler(self) -> CardHandler:
        return CardHandler()
    
    @injector.singleton
    @injector.provider
    def provide_game_session(self) -> GameSession:
        return GameSession()
