from __future__ import annotations

from coordinates import Coordinates

from typing import Iterable, Callable, Generator, TypeVar, Generic


class Tile:
    def __repr__(self) -> str:
        return " "


GenericTile = TypeVar('GenericTile', bound=Tile)


class Map(Generic[GenericTile]):
    def __init__(
            self,
            map_grid: list[list[GenericTile]],
    ):
        self._grid = map_grid

        # check that we have a rectangle
        expected_width = self.width
        for row in self._grid:
            assert expected_width == len(row)

    @classmethod
    def load_from_chars(
            cls,
            map_grid: Iterable[Iterable[str]],
            tile_getter: Callable[[str], GenericTile] = GenericTile,
            strip_rows: bool = False,
    ) -> GenericMap:
        if strip_rows:
            def strip(row: Iterable[str]) -> Iterable[str]:
                for item in row:
                    if item.strip() == item:
                        yield item
        else:
            strip = lambda x: x

        return cls([[tile_getter(tile) for tile in strip(row)] for row in map_grid])

    @classmethod
    def load_from_file(
            cls,
            file_path: str,
            tile_getter: Callable[[str], GenericTile] = GenericTile,
    ) -> GenericMap:
        with open(file_path) as file:
            return cls.load_from_chars(file, tile_getter, strip_rows=True)

    @property
    def height(self) -> int:
        return len(self._grid)

    @property
    def width(self) -> int:
        if self.height == 0:
            return 0
        return len(self._grid[0])

    def contains_coordinates(self, coordinates: Coordinates) -> bool:
        return (0 <= coordinates.from_top < self.height) and (0 <= coordinates.from_left < self.width)

    def get_item(self, from_top: int, from_left: int) -> GenericTile:
        return self._grid[from_top][from_left]

    def __getitem__(self, coordinates: Coordinates) -> GenericTile:
        return self.get_item(coordinates.from_top, coordinates.from_left)

    def set_item(self, from_top: int, from_left: int, value: GenericTile) -> None:
        self._grid[from_top][from_left] = value

    def __setitem__(self, coordinates: Coordinates, value: GenericTile) -> None:
        self.set_item(coordinates.from_top, coordinates.from_left, value)

    def find_items_by_criteria(self, criteria: Callable[[GenericTile], bool]) -> Generator[Coordinates, None, None]:
        for from_top, row in enumerate(self._grid):
            for from_left, tile in enumerate(row):
                if criteria(tile):
                    yield Coordinates(from_top=from_top, from_left=from_left)

    def find_first_item_by_criteria(self, criteria: Callable[[GenericTile], bool]) -> Coordinates | None:
        for coordinates in self.find_items_by_criteria(criteria):
            return coordinates
        return None

    def find_items(self, tile: GenericTile) -> Generator[Coordinates, None, None]:
        return self.find_items_by_criteria(lambda x: x == tile)

    def find_first_item(self, tile: GenericTile) -> Coordinates | None:
        for coordinates in self.find_items(tile):
            return coordinates
        return None

    def count_items_by_criteria(self, criteria: Callable[[GenericTile], bool]) -> int:
        return sum(1 for _ in self.find_items_by_criteria(criteria))

    def __repr__(self) -> str:
        return "\n".join(["".join([
            repr(item) for item in row
        ]) for row in self._grid])

    def all_tiles(self) -> Generator[GenericTile, None, None]:
        for row in self._grid:
            for item in row:
                yield item


GenericMap = TypeVar('GenericMap', bound=Map)
