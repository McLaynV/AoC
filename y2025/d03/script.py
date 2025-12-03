from operator import indexOf
from typing import Generator

from expectations_check import validate_result


def produce_banks(file_name: str) -> Generator[str, None, None]:
    with open(file_name) as f:
        for line in f:
            yield line.strip()


def get_joltage_of_bank(bank: str, count: int) -> str:
    if count == 1:
        return max(bank)
    strongest = max(bank[:-count + 1])
    strongest_index = indexOf(bank, strongest)
    remaining_bank = bank[strongest_index + 1:]
    remaining_count = count - 1
    return strongest + get_joltage_of_bank(remaining_bank, remaining_count)


@validate_result
def part(count: int, file_name: str) -> int:
    result = 0
    for bank in produce_banks(file_name):
        result += int(get_joltage_of_bank(bank, count))
    return result


def main():
    part(2, "example.txt", expected_result=357)
    part(2, "input.txt", expected_result=17412)
    part(12, "example.txt", expected_result=3121910778619)
    part(12, "input.txt", expected_result=172681562473501)

    part(5, "multi_zero.txt", expected_result=98000)


if __name__ == "__main__":
    main()
