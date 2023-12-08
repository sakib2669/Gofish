import logging
from threading import Lock

from gameauth import TokenValidator, InvalidTokenError
from gamecomm.server import WsGameListener

from .server import GameServer


logger = logging.getLogger(__name__)


class GameListener:

    def __init__(self, local_ip, local_port, token_validator: TokenValidator):
        self.local_ip = local_ip
        self.local_port = local_port
        self.token_validator = token_validator
        self._servers: dict[str, GameServer] = {}
        self._lock = Lock()

    def _find_or_create_server(self, gid: str):
        with self._lock:
            if gid not in self._servers:
                self._servers[gid] = GameServer(gid)
                logger.info(f"created new server for gid {gid}")
            return self._servers[gid]

    def handle_authentication(self, gid: str, token: str):
        try:
            return self.token_validator.validate(gid, token)
        except InvalidTokenError:
            return None

    def handle_connection(self, connection):
        server = self._find_or_create_server(connection.gid)
        server.handle_connection(connection)
        #connection.send({'action': 'set_gid', 'gid': connection.gid})

    def handle_stop(self):
        with self._lock:
            for server in self._servers.values():
                server.stop()

    def run(self):
        logger.info(f"listening on {self.local_ip}:{self.local_port}")
        logger.info(f"authentication is {'enabled' if self.token_validator else 'disabled'}")
        listener = WsGameListener(self.local_ip, self.local_port,
                                  on_connection=self.handle_connection,
                                  on_authenticate=self.handle_authentication if self.token_validator else None,
                                  on_stop=self.handle_stop)
        listener.run()
