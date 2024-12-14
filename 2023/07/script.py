from __future__ import annotations

from typing import List, Optional, Union, Dict
from enum import Enum
import functools


def check_expectations(expected, actual):
    if expected is not None:
        assert expected == actual, f"expected={expected} actual={actual}"


@functools.total_ordering
class HandType(Enum):
    def __new__(cls, value, groups_counts):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.main_groups_counts = groups_counts
        return obj

    FIVE_OF_KIND = (6, [5])
    FOUR_OF_KIND = (5, [4, 1])
    FULL_HOUSE = (4, [3, 2])
    THREE_OF_KIND = (3, [3, 1, 1])
    TWO_PAIR = (2, [2, 2, 1])
    ONE_PAIR = (1, [2, 1, 1, 1])
    HIGH_CARD = (0, [1, 1, 1, 1, 1])

    def __repr__(self) -> str:
        return self.name

    def __lt__(self, other) -> bool:
        return self.value < other.value

    @staticmethod
    def parse(cards: str, alternative: bool) -> HandType:
        groups: Dict[str, int] = {}
        for c in cards:
            if c not in groups:
                groups[c] = 0
            groups[c] += 1
        if alternative and (CardLabelAlternative.C_J.label in groups):
            jokers = groups[CardLabelAlternative.C_J.label]
            del groups[CardLabelAlternative.C_J.label]
        else:
            jokers = 0
        groups_counts = [v for v in groups.values()]
        groups_counts.sort(reverse=True)
        if len(groups_counts) == 0:
            groups_counts = [0]
        groups_counts[0] += jokers
        for h in HandType:
            if h.main_groups_counts == groups_counts:
                return h
        raise ValueError(f"Cards {cards}, groups {groups_counts}, alternative {alternative}")


@functools.total_ordering
class CardLabelOriginal(Enum):
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    C_A = (14, "A")
    C_K = (13, "K")
    C_Q = (12, "Q")
    C_J = (11, "J")
    C_T = (10, "T")
    C_9 = (9, "9")
    C_8 = (8, "8")
    C_7 = (7, "7")
    C_6 = (6, "6")
    C_5 = (5, "5")
    C_4 = (4, "4")
    C_3 = (3, "3")
    C_2 = (2, "2")

    def __str__(self) -> str:
        return self.label

    def __lt__(self, other) -> bool:
        return self.value < other.value

    @staticmethod
    def parse(character: str) -> CardLabelOriginal:
        for lbl in CardLabelOriginal:
            if lbl.label == character:
                return lbl


@functools.total_ordering
class CardLabelAlternative(Enum):
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    C_A = (14, "A")
    C_K = (13, "K")
    C_Q = (12, "Q")
    C_T = (10, "T")
    C_9 = (9, "9")
    C_8 = (8, "8")
    C_7 = (7, "7")
    C_6 = (6, "6")
    C_5 = (5, "5")
    C_4 = (4, "4")
    C_3 = (3, "3")
    C_2 = (2, "2")
    C_J = (1, "J")

    def __str__(self) -> str:
        return self.label

    def __lt__(self, other) -> bool:
        return self.value < other.value

    @staticmethod
    def parse(character: str) -> CardLabelAlternative:
        for lbl in CardLabelAlternative:
            if lbl.label == character:
                return lbl


@functools.total_ordering
class Hand:
    def __init__(self, cards: str, bid: Union[str, int], alternative: bool):
        assert len(cards) == 5, f"Expected 5 cards, got this: {cards}"
        label_class = CardLabelAlternative if alternative else CardLabelOriginal
        self.cards = [label_class.parse(c) for c in cards]
        self.bid = int(bid)
        self.hand_type = HandType.parse(cards, alternative)

    def __repr__(self) -> str:
        cards = "".join(str(c) for c in self.cards)
        return f"{cards} {self.bid} {self.hand_type.name}"

    def __eq__(self, other) -> bool:
        return self.cards == other.cards

    def __lt__(self, other) -> bool:
        if self.hand_type != other.hand_type:
            return self.hand_type < other.hand_type
        for s, o in zip(self.cards, other.cards):
            if s != o:
                return s < o
        return False  # equal


def part_1(
        file_name: str,
        alternative: bool,
        expected_result: Optional[int] = None,
) -> int:
    hands: List[Hand] = []
    with open(file_name) as f:
        for line in f:
            cards, bid = line.split(" ")
            hands.append(Hand(cards, bid, alternative))
    hands.sort()
    # print(hands)

    result = 0
    for index, hand in enumerate(hands):
        result += (index + 1) * hand.bid

    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example.txt", False, 6440))
    print(part_1("input.txt", False, 246409899))
    print(part_1("example.txt", True, 5905))
    print(part_1("input.txt", True, 244848487))
