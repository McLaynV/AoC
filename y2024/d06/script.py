from __future__ import annotations

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


class LabTile(Tile):
    def __init__(
            self,
            lab_place: LabPlace,
    ):
        self.lab_place = lab_place
        self._visited_directions_main: set[DirectionUnit] = set()
        self._visited_directions_loop_check: set[DirectionUnit] = set()

    def clean_loop_search(self) -> None:
        self._visited_directions_loop_check.clear()

    @staticmethod
    def get_lab_location(tile_character: str) -> LabTile:
        return LabTile(lab_place=LabPlace.parse_lab_tile(tile_character))

    @property
    def visited(self) -> bool:
        return (len(self._visited_directions_main) > 0) or (len(self._visited_directions_loop_check) > 0)

    def __repr__(self) -> str:
        return "O" if self.visited else self.lab_place.value

    def visit(
            self,
            direction: DirectionUnit,
            checking_for_loops: bool = False,
    ) -> None:
        if checking_for_loops:
            self._visited_directions_loop_check.add(direction)
        else:
            self._visited_directions_main.add(direction)

    def has_visited(self, direction: DirectionUnit) -> bool:
        return (direction in self._visited_directions_main) or (direction in self._visited_directions_loop_check)


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
    lab[current_coordinates].visit(direction)

    assert walk_the_map(lab, current_coordinates, direction) == EndStatus.EXITED

    return lab.count_items_by_criteria(lambda x: x.visited)


def walk_the_map(
        lab: LabMap,
        current_coordinates: Coordinates,
        direction: DirectionUnit,
        checking_for_loops: bool = False,
):
    while True:
        lab[current_coordinates].visit(direction, checking_for_loops)
        next_coordinates = current_coordinates + direction
        if not lab.contains_coordinates(next_coordinates):
            break
        if lab[next_coordinates].lab_place == LabPlace.BLOCK:
            direction = direction.turn_right()
            continue
        if lab[next_coordinates].has_visited(direction):
            return EndStatus.LOOPED
        current_coordinates = next_coordinates
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
    lab[current_coordinates].visit(direction)

    loop_count = 0

    # walk the map
    while True:
        lab[current_coordinates].visit(direction)
        next_coordinates = current_coordinates + direction
        if not lab.contains_coordinates(next_coordinates):
            break
        if lab[next_coordinates].lab_place == LabPlace.BLOCK:
            direction = direction.turn_right()
            continue
        if lab[next_coordinates].lab_place == LabPlace.EMPTY:
            if not lab[next_coordinates].visited:
                # lab_copy = deepcopy(lab)  # this takes too long
                lab[next_coordinates].lab_place = LabPlace.BLOCK
                if walk_the_map(lab, current_coordinates, direction, True) == EndStatus.LOOPED:
                    loop_count += 1
                # clean up:
                for tile in lab.all_tiles():
                    tile.clean_loop_search()
                lab[next_coordinates].lab_place = LabPlace.EMPTY
        current_coordinates = next_coordinates

    return loop_count


if __name__ == '__main__':
    part_1("example.txt", expected_result=41)
    part_1("input.txt", expected_result=4580)
    part_2("example.txt", expected_result=6)
    part_2("input.txt", expected_result=1480)
