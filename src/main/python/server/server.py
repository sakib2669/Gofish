import logging
from threading import Lock

from gamecomm.server import GameConnection

from model.game import GoFishGame

from .controller import GameController
from .publisher import GamePublisher


logger = logging.getLogger(__name__)


class GameServer:

    def __init__(self, gid: str):
        self.gid = gid
        self.publisher = GamePublisher(self)
        self._controllers: dict[GameConnection, GameController] = {}
        self._lock = Lock()
        self.connected_ = []
        self.go_fish_game = GoFishGame([])
        self.game_started = False

    def send_player_list_to_all(self):
        player_names = [player.name for player in self.go_fish_game.players]
        for controller in self._controllers.values():
            controller.connection.send({
                "action": "update_player_list",
                "playerNames": player_names
            })

    def handle_close(self, connection: GameConnection):
        with self._lock:
            self._controllers.pop(connection)
            self.publisher.remove_subscriber(connection)

    def handle_connection(self, connection):
        controller = GameController(connection, self.publisher,self.go_fish_game, on_close=self.handle_close)
        with self._lock:
            self._controllers[connection] = controller
            self.publisher.add_subscriber(connection)
            self.publisher.add_controller(controller)

        controller.run()

    #def check_all_players_ready(self):
        #if all(controller.is_ready for controller in self._controllers.values()) and not self.game_started:
            #self.start_game()

    def start_game(self):
        if not self.game_started:  
            player_names = [controller.player_name for controller in self._controllers.values()]
            self.go_fish_game.start_game(player_names)
            self.game_started = True
            for controller in self._controllers.values():
                controller.connection.send({"action": "start_game", "message": "The game has started."})
                controller.send_initial_hand()
                
            first_player = self.go_fish_game.players[0].name
            self.publisher.notify_all_players_of_turn(first_player)
            self.send_player_list_to_all()



    def stop(self):
        with self._lock:
            for controller in self._controllers.values():
                controller.stop()
