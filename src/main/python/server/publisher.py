import logging
from threading import Lock

from gamecomm.server import GameConnection

logger = logging.getLogger(__name__)


class GamePublisher:

    def __init__(self, game_server):
        self._subscribers: list[GameConnection] = []
        self._lock = Lock()
        self._controllers = []
        self.game_server = game_server


    def add_controller(self, controller):
        self._controllers.append(controller)

    def get_all_controllers(self):
        return self._controllers
    
    def add_subscriber(self, connection: GameConnection):
        logger.info(f"adding subscriber {connection}")
        with self._lock:
            self._subscribers.append(connection)

    def remove_subscriber(self, connection: GameConnection):
        logger.info(f"removing subscriber {connection}")
        with self._lock:
            self._subscribers.remove(connection)

    def publish_event(self, event):
        logger.info(f"publishing event: {event}")
        with self._lock:
            subscribers = list(self._subscribers)
        for subscriber in subscribers:
            subscriber.send(event)

    def notify_all_players_of_turn(self, current_player_name):
        for controller in self._controllers:
            controller.notify_turn(current_player_name)

    def check_all_players_ready(self):
        if not self.game_server.game_started and all(controller.is_ready for controller in self.get_all_controllers()):
            # Logic to notify GameServer to start the game
            self.game_server.start_game()
    
    @property
    def subscribers(self):
        with self._lock:
            return list(self._subscribers)
