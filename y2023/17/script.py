from __future__ import annotations

import functools
from typing import List, Optional, Union, Dict, Set, Tuple, Callable


def check_expectations(expected, actual):
    if expected is not None:
        assert expected == actual, f"expected={expected} actual={actual}"


X = 0
Y = 1
XY = [X, Y]


@functools.total_ordering
class CityTile:
    INFINITY = 9999999999999999

    def __init__(self, digit: Union[str, int], x: int, y: int):
        self.local_heat_loss = int(digit)
        self.coordinates = [x, y]
        self.minimum_heat_from = [CityTile.INFINITY, CityTile.INFINITY]

    def get_comparable(self) -> Tuple:
        return min(self.minimum_heat_from), min(self.coordinates), self.local_heat_loss

    def __lt__(self, other: CityTile):
        return self.get_comparable() < other.get_comparable()


class CityMap:
    def __init__(
            self,
            file_name: str,
            min_distance: int,
            max_distance: int,
    ):
        self._map: List[List[CityTile]] = []
        with open(file_name) as f:
            for y, line in enumerate(f):
                row = [CityTile(digit, x, y) for x, digit in enumerate(line.strip())]
                self._map.append(row)
        self.min_distance = min_distance
        self.max_distance = max_distance
        self._compute_heat_path()

    def get_tile(self, x: int, y: int) -> CityTile:
        assert self.is_valid_coordinate(x, y)
        return self._map[y][x]

    @property
    def first_tile_index(self) -> Tuple[int, int]:
        return 0, 0

    @property
    def last_tile_index(self) -> Tuple[int, int]:
        return len(self._map[0]) - 1, len(self._map) - 1

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        return (
                self.first_tile_index[X] <= x <= self.last_tile_index[X]
        ) and (
                self.first_tile_index[Y] <= y <= self.last_tile_index[Y]
        )

    def _compute_heat_path(self):
        origin = self.get_tile(*self.first_tile_index)
        origin.minimum_heat_from = [0, 0]
        to_update_neighbors_from = [{origin}, {origin}]
        while sum(len(to_update) for to_update in to_update_neighbors_from) > 0:
            for xy, to_update_neighbors_from_xy in enumerate(to_update_neighbors_from):
                if len(to_update_neighbors_from_xy) == 0:
                    continue
                current = min(to_update_neighbors_from_xy)  # TODO: optimization: only use the current xy dimension here
                to_update_neighbors_from_xy.remove(current)
                for direction in [-1, 1]:
                    current_heat = current.minimum_heat_from[xy]
                    current_coordinates = current.coordinates
                    for delta in range(1, self.max_distance + 1):
                        new_coordinates = tuple(
                            c + direction * delta * abs(i - xy) for i, c in enumerate(current_coordinates)
                        )
                        if not self.is_valid_coordinate(*new_coordinates):
                            break
                        new_tile = self.get_tile(*new_coordinates)
                        current_heat += self.get_tile(*new_coordinates).local_heat_loss
                        if delta < self.min_distance:
                            continue
                        if new_tile.minimum_heat_from[1 - xy] <= current_heat:
                            continue
                        new_tile.minimum_heat_from[1 - xy] = current_heat
                        to_update_neighbors_from[1 - xy].add(new_tile)

    def get_minimum_heat_path_heat_loss(self) -> int:
        return min(self.get_tile(*self.last_tile_index).minimum_heat_from)


def part_1(
        file_name: str,
        min_distance: int,
        max_distance: int,
        expected_result: Optional[int] = None,
) -> int:
    result = CityMap(file_name, min_distance, max_distance).get_minimum_heat_path_heat_loss()
    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example.txt", 1, 3, 102))
    print(part_1("input.txt", 1, 3, 866))
    print(part_1("example.txt", 4, 10, 94))
    print(part_1("input.txt", 4, 10, 1010))
