from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union, Dict, Set, Tuple, Callable


def check_expectations(expected, actual):
    if expected is not None:
        assert expected == actual, f"expected={expected} actual={actual}"


class Coordinates:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        if not isinstance(other, Coordinates):
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other) -> Coordinates:
        return Coordinates(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> Coordinates:
        return self + (-other)

    def __neg__(self) -> Coordinates:
        return Coordinates(-self.x, -self.y)

    def __hash__(self) -> int:
        return (self.x, self.y).__hash__()

    def __str__(self) -> str:
        return f"({self.x},{self.y})"


class GardenTile(Enum):
    EMPTY = "."
    ROCK = "#"
    START = "S"
    EVEN = "E"
    ODD = "O"

    def __invert__(self) -> GardenTile:
        if self is GardenTile.EVEN:
            return GardenTile.ODD
        if self is GardenTile.ODD:
            return GardenTile.EVEN
        raise ValueError(f"Inverse not supported for {self}.")

    def __str__(self) -> str:
        return self.value


class GardenChunk:
    def __init__(self, chunk_map: List[List[GardenTile]]):
        self._chunk_map = chunk_map

    @property
    def chunk_width(self) -> int:
        return len(self._chunk_map[0])

    @property
    def chunk_height(self) -> int:
        return len(self._chunk_map)

    def check_coordinates(self, coordinates: Coordinates) -> bool:
        return self.check_coordinates_xy(coordinates.x, coordinates.y)

    def check_coordinates_xy(self, x: int, y: int) -> bool:
        return self._check_coordinates_x(x) and self._check_coordinates_y(y)

    def _check_coordinates_x(self, x: int) -> bool:
        return 0 <= x < self.chunk_width

    def _check_coordinates_y(self, y: int) -> bool:
        return 0 <= y < self.chunk_height

    def get_value_coordinates(self, coordinates: Coordinates) -> GardenTile:
        return self.get_value_xy(coordinates.x, coordinates.y)

    def get_value_xy(self, x: int, y: int) -> GardenTile:
        if not self.check_coordinates_xy(x, y):
            return GardenTile.ROCK
        return self._chunk_map[y][x]

    def set_value_coordinates(self, coordinates: Coordinates, value: GardenTile) -> None:
        self.set_value_xy(coordinates.x, coordinates.y, value)

    def set_value_xy(self, x: int, y: int, value: GardenTile) -> None:
        assert self._chunk_map[y][x] is GardenTile.EMPTY
        self._chunk_map[y][x] = value

    @staticmethod
    def copy_from(garden_chunk: GardenChunk) -> GardenChunk:
        map_copy = [[tile for tile in row] for row in garden_chunk._chunk_map]
        return GardenChunk(map_copy)

    def count_evens(self) -> int:
        return self.count_tiles(GardenTile.EVEN)

    def count_odds(self) -> int:
        return self.count_tiles(GardenTile.ODD)

    def count_tiles(self, tile_type: GardenTile) -> int:
        result = 0
        for row in self._chunk_map:
            for tile in row:
                if tile is tile_type:
                    result += 1
        return result

    def __str__(self) -> str:
        result = ""
        for row in self._chunk_map:
            if result != "":
                result += "\n"
            result += "".join(str(item) for item in row)
        return result


class GardenMap(GardenChunk):
    def __init__(self, file_name: str):
        map_template: List[List[GardenTile]] = []
        self._start_coordinates: Optional[Coordinates] = None
        with open(file_name) as f:
            for y, line in enumerate(f):
                line_stripped = line.strip()
                row: List[GardenTile] = []
                map_template.append(row)
                for x, character in enumerate(line_stripped):
                    tile = GardenTile(character)
                    if tile == GardenTile.START:
                        assert self._start_coordinates is None
                        self._start_coordinates = Coordinates(x, y)
                        tile = GardenTile.EMPTY
                    row.append(tile)
        assert self._start_coordinates is not None
        super().__init__(map_template)

    def compute_odds_and_evens(self, steps) -> None:
        one_percent_ish = (int((steps - 1) / 100) + 1)
        to_do: List[Coordinates] = [self._start_coordinates]
        self.set_value_coordinates(self._start_coordinates, GardenTile.EVEN)  # 0-th
        for _ in range(steps):
            if len(to_do) == 0:
                break
            if _ % one_percent_ish == 0:
                print(".", end="")
            previous = to_do
            to_do: List[Coordinates] = []
            for coordinates in previous:
                current_value = self.get_value_coordinates(coordinates)
                neighbors_value = ~current_value
                for vector in [Coordinates(*xy) for xy in [(-1, 0), (0, -1), (0, 1), (1, 0)]]:
                    neighbor_coordinates = coordinates + vector
                    neighbor = self.get_value_coordinates(neighbor_coordinates)
                    if neighbor in [GardenTile.ROCK, neighbors_value]:
                        continue
                    if neighbor is GardenTile.EMPTY:
                        self.set_value_coordinates(neighbor_coordinates, neighbors_value)
                        to_do.append(neighbor_coordinates)
                        continue
                    raise ValueError("That's weird.")


class GardenMapInfinite(GardenMap):
    def __init__(self, file_name: str):
        super().__init__(file_name)
        self._map_chunks: Dict[Coordinates, GardenChunk] = dict()  # {Coordinates(0, 0): self.get_new_chunk()}

    def get_new_chunk(self) -> GardenChunk:
        return GardenChunk([[item for item in row] for row in self._chunk_map])

    def get_chunk_offset_coordinates(self, coordinates: Coordinates) -> Coordinates:
        return self.get_chunk_offset_xy(coordinates.x, coordinates.y)

    def get_chunk_offset_xy(self, x: int, y: int) -> Coordinates:
        return Coordinates(self.get_chunk_offset_x(x), self.get_chunk_offset_y(y))

    def get_chunk_offset_x(self, x: int) -> int:
        return GardenMapInfinite.get_coordinate_offset(x, self.chunk_width)

    def get_chunk_offset_y(self, y: int) -> int:
        return GardenMapInfinite.get_coordinate_offset(y, self.chunk_height)

    @staticmethod
    def get_coordinate_offset(coordinate_value: int, coordinate_size: int) -> int:
        internal_coordinate = coordinate_value % coordinate_size
        return coordinate_value - internal_coordinate

    def check_coordinates_get_chunk_xy(self, x: int, y: int) -> Tuple[GardenChunk, Coordinates]:
        chunk_offset = self.get_chunk_offset_xy(x, y)
        if chunk_offset not in self._map_chunks:
            self._map_chunks[chunk_offset] = self.get_new_chunk()
        return self._map_chunks[chunk_offset], Coordinates(x, y) - chunk_offset

    def check_coordinates_xy(self, x: int, y: int) -> bool:
        self.check_coordinates_get_chunk_xy(x, y)
        return True

    def get_value_xy(self, x: int, y: int) -> GardenTile:
        chunk, chunk_coordinates = self.check_coordinates_get_chunk_xy(x, y)
        return chunk.get_value_coordinates(chunk_coordinates)

    def set_value_xy(self, x: int, y: int, value: GardenTile) -> None:
        chunk, chunk_coordinates = self.check_coordinates_get_chunk_xy(x, y)
        chunk.set_value_coordinates(chunk_coordinates, value)

    def count_evens(self) -> int:
        result = 0
        for chunk in self._map_chunks.values():
            result += chunk.count_evens()
        return result


def part_1(
        file_name: str,
        steps: int,
        expected_result: Optional[int] = None,
) -> int:
    garden = GardenMap(file_name)
    garden.compute_odds_and_evens(steps)
    result = garden.count_evens()
    check_expectations(expected_result, result)
    return result


def part_2(
        file_name: str,
        steps: int,
        expected_result: Optional[int] = None,
) -> int:
    garden = GardenMapInfinite(file_name)
    garden.compute_odds_and_evens(steps)
    result = garden.count_evens()
    check_expectations(expected_result, result)
    return result


"""
###################
## SPOILER ALERT ##
###################
"""


def part_2_optimized_for_particular_input(
        file_name: str,
        steps: int,
        expected_result: Optional[int] = None,
) -> int:
    garden = GardenMapInfinite(file_name)

    chunk_width = garden.chunk_width
    chunk_height = garden.chunk_height
    assert chunk_width == chunk_height
    diameter = chunk_width
    assert diameter % 2 == 1
    radius = (diameter - 1) / 2
    assert radius == int(radius)
    radius = int(radius)
    assert (steps - radius) % diameter == 0
    big_radius = (steps - radius) / diameter
    assert big_radius == int(big_radius)
    big_radius = int(big_radius)
    assert big_radius % 2 == 0

    number_of_full_chunks_odd = big_radius * big_radius
    number_of_full_chunks_even = (big_radius - 1) * (big_radius - 1)
    number_of_big_edges = big_radius - 1
    number_of_small_edges = big_radius

    garden.compute_odds_and_evens(radius + 2 * diameter)
    r"""
        ^ 
      / # \
    < # # # >
      \ # /
        v 
    """

    in_full_even_chunk_count_odds = garden._map_chunks[(Coordinates(0 * diameter, 0 * diameter))].count_odds()
    in_full_odd_chunk_count_odds = garden._map_chunks[(Coordinates(0 * diameter, 1 * diameter))].count_odds()

    in_big_edge_top_left_count_odds = garden._map_chunks[(Coordinates(-1 * diameter, -1 * diameter))].count_odds()
    in_big_edge_top_right_count_odds = garden._map_chunks[(Coordinates(1 * diameter, -1 * diameter))].count_odds()
    in_big_edge_bottom_left_count_odds = garden._map_chunks[(Coordinates(-1 * diameter, 1 * diameter))].count_odds()
    in_big_edge_bottom_right_count_odds = garden._map_chunks[(Coordinates(1 * diameter, 1 * diameter))].count_odds()

    in_small_edge_top_left_count_odds = garden._map_chunks[(Coordinates(-1 * diameter, -2 * diameter))].count_odds()
    in_small_edge_top_right_count_odds = garden._map_chunks[(Coordinates(1 * diameter, -2 * diameter))].count_odds()
    in_small_edge_bottom_left_count_odds = garden._map_chunks[(Coordinates(-1 * diameter, 2 * diameter))].count_odds()
    in_small_edge_bottom_right_count_odds = garden._map_chunks[(Coordinates(1 * diameter, 2 * diameter))].count_odds()

    in_corner_top_count_odds = garden._map_chunks[(Coordinates(0 * diameter, -2 * diameter))].count_odds()
    in_corner_bottom_count_odds = garden._map_chunks[(Coordinates(0 * diameter, 2 * diameter))].count_odds()
    in_corner_left_count_odds = garden._map_chunks[(Coordinates(-2 * diameter, 0 * diameter))].count_odds()
    in_corner_right_count_odds = garden._map_chunks[(Coordinates(2 * diameter, 0 * diameter))].count_odds()

    result = sum((
        in_corner_top_count_odds,
        in_corner_bottom_count_odds,
        in_corner_left_count_odds,
        in_corner_right_count_odds,
        in_full_even_chunk_count_odds * number_of_full_chunks_even,
        in_full_odd_chunk_count_odds * number_of_full_chunks_odd,
        in_big_edge_top_left_count_odds * number_of_big_edges,
        in_big_edge_top_right_count_odds * number_of_big_edges,
        in_big_edge_bottom_left_count_odds * number_of_big_edges,
        in_big_edge_bottom_right_count_odds * number_of_big_edges,
        in_small_edge_top_left_count_odds * number_of_small_edges,
        in_small_edge_top_right_count_odds * number_of_small_edges,
        in_small_edge_bottom_left_count_odds * number_of_small_edges,
        in_small_edge_bottom_right_count_odds * number_of_small_edges,
    ))
    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example.txt", 6, 16))
    print(part_1("input.txt", 64, 3758))

    print(part_2("example.txt", 6, 16))
    print(part_2("example.txt", 10, 50))
    print(part_2("example.txt", 50, 1594))
    print(part_2("example.txt", 100, 6536))
    print(part_2("example.txt", 500, 167004))
    # print(part_2("example.txt", 1000, 668697))
    # print(part_2("example.txt", 5000, 16733044))
    print(part_2_optimized_for_particular_input("input.txt", 26501365, 621494544278648))
