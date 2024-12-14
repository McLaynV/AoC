from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum

from coordinates import Coordinates, DirectionUnit
from expectations_check import validate_result
from map_loader import Map, Tile


class LabPlace(Enum):
    BLOCK = "#"
    EMPTY = "."
    START = "^"

    @staticmethod
    def parse_lab_tile(tile_character: str) -> LabPlace:
        for option in LabPlace:
            if option.value == tile_character:
                return option
        raise ValueError(f"Unexpected tile character: {tile_character}")


@dataclass
class LabTile(Tile):
    lab_place: LabPlace
    visited_directions: set[DirectionUnit] = field(default_factory=lambda: set())

    @staticmethod
    def get_lab_location(tile_character: str) -> LabTile:
        return LabTile(lab_place=LabPlace.parse_lab_tile(tile_character))

    @property
    def visited(self) -> bool:
        return len(self.visited_directions) > 0

    def __repr__(self) -> str:
        return "O" if self.visited else self.lab_place.value


class LabMap(Map[LabTile]):
    pass


class EndStatus(Enum):
    EXITED = 0
    LOOPED = 1


@validate_result
def part_1(
        file_name: str,
) -> int | None:
    # load the map, get start coordinates
    lab = LabMap.load_from_file(file_name, LabTile.get_lab_location)
    current_coordinates = lab.find_first_item_by_criteria(lambda x: x.lab_place == LabPlace.START)
    lab[current_coordinates].lab_place = LabPlace.EMPTY
    direction = DirectionUnit.UP
    lab[current_coordinates].visited_directions.add(direction)

    assert walk_the_map(lab, current_coordinates, direction) == EndStatus.EXITED

    # print(lab)
    return lab.count_items_by_criteria(lambda x: x.visited)


def walk_the_map(
        lab: LabMap,
        current_coordinates: Coordinates,
        direction: DirectionUnit,
):
    while True:
        lab[current_coordinates].visited_directions.add(direction)
        next_coordinates = current_coordinates + direction
        if not lab.contains_coordinates(next_coordinates):
            break
        if lab[next_coordinates].lab_place == LabPlace.BLOCK:
            direction = direction.turn_right()
            continue
        if direction in lab[next_coordinates].visited_directions:
            # print("\n--- looped:")
            # print(lab)
            return EndStatus.LOOPED
        current_coordinates = next_coordinates
    # print("\n--- exited:")
    # print(lab)
    return EndStatus.EXITED


@validate_result
def part_2(
        file_name: str,
) -> int:
    # load the map, get start coordinates
    lab = LabMap.load_from_file(file_name, LabTile.get_lab_location)
    current_coordinates = lab.find_first_item_by_criteria(lambda x: x.lab_place == LabPlace.START)
    lab[current_coordinates].lab_place = LabPlace.EMPTY
    direction = DirectionUnit.UP
    lab[current_coordinates].visited_directions.add(direction)

    loop_count = 0

    # walk the map
    while True:
        lab[current_coordinates].visited_directions.add(direction)
        next_coordinates = current_coordinates + direction
        if not lab.contains_coordinates(next_coordinates):
            break
        if lab[next_coordinates].lab_place == LabPlace.BLOCK:
            direction = direction.turn_right()
            continue
        if lab[next_coordinates].lab_place == LabPlace.EMPTY:
            if not lab[next_coordinates].visited:
                lab_copy = deepcopy(lab)  # this takes too long
                lab_copy[next_coordinates].lab_place = LabPlace.BLOCK
                print(".", end="")
                if walk_the_map(lab_copy, current_coordinates, direction) == EndStatus.LOOPED:
                    loop_count += 1
                # print("\n")
                # print(lab)
        current_coordinates = next_coordinates

    # print(lab)
    return loop_count


if __name__ == '__main__':
    part_1("example.txt", expected_result=41)
    part_1("input.txt", expected_result=4580)
    part_2("example.txt", expected_result=6)
    part_2("input.txt", expected_result=None)
