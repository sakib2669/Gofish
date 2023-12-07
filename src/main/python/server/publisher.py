import logging
from threading import Lock

from gamecomm.server import GameConnection

logger = logging.getLogger(__name__)


class GamePublisher:

    def __init__(self):
        self._subscribers: list[GameConnection] = []
        self._lock = Lock()

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