from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import cache, cached_property
import re

from coordinates import Coordinates, Direction
from expectations_check import validate_result
from map_loader import Map, Tile


class TileValue(StrEnum):
    PRESENT = "#"
    EMPTY = "."


@dataclass
class PresentTile(Tile[TileValue]):

    @classmethod
    def representation_from_string(cls, value: str) -> TileValue:
        return TileValue(value)

    def __bool__(self) -> bool:
        return self.representation is TileValue.PRESENT


PresentTile.PRESENT = PresentTile.get_singleton(TileValue.PRESENT)
PresentTile.EMPTY = PresentTile.get_singleton(TileValue.EMPTY)


class PresentRotation(Map[PresentTile]):

    @property
    def size(self) -> int:
        return sum(
            sum(
                1
                for tile in row
                if bool(tile)
            )
            for row in self
        )

    @cached_property
    def frozen(self) -> tuple[tuple[bool, ...], ...]:
        return tuple(
            tuple(
                bool(item)
                for item in row
            )
            for row in self.rows
        )

    def __hash__(self) -> int:
        return hash(self.frozen)

    def __eq__(self, other):
        return self.frozen == other.frozen

    def flip_sides(self) -> PresentRotation:
        return PresentRotation(
            tuple(
                tuple(reversed(row))
            )
            for row in self
        )

    def rotate_left(self) -> PresentRotation:
        return PresentRotation(
            column
            for column in reversed(self.columns)
        )


@dataclass(frozen=True)
class Present:
    shape: PresentRotation

    @cached_property
    def size(self) -> int:
        return self.shape.size

    @cached_property
    def rotations(self) -> tuple[PresentRotation, ...]:
        result: set[PresentRotation] = set()

        rotation = self.shape
        result.add(rotation)
        for _ in range(3):
            rotation = rotation.rotate_left()
            result.add(rotation)

        rotation = rotation.flip_sides()
        result.add(rotation)
        for _ in range(3):
            rotation = rotation.rotate_left()
            result.add(rotation)

        # print("\n")
        # for rotation in result:
        #     print(rotation, "\n")
        # print("\n")
        return tuple(result)

    @classmethod
    def parse(cls, definition: list[str]) -> Present:
        return cls(
            PresentRotation.load_from_chars(
                (
                    TileValue(tile)
                    for tile in row
                )
                for row in definition
            )
        )


@cache
def get_coordinates_of_shape(shape: PresentRotation) -> tuple[Coordinates, ...]:
    return tuple(
        Coordinates(from_top=row_index, from_left=col_index)
        for row_index, row in enumerate(shape)
        for col_index, item in enumerate(row)
        if item
    )


@dataclass
class RegionDefinition:
    width: int
    length: int
    presents_counts: tuple[int, ...]

    def size_can_fit(self, presents: tuple[Present, ...]) -> bool:
        needed_size = 0
        for count, present in zip(self.presents_counts, presents):
            needed_size += count * present.size
        return needed_size <= self.width * self.length


class Region(Map[PresentTile]):
    def can_put(self, offset: Direction, shape: PresentRotation) -> bool:
        for shape_coordinates in get_coordinates_of_shape(shape.frozen):
            offset_coordinates = self.sum_coordinates(shape_coordinates, offset)
            if bool(self[offset_coordinates]):
                return False
        return True

    @staticmethod
    @cache
    def sum_coordinates(shape_coordinates: Coordinates, offset: Direction) -> Coordinates:
        return shape_coordinates + offset

    def change(self, offset: Direction, shape: PresentRotation, new_value: PresentTile) -> None:
        for shape_coordinates in get_coordinates_of_shape(shape.frozen):
            offset_coordinates = self.sum_coordinates(shape_coordinates, offset)
            self[offset_coordinates] = new_value

    def put_present(self, offset: Direction, shape: PresentRotation) -> None:
        self.change(offset, shape, PresentTile.PRESENT)

    def remove_present(self, offset: Direction, shape: PresentRotation) -> None:
        self.change(offset, shape, PresentTile.EMPTY)


def load_input(file_name: str) -> tuple[tuple[Present, ...], tuple[RegionDefinition, ...]]:
    presents: list[Present] = []
    regions: list[RegionDefinition] = []
    with open(file_name) as f:
        present_definition: list[str] = []
        for line in f:
            line = line.strip()
            if re.match(r"^[0-9]+:$", line):
                index = int(line[:-1])
                assert len(presents) == index
                assert len(present_definition) == 0
            elif re.match(r"^[.#]+$", line):
                present_definition.append(line)
            elif not line:
                present = PresentRotation.load_from_chars(present_definition, PresentTile.get_singleton)
                presents.append(Present(present))
                present_definition.clear()
            elif re.match(r"^[0-9]+x[0-9]+:( [0-9]+)+$", line):
                region_size, counts = line.split(": ")
                width, length = region_size.split("x")
                presents_counts = tuple(
                    int(c)
                    for c in counts.split(" ")
                )
                region_definition = RegionDefinition(int(width), int(length), presents_counts)
                regions.append(region_definition)
            else:
                raise ValueError("Unexpected line pattern.")
    return tuple(presents), tuple(regions)


def place_recursively(
        region: Region,
        presents: tuple[Present, ...],
        remaining_counts: list[int],
        start_at_offset_height: int = 0,
        start_at_offset_width: int = 0,
) -> bool:
    # print(region,"\n")
    if sum(remaining_counts) == 0:
        return True
    index = next(
        i
        for i, c in enumerate(remaining_counts)
        if c > 0
    )
    remaining_counts[index] -= 1
    next_present_is_the_same = (remaining_counts[index] > 0)
    present = presents[index]
    for rotation in present.rotations:
        for offset_height in range(start_at_offset_height, region.height - rotation.height + 1):
            for offset_width in range(region.width - rotation.width + 1):
                if (offset_height == start_at_offset_height) and (offset_width < start_at_offset_width):
                    continue
                offset = Direction(offset_height, offset_width)
                if not region.can_put(offset, rotation):
                    continue
                region.put_present(offset, rotation)
                if place_recursively(
                        region, presents, remaining_counts,
                        start_at_offset_height=offset_height if next_present_is_the_same else 0,
                        start_at_offset_width=offset_width + 1 if next_present_is_the_same else 0,
                ):
                    return True
                region.remove_present(offset, rotation)
    remaining_counts[index] += 1
    return False


@validate_result
def part_1(file_name: str) -> int:
    presents, regions = load_input(file_name)
    satisfiable = 0
    for region_definition in regions:
        if not region_definition.size_can_fit(presents):
            continue  # too many presents for that region
        region = Region.initialize_constant_singleton(
            region_definition.length, region_definition.width, PresentTile.EMPTY
        )
        print(satisfiable)
        if place_recursively(region, presents, list(region_definition.presents_counts)):
            satisfiable += 1
            continue
    return satisfiable


def main():
    part_1("example.txt", expected_result=2)
    part_1("input.txt")


if __name__ == "__main__":
    main()
