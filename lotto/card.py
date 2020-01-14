from console import RectangularFigure, Row, Digit, HorizontalSeparator, RectangularBuildingBlock, \
    Column, VerticalSeparator


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
                lambda elem: elem if elem != ' ' else "-",
                row
            )),
            compiled
        ))


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

    def unmark_position(self, position: int):
        assert 0 < position <= len(self.numbers)
        self.used.remove(self.numbers[position - 1])

    def mark_used_number_if_present(self, num: int):
        if num in self.numbers:
            self.used.add(num)

    def get_unmarked(self):
        return set(self.numbers) - self.used

    def is_complete(self):
        return not bool(self.get_unmarked())