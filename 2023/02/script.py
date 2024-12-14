from typing import Dict, Optional

R = "red"
G = "green"
B = "blue"


def check_or_zero(game: str, rules: Dict[str, int]) -> int:
    game_label, game_steps = [part.strip() for part in game.split(":")]
    game_label_game, game_number_str = [part.strip() for part in game_label.split(" ") if part.strip() != ""]
    if game_label_game != "Game":
        raise ValueError(f"Something be bad here: {game}")
    game_number = int(game_number_str)
    steps = [part.strip() for part in game_steps.replace(";", ",").split(",")]
    for step in steps:
        number, color = step.split(" ")
        if int(number) > rules[color]:
            return 0
    return game_number


def part_1(file_name: str, rules: Dict[str, int], expected_result: Optional[int] = None) -> int:
    result = 0

    with open(file_name) as f:
        for line in f:
            result += check_or_zero(line, rules)

    if expected_result is not None:
        assert expected_result == result, f"expected={expected_result} actual={result}"
    return result


def power_of_game(game: str) -> int:
    encountered_maximums = {R: 0, G: 0, B: 0}
    game_label, game_steps = [part.strip() for part in game.split(":")]
    steps = [part.strip() for part in game_steps.replace(";", ",").split(",")]
    for step in steps:
        number, color = step.split(" ")
        encountered_maximums[color] = max(encountered_maximums[color], int(number))
    return encountered_maximums[R] * encountered_maximums[G] * encountered_maximums[B]


def part_2(file_name: str, expected_result: Optional[int] = None) -> int:
    result = 0

    with open(file_name) as f:
        for line in f:
            result += power_of_game(line)

    if expected_result is not None:
        assert expected_result == result, f"expected={expected_result} actual={result}"
    return result


if __name__ == '__main__':
    rules_1 = {R: 12, G: 13, B: 14}
    print(part_1("example.txt", rules_1, 8))
    print(part_1("input.txt", rules_1, 2632))
    print(part_2("example.txt", 2286))
    print(part_2("input.txt", 69629))
