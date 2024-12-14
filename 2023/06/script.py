from __future__ import annotations

import math
from typing import List, Optional


def is_winning(record: int, time: int, x: int) -> bool:
    return x * (time - x) > record


def part_1(
        file_name: str,
        expected_result: Optional[int] = None,
) -> int:
    with open(file_name) as f:
        times: List[int] = [int(t) for t in f.readline().split(":")[1].strip().split(" ") if t != ""]
        records: List[int] = [int(r) for r in f.readline().split(":")[1].strip().split(" ") if r != ""]

    result = 1
    for time, record in zip(times, records):
        faster = [x for x in range(time) if is_winning(record, time, x)]
        result *= len(faster)

    if expected_result is not None:
        msg = f"expected={expected_result} actual={result}"
        assert expected_result == result, msg
    return result


def part_2(
        file_name: str,
        expected_result: Optional[int] = None,
) -> int:
    with open(file_name) as f:
        time = int(f.readline().split(":")[1].replace(" ", "").strip())
        record = int(f.readline().split(":")[1].replace(" ", "").strip())

    # x*x - T*x + R < 0
    # x = (T +- sqrt(T*T - 4*R) / 2
    sqrt_discriminant = math.sqrt(time * time - 4 * record)
    x_minus = (time - sqrt_discriminant) / 2
    x_plus = (time + sqrt_discriminant) / 2

    first = math.floor(x_minus)
    while not is_winning(record, time, first):
        first += 1
    last = math.ceil(x_plus)
    while not is_winning(record, time, last):
        last -= 1

    result = last - first + 1

    if expected_result is not None:
        msg = f"expected={expected_result} actual={result}"
        assert expected_result == result, msg
    return result


if __name__ == '__main__':
    print(part_1("example.txt", 288))
    print(part_1("input.txt", 281600))
    print(part_2("example.txt", 71503))
    print(part_2("input.txt", 33875953))
