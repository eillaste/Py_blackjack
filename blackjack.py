"""Blackjack."""
import importlib
import os
import pkgutil
import random
from deck import Deck, Card
from game_view import GameView, FancyView, Move
from strategy import Strategy, HumanStrategy, MirrorDealerStrategy
rn = random
d = Deck


class Hand:
    """Hand."""

    def __init__(self, cards: list = None):
        """Init."""
        if cards is None:
            self.cards = []
        else:
            self.cards = cards
        self.is_double_down = False
        self.is_surrendered = False

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def double_down(self, card: Card) -> None:
        """Double down."""
        # Lisan 1 kaardi käe kaartidesse ja muudan is_double_down tõeseks.
        self.cards.append(card)
        self.is_double_down = True

    def split(self):
        """Split hand."""
        if self.can_split:
            r = random.choice(self.cards)
            self.cards.remove(r)
            return Hand([r])
        else:
            raise ValueError('Invalid hand to split!')

    @property
    def can_split(self) -> bool:
        """Check if hand can be split."""
        if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            return True
        else:
            return False

    @property
    def is_blackjack(self) -> bool:
        """Check if is blackjack."""
        if self.score == 21 and len(self.cards) == 2:
            return True
        else:
            return False

    @property
    def is_soft_hand(self):
        """Check if is soft hand."""
        is_soft = False
        for i in self.cards:
            if i.value == 'ACE':
                is_soft = True

        return is_soft

    @property
    def score(self) -> int:
        """Get score of hand."""
        card_values = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'JACK': 10,
            'QUEEN': 10,
            'KING': 10,
            'ACE': 11}
        hand_value = []
        for i in self.cards:
            hand_value.append(card_values[i.value])
        while sum(hand_value) > 21 and 11 in hand_value:
            for i, j in enumerate(hand_value):
                if j == 11:
                    hand_value[i] = 1
                    break
                else:
                    pass
        return sum(hand_value)


class Player:
    """Player."""

    def __init__(self, name: str, strategy: Strategy, coins: int = 100):
        """Init."""
        self.name = name
        self.coins = coins
        self.hands = []
        self.strategy = strategy
        strategy.player = self

    def join_table(self):
        """Join table."""
        self.coins -= GameController.BUY_IN_COST

    def play_move(self, hand: Hand) -> Move:
        """Play movee."""
        return self.strategy.play_move(hand)

    def split_hand(self, hand: Hand) -> None:
        """Split hand."""
        self.hands.append(hand.split)


class GameController:
    """Game controller."""

    PLAYER_START_COINS = 200
    BUY_IN_COST = 10

    def __init__(self, view: GameView):
        """Init."""
        self.view = view
        self.players = []
        self.house = Hand()
        self.deck = None
        self.decks_count = None

    def start_game(self) -> None:
        """Start game."""
        self.players.clear()
        players_count = self.view.ask_players_count()
        bot_count = self.view.ask_bots_count()
        self.decks_count = self.view.ask_decks_count()
        for p in range(players_count):
            name = self.view.ask_name(p)
            player = Player(f'{name}', HumanStrategy(self.players, self.house, self.decks_count, self.view), GameController.PLAYER_START_COINS)
            self.players.append(player)

        # strategies = GameController.load_strategies()
        for b in range(bot_count):
            player = Player(f'BOT#{b}', MirrorDealerStrategy(self.players, self.house, self.decks_count), GameController.PLAYER_START_COINS)
            self.players.append(player)
        self.deck = Deck(self.decks_count, True)

    def check_players(self) -> list:
        """Check players."""
        active_players = []
        for p in self.players:
            if p.coins < 10:
                pass
            else:
                p.coins -= 10
                active_players.append(p)
                p.hands = []
                p.hands.append(Hand())
        return active_players

    def init_round(self, players):
        """Init round."""
        for i in range(2):
            for player in players:
                if self.deck.remaining > 0:
                    player.hands[0].add_card(self.deck.draw_card())
                else:
                    break
            if self.deck.remaining > 0:
                self.house.add_card(self.deck.draw_card(i == 0))
        print(players)

    def evaluate_split(self, player, hand):
        """Evaluate split."""
        if player.coins < 10 or not hand.can_split:
            pass
        elif self.deck.remaining < 2:
            pass
        else:
            player.coins -= 10
            removed_card = player.hands[0].cards[0]
            player.hands[0].cards.remove(removed_card)
            player.hands.append(Hand([removed_card]))
            player.hands[0].add_card(self.deck.draw_card())
            score = player.hands[0].score
            print(score)

    def evaluate_hand_type(self, hand, player):
        """Evaluate hand type."""
        if type(hand) == Hand:
            score = hand.score
        else:
            hand1 = player.hands[1]
            hand1.add_card(self.deck.draw_card())
            score = hand.score
        return score

    def evaluate_other_moves(self, move, hand, player):
        """Evaluate other moves."""
        if move == Move.STAND:
            return 'break'
        elif move == Move.DOUBLE_DOWN:
            if hand.is_double_down:
                return 'pass'
            elif player.coins < 10:
                return 'pass'
            else:
                player.coins -= 10
                hand.double_down(self.deck.draw_card())
                return 'break'
        elif move == Move.SURRENDER:
            hand.is_surrendered = True
            return 'break'

    def make_moves(self, players):
        """Make moves."""
        for player in players:
            for i, hand in enumerate(player.hands):
                score = self.evaluate_hand_type(hand, player)
                while score < 21:
                    print(player.hands[0].cards)
                    if self.deck.remaining > 0:
                        if len(hand.cards) < 2:
                            hand.add_card(self.deck.draw_card())
                        move = player.play_move(hand)
                        if move == Move.HIT:
                            hand.add_card(self.deck.draw_card())
                            score = hand.score
                        elif move == Move.SPLIT:
                            self.evaluate_split(player, hand)
                        else:
                            if self.evaluate_other_moves(move, hand, player) == 'break':
                                break
                            elif self.evaluate_other_moves(move, hand, player) == 'pass':
                                pass
                    else:
                        break
                else:
                    pass

    def play_house(self):
        """Play house."""
        print(self.house.cards[0].__str__(), self.house.cards[1].__str__())
        self.house.cards[0].top_down = False
        # Pööran kaardi ümber
        print(self.house.cards[0].__str__(), self.house.cards[1].__str__())
        while self.house.score < 17:
            self.house.add_card(self.deck.draw_card())
        else:
            pass
        pass

    def evaluate_score(self, player, hand):
        """Evaluate score."""
        if hand.is_double_down:
            # Kui käsi on double_down...
            if self.house.score == hand.score:
                player.coins += 20
                print('double down, draw')
            elif self.house.score > 21 > hand.score or 22 > hand.score > self.house.score:
                player.coins += 40
                print('double down, you won')
            elif self.house.score > hand.score < 22:
                print('double down but lost')

        elif hand.score > 21 or 22 > self.house.score > hand.score:
            print('you lose, bust')

        elif self.house.score < hand.score < 22 or self.house.score > 22 > hand.score:
            player.coins += 20
            print('you win, beating house, nobody is bust')

        elif self.house.score == hand.score:
            print('draw, get coins back')
            player.coins += 10

    def gimme_money(self, players):
        """Gimme money."""
        for player in players:
            for hand in player.hands:
                print(hand.score)
                if hand.is_blackjack:
                    player.coins += 25
                    print(f'{player.name} hits blackjack and wins 25')
                elif hand.is_surrendered:
                    player.coins += 5
                    print(f'{player.name} surrender, gets 5 back, house wins')
                else:
                    self.evaluate_score(player, hand)

        print(self.house.score)

    def play_round(self) -> bool:
        """Play round."""
        active_players = self.check_players()
        self.init_round(active_players)
        self.make_moves(active_players)
        if self.deck.remaining > 0:
            self.play_house()
            # Käe lõpus toimub raha ümberjagamine.
            self.gimme_money(active_players)
        print(active_players[0].coins)

    def _draw_card(self, top_down: bool = False) -> Card:
        """Draw card."""

    @staticmethod
    def load_strategies() -> list:
        """
        Load strategies.

        @:return list of strategies that are in same package.
        DO NOT EDIT!
        """
        pkg_dir = os.path.dirname(__file__)
        for (module_loader, name, is_pkg) in pkgutil.iter_modules([pkg_dir]):
            importlib.import_module(name)
        return list(filter(lambda x: x.__name__ != HumanStrategy.__name__, Strategy.__subclasses__()))


if __name__ == '__main__':
    game_controller = GameController(FancyView())
    game_controller.start_game()
    while game_controller.play_round():
        pass
