"""Deck."""
from typing import Optional, List
import requests


class Card:
    """Simple dataclass for holding card information."""

    def __init__(self, value: str, suit: str, code: str):
        """Constructor."""
        self.value = value
        self.suit = suit
        self.code = code
        self.top_down = False
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'JACK', 'QUEEN', 'KING', 'ACE']
        self.suits = ['SPADES', 'DIAMONDS', 'HEARTS', 'CLUBS']
        self.codes = {'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '0S', 'JS', 'QS', 'KS', 'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '0D', 'JD', 'QD', 'KD', 'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '0C', 'JC', 'QC', 'KC', 'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '0H', 'JH', 'QH', 'KH'}

    def __str__(self):
        """Str."""
        if self.top_down is False:
            return f'{self.code}'
        else:
            return "??"

    def __repr__(self) -> str:
        """Repr."""
        return self.code

    def __eq__(self, o) -> bool:
        """Eq."""
        if isinstance(o, Card):
            if self.suit == o.suit and self.value == o.value:
                return True
            else:
                return False
        else:
            return False


class Deck:
    """Deck."""

    DECK_BASE_API = "https://deckofcardsapi.com/api/deck/"

    def __init__(self, deck_count: int = 1, shuffle: bool = False):
        """Constructor."""
        self.deck_count = deck_count
        self.is_shuffled = shuffle
        self.deck_id = 0
        self._backup_deck = self._generate_backup_pile(deck_count)
        self.remaining = len(self._backup_deck)
        self.deck_count = deck_count
        if shuffle:
            self._request(Deck.DECK_BASE_API + f'new/shuffle/?deck_count={self.deck_count}')
        else:
            self._request(Deck.DECK_BASE_API + f'new/?deck_count={self.deck_count}')

    def shuffle(self) -> None:
        """Shuffle the deck."""
        self._request(Deck.DECK_BASE_API + f'{self.deck_id}/shuffle/')

    def draw_card(self, top_down: bool = False) -> Optional[Card]:
        """
        Draw card from the deck.

        :return: card instance.
        """
        if len(self._backup_deck) > 0:
            card = self._request(Deck.DECK_BASE_API + f'{self.deck_id}/draw/?count=1')
            print(card)
            if len(card.keys()) > 0:
                try:
                    print(card['images'])
                    suit = card['suit']
                    value = card['value']
                    code = card['code']
                    if Card(value, suit, code) in self._backup_deck:
                        self._backup_deck.remove(Card(value, suit, code))
                    my_card = Card(value, suit, code)
                    my_card.top_down = top_down
                    return my_card
                except Exception:
                    print('no connection')
                    suit = card['suit']
                    value = card['value']
                    code = card['code']
                    if Card(value, suit, code) in self._backup_deck:
                        self._backup_deck.remove(Card(value, suit, code))
                        self.remaining = len(self._backup_deck)
                    return Card(value, suit, code)
            else:
                return None
        else:
            return None

    def _request(self, url: str) -> dict:
        """Update deck."""
        try:
            response = requests.get(url)
            r = response.json()
            self.deck_id = r['deck_id']
            self.remaining = r['remaining']
            return r['cards'][0]
        except IndexError:
            return {}
        except Exception:
            return {'value': self._backup_deck[0].value, 'suit': self._backup_deck[0].suit, 'code': self._backup_deck[0].code}

    @staticmethod
    def _generate_backup_pile(deck_count) -> List[Card]:
        """Generate backup pile."""
        backup_deck = []
        for i in ['SPADES', 'DIAMONDS', 'HEARTS', 'CLUBS']:
            for j in ['2', '3', '4', '5', '6', '7', '8', '9', '0', 'JACK', 'QUEEN', 'KING', 'ACE']:
                backup_deck.append(Card(j, i, i[0] + j[0]))
        backup_deck = deck_count * backup_deck
        return backup_deck


if __name__ == '__main__':
    d = Deck(shuffle=True)
    print(d.remaining)  # 52
    card1 = d.draw_card()  # Random card
    print(card1 in d._backup_deck)  # False
    print(d._backup_deck)  # 51 shuffled cards
    d2 = Deck(deck_count=2)
    print(d2._backup_deck)  # 104 ordered cards (deck after deck)
