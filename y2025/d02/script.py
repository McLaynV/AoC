from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from typing import Generator

from expectations_check import validate_result


@dataclass()
class InvalidId:
    half: int

    def __str__(self) -> str:
        return f"{self.half}{self.half}"

    def __int__(self) -> int:
        return int(str(self))

    def increase(self) -> None:
        self.half += 1

    @classmethod
    def get_first_in_interval(cls, interval: Interval) -> InvalidId | None:
        start_str = str(interval.start)
        length = len(start_str)
        half_length = math.floor(length / 2)
        if length % 2 == 0:
            # even length
            invalid_id = InvalidId(half=int(start_str[:half_length]))
            if invalid_id in interval:
                return invalid_id
            # was too small
            invalid_id.increase()
        else:
            # odd length
            invalid_id = InvalidId(half=int("1" + ("0" * half_length)))

        if invalid_id in interval:
            return invalid_id
        # was too big
        return None


@dataclass()
class Interval:
    start: int
    end: int

    @classmethod
    def parse(cls, interval_string: str) -> Interval:
        start, end = interval_string.split("-")
        return cls(int(start), int(end))

    def __contains__(self, item: int | InvalidId) -> bool:
        if not isinstance(item, int):
            item = int(item)
        return self.start <= item <= self.end


def produce_intervals(file_name: str) -> Generator[Interval, None, None]:
    with open(file_name) as f:
        interval_strings = itertools.chain.from_iterable(
            line.split(",")
            for line in f
        )
        for interval_string in interval_strings:
            yield Interval.parse(interval_string)


@validate_result
def sum_invalid_ids(file_name: str) -> int:
    result = 0
    for interval in produce_intervals(file_name):
        invalid_id = InvalidId.get_first_in_interval(interval)
        if invalid_id is None:
            continue
        while invalid_id in interval:
            result += int(invalid_id)
            invalid_id.increase()
    return result


def main():
    print(sum_invalid_ids("example.txt", expected_result=1227775554))
    print(sum_invalid_ids("input.txt", expected_result=19605500130))


if __name__ == "__main__":
    main()
