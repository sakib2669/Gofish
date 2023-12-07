import logging
from threading import Lock

from gamecomm.server import GameConnection

from .controller import GameController
from .publisher import GamePublisher


logger = logging.getLogger(__name__)


class GameServer:

    def __init__(self, gid: str):
        self.gid = gid
        self.publisher = GamePublisher()
        self._controllers: dict[GameConnection, GameController] = {}
        self._lock = Lock()

    def handle_close(self, connection: GameConnection):
        with self._lock:
            self._controllers.pop(connection)
            self.publisher.remove_subscriber(connection)

    def handle_connection(self, connection):
        controller = GameController(connection, self.publisher, on_close=self.handle_close)
        with self._lock:
            self._controllers[connection] = controller
            self.publisher.add_subscriber(connection)
        controller.run()

    def stop(self):
        with self._lock:
            for controller in self._controllers.values():
                controller.stop()
