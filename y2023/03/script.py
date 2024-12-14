from typing import Union, Optional, List


class Number:
    def __init__(self, value: Union[int, str], start_index: int, end_index: int):
        self.value = int(value)
        self.start_index = start_index
        self.end_index = end_index

    def __str__(self) -> str:
        return f"{self.value}[{self.start_index}..{self.end_index}]"

    def touches_index(self, index: int) -> bool:
        return (self.start_index - 1) <= index <= (self.end_index + 1)


class Row:
    def __init__(self, row: str):
        self.is_part: List[bool] = []
        self.is_gear: List[bool] = []
        self.numbers: List[Number] = []

        number_string = ""
        for index, char in enumerate(f".{row}."):  # surround with dots
            # building a number
            if "0" <= char <= "9":
                self.is_part.append(False)
                self.is_gear.append(False)
                number_string += char
                continue
            # not building a number
            self.is_part.append(char != ".")
            self.is_gear.append(char == "*")
            # finished building a number
            if number_string != "":
                self.numbers.append(Number(number_string, index - len(number_string), index - 1))
                number_string = ""


def sum_part_numbers_in_middle_row(previous: Row, current: Row, following: Row) -> int:
    row_length = len(previous.is_part)
    assert row_length == len(current.is_part)
    assert row_length == len(following.is_part)

    result = 0
    part_indices = [i for i in range(row_length) if (previous.is_part[i] or current.is_part[i] or following.is_part[i])]
    for number in current.numbers:
        for index in part_indices:
            if number.touches_index(index):
                result += number.value
                break
    return result


def sum_gear_ratios_in_middle_row(rows: List[Row]) -> int:
    result = 0
    for gear_index in range(len(rows[1].is_gear)):
        if not rows[1].is_gear[gear_index]:
            continue
        numbers = [number for row in rows for number in row.numbers if number.touches_index(gear_index)]
        if len(numbers) != 2:
            continue
        result += numbers[0].value * numbers[1].value
    return result


def part_12(
        file_name: str,
        expected_result_parts: Optional[int] = None,
        expected_result_gears: Optional[int] = None
) -> List[int]:
    result_parts = 0
    result_gears = 0
    rows: List[Row] = []

    with open(file_name) as f:
        empty_row: Optional[Row] = None
        for line in f:
            line_without_eol = line.strip()
            # initialize
            while len(rows) < 2:
                if empty_row is None:
                    empty_row = Row(len(line_without_eol) * ".")
                rows.append(empty_row)
            # parse third row
            rows.append(Row(line_without_eol))
            # process second row
            result_parts += sum_part_numbers_in_middle_row(*rows)
            result_gears += sum_gear_ratios_in_middle_row(rows)
            # forget first row
            rows = rows[1:]
        # process the last row of the input
        rows.append(empty_row)
        result_parts += sum_part_numbers_in_middle_row(*rows)
        result_gears += sum_gear_ratios_in_middle_row(rows)

    if expected_result_parts is not None:
        msg = f"expected_parts={expected_result_parts} actual_parts={result_parts}"
        assert expected_result_parts == result_parts, msg
    if expected_result_gears is not None:
        msg = f"expected_gears={expected_result_gears} actual_gears={result_gears}"
        assert expected_result_gears == result_gears, msg
    return [result_parts, result_gears]


if __name__ == '__main__':
    print(part_12("example.txt", 4361, 467835))
    print(part_12("input.txt", 528799, 84907174))
