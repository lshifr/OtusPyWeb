from console import RectangularFigure, Row, Column, VerticalSeparator, HorizontalSeparator, \
    Digit, VerticalPadding, PaddableRow, TextLine, Text, HorizontalAlignment,PaddableColumn, \
    RectangularBuildingBlock, HorizontalPadding
import random
from operator import itemgetter


def cls():
    print("\n" * 100)


class CardNumber(RectangularFigure):

    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        assert type(number) is int and 0 < number < 100
        high = int(number / 10)
        low = number % 10
        self.figure = Row(
            Digit.get(high),
            HorizontalSeparator(" "),
            Digit.get(low)
        )

    def get_height(self):
        return self.figure.get_height()

    def get_width(self):
        return self.figure.get_width()

    def compile(self, height=None, width=None):
        return self.figure.compile(height=height, width=width)


class UsedCardNumber(CardNumber):
    def __init__(self, number, **kwargs):
        super().__init__(number, **kwargs)

    def compile(self, height=None, width=None):
        compiled = super().compile(height=height, width=width)
        return list(map(
            lambda row: list(map(
                lambda elem: elem if elem != ' ' else "/",
                row
            )),
            compiled
        ))


class Messages(RectangularBuildingBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def clear_messages(self):
        self.messages = []

    def get_current_figure(self, height=None, width=None):
        return Column(
            VerticalSeparator("="),
            Row(
                HorizontalSeparator("="),
                Text(
                    [" "] + self.messages + [" "],
                    hor_align=HorizontalAlignment.LEFT
                ),
                HorizontalSeparator("=")
            ),
            VerticalSeparator("="),
            hor_align=HorizontalAlignment.LEFT
        )


class Card(RectangularBuildingBlock):
    def __init__(self, dealer, card_numbers, **kwargs):
        super().__init__(**kwargs)
        for num in card_numbers:
            assert type(num) is int and 0 < num < 100
        self.dealer = dealer
        self.numbers = card_numbers
        self.used = set()

    def get_current_figure(self, height=None, width=None):
        def get_components():
            yield HorizontalSeparator("|")
            for num in self.numbers:
                yield HorizontalSeparator(" ")
                yield UsedCardNumber(num) if num in self.used else CardNumber(num)
                yield HorizontalSeparator(" ")
                yield HorizontalSeparator("|")

        return Column(
            VerticalSeparator("-"),
            Row(*get_components()),
            VerticalSeparator("-")
        )

    def mark_used_position(self, position: int):
        assert 0 < position <= len(self.numbers)
        self.used.add(self.numbers[position - 1])

    def unmark_position(self, position:int):
        assert 0 < position <= len(self.numbers)
        self.used.remove(self.numbers[position - 1])

    def mark_used_number_if_present(self, num: int):
        if num in self.numbers:
            self.used.add(num)


MAX_NUMBER = 15


class Dealer(object):
    def __init__(self, card_size: int):
        self.card_size = card_size
        self._refresh()

    def _refresh(self):
        self.available = list(range(1, MAX_NUMBER))
        self.used = set()

    def deal_card(self):
        return Card(self, random.choices(range(1, MAX_NUMBER), k=self.card_size))

    def next_number(self):
        if not self.available:
            return None
        num = random.choice(self.available)
        self.available.remove(num)
        self.used.add(num)
        return num

    def check_card(self, card: Card):
        return bool(card.used - self.used)


USER_NAMES = (
    "Bob",
    "John",
    "Lizzie",
    "Kate",
    "Rick",
)


class User(RectangularBuildingBlock):

    def __init__(self, name, game, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.game = game
        self.card = None

    def get_card(self, dealer: Dealer):
        self.card = dealer.deal_card()

    def mark_used_number_if_present(self, num):
        self.card.mark_used_number_if_present(num)

    def mark_used_position(self, position):
        self.card.mark_used_position(position)
        self.game.handle_user_action({
            "action":"MARK_POSITION",
            "user": self,
            "card": self.card,
            "position" : position
        })

    def get_current_figure(self, height=None, width=None):
        return PaddableRow(
            HorizontalPadding(
                Text(["Player", "", self.name.upper()], hor_align=HorizontalAlignment.LEFT),
                10
            )
            ,
            self.card
        )


DEFAULT_CARD_SIZE = 5
DEFAULT_PLAYERS = 4


class Lotto(RectangularBuildingBlock):
    def __init__(
            self,
            card_size=DEFAULT_CARD_SIZE,
            players=DEFAULT_PLAYERS,
            name='You',
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.dealer = Dealer(card_size)
        self.others = [User(n, self) for n in random.sample(USER_NAMES, players-1)]
        self.you = User(name, self)
        self.messages = Messages()
        self.done = False
        all_users = self.others + [self.you]
        for user in all_users:
            user.get_card(self.dealer)

    def get_current_figure(self, height=None, width=None):
        components = [*self.others, self.you]
        if self.messages.messages:
            components.append(self.messages)
        return PaddableColumn(*components)

    def repaint(self):
        cls()
        self.draw()
        self.messages.clear_messages()

    def request_new_number(self):
        num = self.dealer.next_number()
        if num is None:
            self.messages.add_message("No numbers left. Game over!")
            self.done = True
        else:
            for player in self.others:
                player.mark_used_number_if_present(num)
            self.messages.add_message("New number is %d" % num)
        self.repaint()

    def handle_user_action(self, action):
        action_type, user = itemgetter("action", "user")(action)
        if action_type is "MARK_POSITION":
            card, position = itemgetter("card", "position")(action)
            if not self.dealer.check_card(card):
                self.messages.add_message("Player %s tried to cheat!" % user.name)
                card.unmark_position(position)
        self.repaint()

    def mark_position(self, position):
        self.you.mark_used_position(position)

    def quit(self):
        self.messages.add_message("The game stopped at user's request")
        self.repaint()
        self.done = True

    def start_game(self):
        self.repaint()
        while not self.done:
            val = input(
                """Enter choice:
                 n - get next number
                 1, 2, 3, 4, or 5 - mark position as present on your card
                 q - quit the game
                 \n
                 """
            )
            if val == 'n':
                self.request_new_number()
            elif val in ['1', '2', '3', '4', '5']:
                self.mark_position(int(val))
            elif val == 'q':
                self.quit()
            else:
                self.messages.add_message("Unrecognized option")
                self.repaint()



Lotto().start_game()


