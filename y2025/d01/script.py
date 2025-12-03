from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Literal

from expectations_check import validate_result


@dataclass
class RotationSplit:
    full_circles: int
    partial: int


class Rotation(int):
    @classmethod
    def parse(cls, value: str) -> Rotation:
        amount = int(value[1:])
        match value[0]:
            case "R":
                direction = 1
            case "L":
                direction = -1
            case _:
                raise ValueError(f"Unexpected direction '{value[0]}'.")
        return cls(direction * amount)

    @property
    def direction_sign(self) -> Literal[-1, 1]:
        return -1 if self < 0 else 1

    def split(self, circle_size: int) -> RotationSplit:
        quotient, remainder = divmod(abs(self), circle_size)
        return RotationSplit(full_circles=quotient, partial=remainder * self.direction_sign)


@dataclass
class Dial:
    size: int
    current_value: int
    landed_on_zero: int = 0
    went_through_zero: int = 0

    def rotate(self, rotation: Rotation) -> None:
        self._process_rotation(rotation)
        if self.current_value == 0:
            self.landed_on_zero += 1

    def _process_rotation(self, rotation: Rotation) -> None:
        rotation_split = rotation.split(self.size)
        self.went_through_zero += rotation_split.full_circles
        if not rotation_split.partial:
            return
        started_on_zero = (self.current_value == 0)
        self.current_value += rotation_split.partial
        if 0 < self.current_value < self.size:
            return
        if not started_on_zero:
            self.went_through_zero += 1
        if self.current_value < 0:
            self.current_value += self.size
        if self.current_value >= self.size:
            self.current_value -= self.size


def produce_rotations(file_name: str) -> Generator[Rotation, None, None]:
    with open(file_name) as f:
        for line in f:
            yield Rotation.parse(line)


@validate_result
def part(part2: bool, file_name: str) -> int:
    dial = Dial(size=100, current_value=50)
    for rotation in produce_rotations(file_name):
        dial.rotate(rotation)
    return dial.went_through_zero if part2 else dial.landed_on_zero


def main():
    part(False, "example.txt", expected_result=3)
    part(False, "input.txt", expected_result=1043)
    part(True, "example.txt", expected_result=6)
    part(True, "input.txt", expected_result=5963)


if __name__ == "__main__":
    main()
