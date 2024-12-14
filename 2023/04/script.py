from typing import List, Optional


def card_matches(card: str) -> int:
    winning_str, my_str = card.split(":")[1].split("|")
    winning_list = [w for w in winning_str.strip().split(" ") if w != ""]
    my_list = [m for m in my_str.strip().split(" ") if m != ""]

    result = 0
    for m in my_list:
        if m not in winning_list:
            continue
        result += 1
    return result


def part_1(file_name: str, expected_points: Optional[int] = None, expected_count: Optional[int] = None) -> List[int]:
    points = 0
    card_counts = [1]

    last_index = 0
    with open(file_name) as f:
        for index, line in enumerate(f):
            last_index = index
            matches = card_matches(line)
            if matches > 0:
                points += 2 ** (matches - 1)
            while len(card_counts) < index + max(matches, 1) + 1:
                card_counts.append(1)
            for i_next in range(index + 1, index + matches + 1):
                card_counts[i_next] += card_counts[index]
    card_counts = card_counts[:last_index + 1]
    # print(card_counts)
    count = sum(card_counts)

    if expected_points is not None:
        assert expected_points == points, f"expected={expected_points} actual={points}"
    if expected_count is not None:
        assert expected_count == count, f"expected={expected_count} actual={count}"
    return [points, count]


if __name__ == '__main__':
    print(part_1("example.txt", 13, 30))
    print(part_1("input.txt", 23028, 9236992))
