from __future__ import annotations

from typing import List, Optional, Union, Dict, Set, Tuple, Callable


def check_expectations(expected, actual):
    if expected is not None:
        assert expected == actual, f"expected={expected} actual={actual}"


def parse_line(line: str, multiplier: int = 1) -> Tuple[str, Tuple[int]]:
    image, numbers_csv = line.strip().split(" ")
    numbers = tuple([int(i) for i in numbers_csv.split(",")] * multiplier)
    image_characters = "?".join([image] * multiplier)
    return image_characters, numbers


def check_filled(row_characters: List[str], numbers: Tuple[int]) -> bool:
    row = "".join(row_characters)
    block_lengths = [len(b) for b in row.split(".") if len(b) > 0]
    return block_lengths == numbers


def brute_force_count_possibilities(row_characters: Union[List[str], str], numbers: Tuple[int]) -> int:
    if isinstance(row_characters, str):
        row_characters = list(row_characters)
    if "?" not in row_characters:
        return 1 if check_filled(row_characters, numbers) else 0
    unknown_index = row_characters.index("?")

    result = 0
    row_characters[unknown_index] = "."
    result += brute_force_count_possibilities(row_characters, numbers)
    row_characters[unknown_index] = "#"
    result += brute_force_count_possibilities(row_characters, numbers)
    row_characters[unknown_index] = "?"


cache: Dict[Tuple[str, Tuple[int]], int] = dict()


def cached_function_results(guts: Callable[[str, Tuple[int]], int]):
    def cached_function(row: str, numbers: Tuple[int]) -> int:
        if (row, numbers) not in cache:
            cache[row, numbers] = guts(row, numbers)
        return cache[row, numbers]

    return cached_function


@cached_function_results
def smarter_count_possibilities(row: str, numbers: Tuple[int]) -> int:
    if len(numbers) == 0:
        return 0 if "#" in row else 1
    number = numbers[0]
    remaining_numbers = numbers[1:]
    needed_length = sum(numbers) + len(remaining_numbers)
    result = 0
    for start_index in range(len(row) - needed_length + 1):
        end_index = start_index + number
        if "#" in row[:start_index]:
            # we already passed a "#"
            break
        if "." in row[start_index:end_index]:
            # we are stretching over a "."
            continue
        if end_index < len(row):
            if "#" == row[end_index]:
                # se are not hitting the input end and the input continues with a "#"
                continue
        result += smarter_count_possibilities(row[end_index + 1:], remaining_numbers)
    return result


def part_1(
        file_name: str,
        multiplier: int,
        expected_result: Optional[int] = None,
) -> int:
    result = 0
    with open(file_name) as f:
        for line in f:
            result += smarter_count_possibilities(*parse_line(line, multiplier))

    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example-0.txt", 1, 6))
    print(part_1("example-1.txt", 1, 1))
    print(part_1("example-2.txt", 1, 4))
    print(part_1("example-3.txt", 1, 1))
    print(part_1("example-4.txt", 1, 1))
    print(part_1("example-5.txt", 1, 4))
    print(part_1("example-6.txt", 1, 10))
    print(part_1("example-22.txt", 1, 21))
    print(part_1("example.txt", 1, 21))
    print(part_1("input.txt", 1, 8193))
    print()
    print(part_1("example-0.txt", 5, 6))
    print(part_1("example-1.txt", 5, 1))
    print(part_1("example-2.txt", 5, 16384))
    print(part_1("example-3.txt", 5, 1))
    print(part_1("example-4.txt", 5, 16))
    print(part_1("example-5.txt", 5, 2500))
    print(part_1("example-6.txt", 5, 506250))
    print(part_1("example-22.txt", 5, 111063614))
    print(part_1("example.txt", 5, 525152))
    print(part_1("input.txt", 5, 45322533163795))
