import random
import threading
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
    def to_dict(self):
        return {
            "rank": self.rank,
            "suit": self.suit
        }


class Deck:
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Deck.ranks for suit in Deck.suits]
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.books = 0

    def draw(self, deck):
        card = deck.draw_card()
        if card:
            self.hand.append(card)
            self.check_for_book()
        return card

    def check_for_book(self):
        rank_count = defaultdict(int)
        for card in self.hand:
            rank_count[card.rank] += 1

        for rank, count in rank_count.items():
            if count == 4:
                self.books += 1
                self.hand = [card for card in self.hand if card.rank != rank]
                return {
                    "action": "book done",
                    "result": "success",
                }


    def has_rank(self, rank):
        return any(card.rank == rank for card in self.hand)

    def give_all_rank(self, rank):
        cards_to_give = [card for card in self.hand if card.rank == rank]
        self.hand = [card for card in self.hand if card.rank != rank]
        return cards_to_give


class GoFishGame:
    def __init__(self, player_names):
        self.deck = Deck()
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0
        self.game_started = False
        self.lock = threading.Lock()
        #self.deal_cards()

    def deal_cards(self):
        num_initial_cards = 7 if len(self.players) <= 3 else 5
        for _ in range(num_initial_cards):
            for player in self.players:
                player.draw(self.deck)

    def start_game(self, player_names):
        with self.lock:
            if not self.game_started:
                self.players = [Player(name) for name in player_names]
                self.deal_cards()
                self.current_player_index = 0
                self.game_started = True

    def next_player(self):
        with self.lock:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            current_player = self.players[self.current_player_index].name
            print(f"Next player's turn: {current_player}")
            logger.info(f"Switching to next player: {current_player}")
            return current_player


    def ask_for_card(self, asking_player_name, target_player_name, rank):
         with self.lock:
            asking_player = next((p for p in self.players if p.name == asking_player_name), None)
            target_player = next((p for p in self.players if p.name == target_player_name), None)
            logger.info(f"Target Player: {target_player}")
            if not target_player or target_player == asking_player:
                return "Invalid target player."

            if target_player.has_rank(rank):
                cards = target_player.give_all_rank(rank)
                asking_player.hand.extend(cards)
                asking_player.check_for_book()
                card_dicts = [card.to_dict() for card in cards]
                return {
                "action": "ask_response",
                "result": "success",
                "cardsReceived": True,
                "message": f"{asking_player.name} got {len(cards)} card(s) of rank {rank} from {target_player.name}.",
                "newCards": card_dicts
            }
            else:
                # Inform the asking player to "Go Fish" and it's the next player's turn
                return {
                "action": "ask_response",
                "result": "go_fish",
                "cardsReceived": False,
                "message": "Go Fish! No cards of that rank. Your turn is over."
            }

    def is_game_over(self):
        return all(player.books >= 1 for player in self.players) or not self.deck.cards

    def is_current_player_turn(self, player):
        check = player == self.players[self.current_player_index].name
        logger.info(f"Checking turn for {player}. Current player: {check}")
        logger.info(f"Checking turn for {player}. Current player: {self.players[self.current_player_index].name}")
        return check
    

    def check_game_end(self):
        # Assuming the game ends when one player collects all cards
        if not self.deck.cards:
            # Find the player with the most books
            max_books = max(player.books for player in self.players)
            winners = [player.name for player in self.players if player.books == max_books]
            return True, winners
        return False, None
