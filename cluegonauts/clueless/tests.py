# Use noqa: F401 to ignore unused import error
from django.test import TestCase  # noqa: F401
from channels.testing import WebsocketCommunicator
from channels.testing import ChannelsLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from clueless.consumers import GamePlayersConsumer
from clueless.classes import RoomHandler, HallwayHandler


class ConsumerTests(TestCase):
    # Tests consumer's initial connection
    async def test_quick_game_connection(self):
        client1_communicator = WebsocketCommunicator(GamePlayersConsumer.as_asgi(),  r"ws/clueless/gameroom/$")
        client1_connected, subprotocol = await client1_communicator.connect()
        assert client1_connected

        client2_communicator = WebsocketCommunicator(GamePlayersConsumer.as_asgi(), r"ws/clueless/gameroom/$")
        client2_connected, subprotocol = await client2_communicator.connect()
        assert client2_connected

        await client1_communicator.send_json_to({'message': 'Miss Scarlett has joined the game.'})

        client1_response = await client1_communicator.receive_json_from()
        assert client1_response['message'] == 'Miss Scarlett has joined the game.'
        client2_response = await client2_communicator.receive_json_from()
        assert client2_response['message'] == 'Miss Scarlett has joined the game.'

        await client1_communicator.disconnect()
        await client2_communicator.disconnect()


class SeleniumTests(ChannelsLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(2)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # Verify chat log displays messages
    def test_chat_message_display(self):
        self.selenium.get(f"{self.live_server_url}/clueless/")

        initial_player_log_str = self.selenium.execute_script("return document.querySelector('#player-log').innerHTML") # stores all html inside div with id player-log
        selected_player = self.selenium.execute_script("return document.querySelector('#player-select').value")

        self.selenium.find_element(By.ID, "player-submit").click()

        modified_player_log_str = self.selenium.execute_script("return document.querySelector('#player-log').innerHTML") # stores all html inside div with id player-log
        player_log_difference_str = modified_player_log_str.removeprefix(initial_player_log_str)

        self.assertEqual("{} has joined the game.".format(selected_player) in player_log_difference_str, True)

    # Verify chat log doesn't grow larger than browser
    def test_chat_message_overflow(self):
        self.selenium.get(f"{self.live_server_url}/clueless/")
        self.selenium.maximize_window()
        screen_height = self.selenium.get_window_size()['height']

        initial_height = self.selenium.find_element(By.ID, "player-log").size['height']
        self.selenium.find_element(By.ID, "player-submit").click()
        message_size = self.selenium.find_element(By.ID, "player-log").size['height'] - initial_height
        screen_message_capacity = int(screen_height / message_size)

        for num in range(0, screen_message_capacity + 1):
            self.selenium.find_element(By.ID, "player-submit").click()
        player_log_height = self.selenium.find_element(By.ID, "player-log").size['height']

        self.assertLessEqual(player_log_height, screen_height)



class RoomAndHallwayTests(TestCase):
    def test_room_secret_passage(self):
        room_handler = RoomHandler()
        study = next(room for room in room_handler.rooms if room.id == "study")
        self.assertEqual(study.secret_passage_to, "library")
        study.is_occupied = True
        self.assertTrue(study.is_occupied)

    def test_room_occupancy(self):
        room_handler = RoomHandler()
        dining_room = next(room for room in room_handler.rooms if room.id == "dining_room")
        dining_room.is_occupied = True
        self.assertTrue(dining_room.is_occupied)

    def test_hallway_connections(self):
        hallway_handler = HallwayHandler()
        hallway = hallway_handler.find_hallway("study", "dining_room")
        self.assertIsNotNone(hallway)
        self.assertEqual(set(hallway.connected_rooms), {"study", "dining_room"})

    def test_hallway_occupancy(self):
        hallway_handler = HallwayHandler()
        hallway_handler.set_hallway_occupied("hallway_1", True)
        hallway = next(h for h in hallway_handler.hallways if h.id == "hallway_1")
        self.assertTrue(hallway.is_occupied)
        