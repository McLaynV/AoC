from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Generator

from expectations_check import validate_result


@dataclass()
class InvalidId:
    part: int
    repetitions: int

    def __str__(self) -> str:
        return str(self.part) * self.repetitions

    def __int__(self) -> int:
        return int(str(self))

    def increase(self) -> None:
        self.part += 1


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


def get_first_invalid_id_in_interval_or_smaller(
        interval: Interval,
        repetitions: int,
) -> InvalidId:
    start_str = str(interval.start)
    length = len(start_str)
    part_length = length // repetitions
    if length % repetitions == 0:
        part_str = start_str[:part_length]
    else:
        part_str = "1" + ("0" * part_length)
    return InvalidId(part=int(part_str), repetitions=repetitions)


def get_all_invalid_ids_with_fixed_repetitions_in_interval(
        interval: Interval,
        repetitions: int,
) -> set[int]:
    result = set()
    invalid_id = get_first_invalid_id_in_interval_or_smaller(interval, repetitions)
    while int(invalid_id) < interval.start:
        invalid_id.increase()
    while invalid_id in interval:
        result.add(int(invalid_id))
        invalid_id.increase()
    return result


def get_all_invalid_ids_in_interval(interval: Interval) -> set[int]:
    result = set()
    for repetitions in range(2, len(str(interval.end)) + 1):
        invalid_ids = get_all_invalid_ids_with_fixed_repetitions_in_interval(interval, repetitions)
        result |= invalid_ids
    return result


def produce_intervals(file_name: str) -> Generator[Interval, None, None]:
    with open(file_name) as f:
        interval_strings = itertools.chain.from_iterable(
            line.split(",")
            for line in f
        )
        for interval_string in interval_strings:
            yield Interval.parse(interval_string)


@validate_result
def part1(file_name: str) -> int:
    result = 0
    for interval in produce_intervals(file_name):
        invalid_ids = get_all_invalid_ids_with_fixed_repetitions_in_interval(interval, 2)
        for invalid_id in invalid_ids:
            result += int(invalid_id)
    return result


@validate_result
def part2(file_name: str) -> int:
    result = 0
    for interval in produce_intervals(file_name):
        for invalid_id in get_all_invalid_ids_in_interval(interval):
            result += invalid_id
    return result


def main():
    part1("example.txt", expected_result=1227775554)
    part1("input.txt", expected_result=19605500130)
    part2("example.txt", expected_result=4174379265)
    part2("input.txt", expected_result=36862281418)


if __name__ == "__main__":
    main()
