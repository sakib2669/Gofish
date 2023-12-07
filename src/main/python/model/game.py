import random
from collections import defaultdict


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


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
        self.deal_cards()

    def deal_cards(self):
        num_initial_cards = 7 if len(self.players) <= 3 else 5
        for _ in range(num_initial_cards):
            for player in self.players:
                player.draw(self.deck)

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(f"Next player's turn: {self.players[self.current_player_index].name}")

    def ask_for_card(self, asking_player, target_player_name, rank):
        target_player = next((p for p in self.players if p.name == target_player_name), None)
        if not target_player or target_player == asking_player:
            return "Invalid target player."

        if target_player.has_rank(rank):
            cards = target_player.give_all_rank(rank)
            asking_player.hand.extend(cards)
            asking_player.check_for_book()
            return f"{asking_player.name} got {len(cards)} cards of {rank} from {target_player.name}"
        else:
            drawn_card = asking_player.draw(self.deck)
            if drawn_card and drawn_card.rank == rank:
                return f"Go Fish! Lucky draw! {asking_player.name} got a {rank}."
            else:
                return "Go Fish! No luck this time."
        return message

    def is_game_over(self):
        return all(player.books >= 1 for player in self.players) or not self.deck.cards

    def is_current_player_turn(self, player):
        return player == self.players[self.current_player_index]

    def check_game_end(self):
        # Assuming the game ends when one player collects all cards
        if not self.deck.cards:
            # Find the player with the most books
            max_books = max(player.books for player in self.players)
            winners = [player.name for player in self.players if player.books == max_books]
            return True, winners
        return False, None