from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass
class Coordinates:
    from_top: int
    from_left: int

    def __add__(self, other: Direction) -> Coordinates:
        return Coordinates(
            from_top=self.from_top + other.down,
            from_left=self.from_left + other.right,
        )


@dataclass
class Direction:
    down: int = 0
    right: int = 0

    @property
    def up(self) -> int:
        return -self.down

    @property
    def left(self) -> int:
        return -self.right

    def __add__(self, other: Direction) -> Direction:
        return Direction(
            down=self.down + other.down,
            right=self.right + other.right,
        )

    def __hash__(self):
        return hash((self.down, self.right))

    def turn_back(self) -> Direction:
        return Direction(down=-self.down, right=-self.right)

    def turn_right(self) -> Direction:
        return Direction(down=self.right, right=self.up)

    def turn_left(self) -> Direction:
        return Direction(down=self.left, right=self.down)


class DirectionUnit(Direction, Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)

    def __new__(
            cls,
            down: int,
            right: int,
    ) -> DirectionUnit:
        obj = object.__new__(cls)
        obj._down = down
        obj._right = right
        return obj

    def turn_back(self) -> DirectionUnit:
        match self:
            case DirectionUnit.UP:
                return DirectionUnit.DOWN
            case DirectionUnit.DOWN:
                return DirectionUnit.UP
            case DirectionUnit.RIGHT:
                return DirectionUnit.LEFT
            case DirectionUnit.LEFT:
                return DirectionUnit.RIGHT

    def turn_right(self) -> DirectionUnit:
        match self:
            case DirectionUnit.UP:
                return DirectionUnit.RIGHT
            case DirectionUnit.RIGHT:
                return DirectionUnit.DOWN
            case DirectionUnit.DOWN:
                return DirectionUnit.LEFT
            case DirectionUnit.LEFT:
                return DirectionUnit.UP

    def turn_left(self) -> DirectionUnit:
        match self:
            case DirectionUnit.UP:
                return DirectionUnit.LEFT
            case DirectionUnit.LEFT:
                return DirectionUnit.DOWN
            case DirectionUnit.DOWN:
                return DirectionUnit.RIGHT
            case DirectionUnit.RIGHT:
                return DirectionUnit.UP
