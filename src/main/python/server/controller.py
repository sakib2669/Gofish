import logging
from threading import Event
from typing import Callable

from gamecomm.server import GameConnection, ConnectionClosedOK, ConnectionClosedError
from model.game import GoFishGame,Player
from .publisher import GamePublisher


logger = logging.getLogger(__name__)


class GameController:

    RECV_TIMEOUT_SECONDS = 0.250

    def __init__(self, connection: GameConnection, publisher: GamePublisher,
                 Gofishgame:GoFishGame, on_close: Callable[[GameConnection], None]):
        self.connection = connection
        self.publisher = publisher
        self.on_close = on_close
        self._shutdown = Event()
        self.go_fish_game = Gofishgame
        self.is_ready = False
        self.player_name = f"Player {len(publisher.subscribers) + 1}"
        self.initial_hand_sent = False

    def send_initial_hand(self):
        if self.go_fish_game.game_started  and not self.initial_hand_sent:
            player = next((p for p in self.go_fish_game.players if p.name == self.player_name), None)
            if player:
                hand = [card.to_dict() for card in player.hand]
                self.connection.send({"action": "initial_hand", "cards": hand})
                self.initial_hand_sent = True 


    def set_player_ready(self):
        self.is_ready = True
        self.publisher.check_all_players_ready() 

    def draw_card(self, player_name):
        try:
            player = next((p for p in self.go_fish_game.players if p.name == player_name), None)
            if player:
                card = player.draw(self.go_fish_game.deck)
                if card:
                        logger.info(f"{player_name} drew a card: {card}")
                        return {"card": card.to_dict()}  # Convert card to dict
                else:
                        return {"error": "No more cards in the deck"}
            else:
                return None
        except Exception as e:
            logger.error(f"Error drawing card: {e}")
            return {"error": str(e)}


    def notify_turn(self, player_name):
        if self.player_name == player_name:
            self.connection.send({"action": "your_turn"})
        else:
            self.connection.send({"action": "wait", "player_turn": player_name})     



    def run(self):
        logger.info(f"connected to {self.connection} for user {self.connection.uid} in game {self.connection.gid}")
        try:
            while not self._shutdown.is_set():
                try:
                    request = self.connection.recv(self.RECV_TIMEOUT_SECONDS)
                    logger.info(f"received request: {request}")
                    if "action" in request:
                            if request["action"] == "player_ready":
                                self.set_player_ready()
                                self.publisher.check_all_players_ready()
                            elif request["action"] == "draw_card":
                                 if self.go_fish_game.is_current_player_turn(self.player_name):
                                    response = self.draw_card(self.player_name)
                                    logger.info(f"Sending response: {response}")
                                    self.connection.send(response)
                                    if response and "card" in response:
                                        next_player = self.go_fish_game.next_player()
                                        self.publisher.notify_all_players_of_turn(next_player)
                            elif request["action"] == "ask_for_card":
                                # Extract the target player name and rank from the request
                                target_player_name = request.get("targetPlayerName")
                                rank = request.get("rank")
                                # Ensure both target player name and rank are provided
                                if target_player_name and rank:
                                    response = self.go_fish_game.ask_for_card(self.player_name, target_player_name, rank)
                                    logger.info(f"response: {response}")
                                    self.connection.send(response)
                                    if response["result"]:
                                          next_player = self.go_fish_game.next_player()
                                          self.publisher.notify_all_players_of_turn(next_player)
                                else:
                                    self.connection.send({"status": "error", "error": {"message": "Target player name or rank missing"}})
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
