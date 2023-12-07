import logging
from threading import Event
from typing import Callable

from gamecomm.server import GameConnection, ConnectionClosedOK, ConnectionClosedError

from .publisher import GamePublisher


logger = logging.getLogger(__name__)


COMMANDS = {
    "hello": {"event": "HelloEvent", "message": "Hello"},
    "hi": {"event": "HiEvent", "message": "Hi there!"},
    "privet": {"event": "PrivetEvent", "message": "Privet!"},
    "hola": {"event": "HolaEvent", "message": "Hola!"},
    "sup": {"event": "SupEvent", "message": "'sup!"},
    "yo": {"event": "YoEvent", "message": "Yo!"},
}


class GameController:

    RECV_TIMEOUT_SECONDS = 0.250

    def __init__(self, connection: GameConnection, publisher: GamePublisher,
                 on_close: Callable[[GameConnection], None]):
        self.connection = connection
        self.publisher = publisher
        self.on_close = on_close
        self._shutdown = Event()

    def run(self):
        logger.info(f"connected to {self.connection} for user {self.connection.uid} in game {self.connection.gid}")
        try:
            while not self._shutdown.is_set():
                try:
                    request = self.connection.recv(self.RECV_TIMEOUT_SECONDS)
                    logger.info(f"received request: {request}")
                    if "command" in request:
                        command = request["command"].lower()
                        if command in COMMANDS:
                            self.publisher.publish_event(COMMANDS[command])
                            self.connection.send({"status": "ok"})
                        else:
                            self.connection.send(
                                {"status": "error", "error": {"message": f"invalid command '{command}'"}})
                    else:
                        self.connection.send({"status": "error", "error": {"message": "must specify command"}})
                except TimeoutError:
                    pass
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError as err:
            logger.error(f"error communicating with client: {err}")

        self.on_close(self.connection)
        logger.info(f"disconnected from {self.connection} for user {self.connection.uid} in game {self.connection.gid}")

    def stop(self):
        logger.info("handling stop")
        self._shutdown.set()
