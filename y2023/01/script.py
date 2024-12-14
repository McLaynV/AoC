from typing import Optional


def part_1(file_name: str, expected_result: Optional[int] = None) -> int:
    result = 0

    with open(file_name) as f:
        for line in f:
            digits = [d for d in line if "0" <= d <= "9"]
            result += int(digits[0]) * 10 + int(digits[-1])

    if expected_result is not None:
        assert expected_result == result, f"expected={expected_result} actual={result}"
    return result


digits_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}


def get_first(substring: str) -> int:
    while len(substring) > 0:
        for s, d in digits_map.items():
            if substring.startswith(s):
                return d
        substring = substring[1:]
    raise ValueError("Not found")


def get_last(substring: str) -> int:
    while len(substring) > 0:
        for s, d in digits_map.items():
            if substring.endswith(s):
                return d
        substring = substring[:-1]
    raise ValueError("Not found")


def part_2(file_name: str, expected_result: Optional[int] = None) -> int:
    result = 0

    with open(file_name) as f:
        for line in f:
            result += get_first(line) * 10 + get_last(line)

    if expected_result is not None:
        assert expected_result == result, f"expected={expected_result} actual={result}"
    return result


if __name__ == '__main__':
    print(part_1("1-example.txt", 142))
    print(part_1("input.txt", 55477))
    print(part_2("2-example.txt", 281))
    print(part_2("input.txt", 54431))
