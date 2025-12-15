from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from typing import Iterable, Callable, Generator, overload, Self

from coordinates import Coordinates


@dataclass
class Tile[Representation: StrEnum](ABC):
    representation: Representation

    def __post_init__(self) -> None:
        if len(self.representation) != 1:
            raise ValueError(f"Expected tile representation of length 1, got {len(self.representation)} instead.")

    def __repr__(self) -> str:
        return str(self.representation)

    def __str__(self) -> str:
        return str(self.representation)

    @classmethod
    @abstractmethod
    def representation_from_string(cls, value: str) -> Representation:
        raise NotImplementedError()

    @classmethod
    def get_new(cls, value: str) -> Self:
        return cls(cls.representation_from_string(value))

    @classmethod
    @cache
    def get_singleton(cls, value: str) -> Self:
        return cls.get_new(value)


class Map[GenericTile: Tile](list[list[GenericTile]]):
    def __init__(
            self,
            map_grid: Iterable[Iterable[GenericTile]],
    ):
        super().__init__(map_grid)

        # check that we have a rectangle
        expected_width = self.width
        for row in self:
            assert expected_width == len(row)

    @classmethod
    def load_from_chars(
            cls,
            map_grid: Iterable[Iterable[str]],
            tile_getter: Callable[[str], GenericTile] = GenericTile,
            strip_rows: bool = False,
    ) -> Self:
        if strip_rows:
            def strip(row: Iterable[str]) -> Iterable[str]:
                for item in row:
                    if item.strip() == item:
                        yield item
        else:
            strip = lambda x: x

        return cls(
            [
                [
                    tile_getter(tile)
                    for tile in strip(row)
                ]
                for row in map_grid]
        )

    @classmethod
    def load_from_file(
            cls,
            file_path: str,
            tile_getter: Callable[[str], GenericTile] = GenericTile,
    ) -> Self:
        with open(file_path) as file:
            return cls.load_from_chars(file, tile_getter, strip_rows=True)

    @classmethod
    def initialize_constant(cls, height: int, width: int, factory: Callable[[], GenericTile]) -> Self:
        return cls(
            [
                [
                    factory()
                    for _ in range(width)
                ]
                for _ in range(height)
            ]
        )

    @classmethod
    def initialize_constant_singleton(cls, height: int, width: int, value: GenericTile) -> Self:
        return cls.initialize_constant(height, width, lambda: value)

    @property
    def height(self) -> int:
        return len(self)

    @property
    def width(self) -> int:
        if self.height == 0:
            return 0
        return len(self.get_row(0))

    def contains_coordinates(self, coordinates: Coordinates) -> bool:
        return (0 <= coordinates.from_top < self.height) and (0 <= coordinates.from_left < self.width)

    def get_item(self, from_top: int, from_left: int) -> GenericTile:
        return self.get_row(from_top)[from_left]

    def get_row(self, from_top: int) -> list[GenericTile]:
        return super().__getitem__(from_top)

    @property
    def rows(self) -> Self:
        return self

    def get_column(self, column_index: int) -> tuple[GenericTile, ...]:
        return tuple(
            row[column_index]
            for row in self.rows
        )

    @property
    def columns(self) -> tuple[tuple[GenericTile, ...], ...]:
        return tuple(
            self.get_column(column_index)
            for column_index in range(self.width)
        )

    @overload
    def __getitem__(self, coordinates: Coordinates) -> GenericTile:
        ...

    @overload
    def __getitem__(self, row_index: int) -> list[GenericTile]:
        ...

    def __getitem__(self, selection: Coordinates | int) -> GenericTile | list[GenericTile]:
        if isinstance(selection, Coordinates):
            return self.get_item(selection.from_top, selection.from_left)
        else:
            return self.get_row(selection)

    def set_item(self, from_top: int, from_left: int, value: GenericTile) -> None:
        self.get_row(from_top)[from_left] = value

    def __setitem__(self, coordinates: Coordinates, value: GenericTile) -> None:
        self.set_item(coordinates.from_top, coordinates.from_left, value)

    def find_items_by_criteria(self, criteria: Callable[[GenericTile], bool]) -> Generator[Coordinates, None, None]:
        for from_top, row in enumerate(self):
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
        return "\n".join(
            "".join(
                str(item)
                for item in row
            )
            for row in self
        )

    def all_tiles(self) -> Generator[GenericTile, None, None]:
        for row in self:
            for item in row:
                yield item
