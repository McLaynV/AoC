from __future__ import annotations

from typing import List, Optional, Union, Dict, Set
from enum import Enum


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

    def __neg__(self) -> Coordinates:
        return Coordinates(-self.x, -self.y)

    def __str__(self) -> str:
        return f"{self.x} {self.y}"


class PipeDirection(Enum):
    NORTH = Coordinates(0, -1)
    SOUTH = Coordinates(0, 1)
    WEST = Coordinates(-1, 0)
    EAST = Coordinates(1, 0)

    @property
    def d_x(self) -> int:
        return self.value.x

    @property
    def d_y(self) -> int:
        return self.value.y

    @staticmethod
    def from_coordinates(coordinates: Coordinates) -> PipeDirection:
        for direction in PipeDirection:
            if direction.value == coordinates:
                return direction
        raise ValueError(f"Not a direction: {coordinates}")

    @staticmethod
    def from_xy(d_x: int, d_y: int) -> PipeDirection:
        return PipeDirection.from_coordinates(Coordinates(d_x, d_y))

    def __neg__(self) -> PipeDirection:
        return PipeDirection.from_coordinates(-self.value)


class PipeType(Enum):
    NORTH_SOUTH = ("|", {PipeDirection.NORTH, PipeDirection.SOUTH})
    WEST_EAST = ("-", {PipeDirection.WEST, PipeDirection.EAST})
    NORTH_EAST = ("L", {PipeDirection.NORTH, PipeDirection.EAST})
    NORTH_WEST = ("J", {PipeDirection.NORTH, PipeDirection.WEST})
    SOUTH_WEST = ("7", {PipeDirection.SOUTH, PipeDirection.WEST})
    SOUTH_EAST = ("F", {PipeDirection.SOUTH, PipeDirection.EAST})
    NOTHING = (".", set())
    START = ("S", {PipeDirection.NORTH, PipeDirection.SOUTH, PipeDirection.WEST, PipeDirection.EAST})

    @property
    def letter(self) -> str:
        return self.value[0]

    @property
    def directions(self) -> Set[PipeDirection]:
        return self.value[1]

    def connects_to(self, direction: PipeDirection) -> bool:
        return direction in self.directions

    @staticmethod
    def from_letter(pipe_letter: str) -> PipeType:
        for pipe_type in PipeType:
            if pipe_type.letter == pipe_letter:
                return pipe_type
        raise ValueError(f"Not found: {pipe_letter}")

    @staticmethod
    def from_directions(directions: Set[PipeDirection]):
        for pipe_type in PipeType:
            if pipe_type.directions == directions:
                return pipe_type
        raise ValueError("Not a valid pipe type.")


class PipeTile:
    def __init__(self, pipe_letter: str, x: int, y: int, map: MapOfPipes):
        self.type = PipeType.from_letter(pipe_letter)
        self.coordinates = Coordinates(x, y)
        self.map = map

    def __add__(self, other: PipeDirection) -> PipeTile:
        if not isinstance(other, PipeDirection):
            raise ValueError("It is only allowed to add direction to tile.")
        coordinates = self.coordinates + other.value
        return self.map.get_from_coordinates(coordinates)


class MapOfPipes:
    def __init__(self, file_name: str):
        self.map: List[List[PipeTile]] = []
        start_tile: Optional[PipeTile] = None
        with open(file_name) as f:
            for y, line in enumerate(f):
                row = []
                self.map.append(row)
                for x, character in enumerate(line.strip()):
                    tile = PipeTile(character, x, y, self)
                    row.append(tile)
                    if tile.type == PipeType.START:
                        assert start_tile is None
                        start_tile = tile

        assert start_tile is not None
        self.start: PipeTile = start_tile
        self._find_start_directions(start_tile)
        self._forget_non_loop()

    def _find_start_directions(self, start_tile):
        start_directions = set()
        for direction in PipeDirection:
            neighbor_coordinates = start_tile.coordinates + direction.value
            neighbor = self.get_from_coordinates(neighbor_coordinates)
            if neighbor.type.connects_to(-direction):
                start_directions.add(direction)
        assert len(start_directions) == 2
        start_tile.type = PipeType.from_directions(start_directions)

    def _forget_non_loop(self):
        loop_members = set()
        new_loop_members = {self.start}
        while len(new_loop_members) > 0:
            member = new_loop_members.pop()
            if member in loop_members:
                continue
            loop_members.add(member)
            for direction in member.type.directions:
                new_loop_members.add(member + direction)
        for row in self.map:
            for tile in row:
                if tile not in loop_members:
                    tile.type = PipeType.NOTHING

    def get_from_xy(self, x: int, y: int) -> PipeTile:
        return self.map[y][x]

    def get_from_coordinates(self, coordinates: Coordinates) -> PipeTile:
        return self.get_from_xy(coordinates.x, coordinates.y)

    def get_far_point_distance(self):
        distance = 1
        came_from = [self.start, self.start]
        current_points = [self.start + direction for direction in self.start.type.directions]
        while current_points[0] != current_points[1]:
            new_points: List[PipeTile] = []
            for cp, cf in zip(current_points, came_from):
                next_step = [cp + direction for direction in cp.type.directions if cp + direction != cf]
                assert len(next_step) == 1
                new_points.append(next_step[0])
            came_from = current_points
            current_points = new_points
            distance += 1
        return distance

    def get_internals_count(self) -> int:
        north_types = [t for t in PipeType if PipeDirection.NORTH in t.directions]
        result = 0
        for row in self.map:
            is_internal = False
            for tile in row:
                if tile.type == PipeType.NOTHING:
                    if is_internal:
                        result += 1
                elif tile.type in north_types:
                    is_internal = not is_internal
            assert not is_internal
        return result


def part_1(
        file_name: str,
        expected_result: Optional[int] = None,
) -> int:
    mop = MapOfPipes(file_name)
    result = mop.get_far_point_distance()

    check_expectations(expected_result, result)
    return result


def part_2(
        file_name: str,
        expected_result: Optional[int] = None,
) -> int:
    mop = MapOfPipes(file_name)
    result = mop.get_internals_count()

    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example-1.txt", 4))
    print(part_1("example-2.txt", 8))
    print(part_1("example-3.txt", 23))
    print(part_1("example-4.txt", 70))
    print(part_1("input.txt", 7063))
    print(part_2("example-1.txt", 1))
    print(part_2("example-2.txt", 1))
    print(part_2("example-3.txt", 4))
    print(part_2("example-4.txt", 8))
    print(part_2("input.txt", 589))
