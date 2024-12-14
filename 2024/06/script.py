from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...expectations_check import validate_result
from ...map_loader import Map, Tile, DirectionUnit


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
    visited: bool = False

    @staticmethod
    def get_lab_location(tile_character: str) -> LabTile:
        return LabTile(lab_place=LabPlace.parse_lab_tile(tile_character))

    def __repr__(self) -> str:
        return "O" if self.visited else self.lab_place.value


class LabMap(Map[LabTile]):
    pass


@validate_result
def part_1(
        file_name: str,
) -> int:
    # load the map, get start coordinates
    lab = LabMap.load_from_file(file_name, LabTile.get_lab_location)
    current_coordinates = lab.find_first_item_by_criteria(lambda x: x.lab_place == LabPlace.START)
    lab[current_coordinates].lab_tile = LabPlace.EMPTY
    lab[current_coordinates].visited = True
    direction = DirectionUnit.UP

    # walk the map
    while True:
        next_coordinates = current_coordinates + direction
        if not lab.contains_coordinates(next_coordinates):
            break
        if lab[next_coordinates].lab_place == LabPlace.BLOCK:
            direction = direction.turn_right()
            continue
        current_coordinates = next_coordinates
        lab[current_coordinates].visited = True

    #print(lab)
    return lab.count_items_by_criteria(lambda x: x.visited)


if __name__ == '__main__':
    print(part_1("example.txt", expected_result=41))
    print(part_1("input.txt"))
