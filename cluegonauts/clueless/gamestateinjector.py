from .classes import CharacterHandler, LocationHandler, CardHandler, currentGameSession
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
    
    @injector.singleton
    @injector.provider
    def provide_game_session_id(self) -> currentGameSession:
        session_id = self.provide_game_session().create_game_session()
        return currentGameSession(session_id)
