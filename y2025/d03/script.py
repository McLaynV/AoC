from operator import indexOf
from typing import Generator

from expectations_check import validate_result


def produce_banks(file_name: str) -> Generator[str, None, None]:
    with open(file_name) as f:
        for line in f:
            yield line.strip()


def get_joltage_of_bank(bank: str) -> int:
    first = max(bank[:-1])
    first_index = indexOf(bank, first)
    second = max(bank[first_index + 1:])
    return int(first + second)


@validate_result
def part1(file_name: str) -> int:
    result = 0
    for bank in produce_banks(file_name):
        result += get_joltage_of_bank(bank)
    return result


def main():
    part1("example.txt", expected_result=357)
    part1("input.txt", expected_result=17412)


if __name__ == "__main__":
    main()
