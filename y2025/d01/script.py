from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from expectations_check import validate_result


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


@dataclass
class Dial:
    size: int
    current_value: int
    landed_on_zero: int = 0

    def rotate(self, rotation: Rotation) -> None:
        self.current_value += rotation
        self.current_value %= self.size
        if self.current_value < 0:
            self.current_value += self.size
        if self.current_value == 0:
            self.landed_on_zero += 1


def produce_rotations(file_name: str) -> Generator[Rotation, None, None]:
    with open(file_name) as f:
        for line in f:
            yield Rotation.parse(line)


@validate_result
def part1(file_name: str) -> int:
    dial = Dial(size=100, current_value=50)
    for rotation in produce_rotations(file_name):
        dial.rotate(rotation)
    return dial.landed_on_zero


def main():
    part1("example.txt", expected_result=3)
    part1("input.txt", expected_result=1043)


if __name__ == "__main__":
    main()
