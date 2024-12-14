from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union, Dict, Set, Tuple, Callable, Iterable

import networkx
import matplotlib.pyplot as plt


def check_expectations(expected, actual):
    if expected is not None:
        assert expected == actual, f"expected={expected} actual={actual}"


@dataclass(frozen=True)
class Coordinates:
    x: int
    y: int

    def __add__(self, other) -> Coordinates:
        return Coordinates(self.x + other.x, self.y + other.y)


@dataclass(frozen=True)
class _HikingTileItem:
    character: str
    slippery_path: bool
    neighbor_directions: Set[Coordinates]
    is_walkable: bool = True

    def __str__(self) -> str:
        return self.character


class HikingTile(Enum):
    PATH = _HikingTileItem(".", False, {Coordinates(-1, 0), Coordinates(0, -1), Coordinates(0, 1), Coordinates(1, 0)})
    FOREST = _HikingTileItem("#", False, set(), False)
    SLOPE_WEST = _HikingTileItem("<", True, {Coordinates(-1, 0)})
    SLOPE_NORTH = _HikingTileItem("^", True, {Coordinates(0, -1)})
    SLOPE_SOUTH = _HikingTileItem("v", True, {Coordinates(0, 1)})
    SLOPE_EAST = _HikingTileItem(">", True, {Coordinates(1, 0)})

    @staticmethod
    def parse(character: str, slippery: bool) -> HikingTile:
        for tile in HikingTile:
            if tile.value.character == character:
                if (not tile.value.slippery_path) or slippery:
                    return tile
                return HikingTile.PATH
        raise ValueError(f"Unexpected character '{character}'.")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Crossroad:
    coordinates: Coordinates
    signpost: Dict[Coordinates, Pathway] = field(default_factory=dict)  # first coordinates on the pathway; pathway


@dataclass(frozen=True)
class Pathway:
    from_crossroad: Crossroad
    to_crossroad: Crossroad
    length: int


@dataclass(frozen=True)
class TilesMap:
    _map: List[List[HikingTile]]
    start: Coordinates
    end: Coordinates

    @staticmethod
    def parse(file_name: str, slippery: bool) -> TilesMap:
        map_rows: List[List[HikingTile]] = []
        with open(file_name) as f:
            for line in f:
                row: List[HikingTile] = []
                map_rows.append(row)
                for character in line.strip():
                    row.append(HikingTile.parse(character, slippery))
                if (row[0] != HikingTile.FOREST) or (row[-1] != HikingTile.FOREST):
                    raise ValueError("Expected the map to be surrounded by forests.")
        start = TilesMap.get_single_walkable_in_row(map_rows, 0)
        end = TilesMap.get_single_walkable_in_row(map_rows, len(map_rows) - 1)
        if map_rows[start.y][start.x] not in [HikingTile.PATH, HikingTile.SLOPE_SOUTH]:
            raise ValueError("Unable to start.")
        map_rows[start.y][start.x] = HikingTile.SLOPE_SOUTH
        # map_rows[end.y][end.x] = HikingTile.SLOPE_NORTH
        return TilesMap(map_rows, start, end)

    @staticmethod
    def get_single_walkable_in_row(map_rows: List[List[HikingTile]], y: int) -> Coordinates:
        walkables = [x for x, tile in enumerate(map_rows[y]) if tile.value.is_walkable]
        if len(walkables) != 1:
            raise ValueError(f"Expected 1 walkable, found {len(walkables)}.")
        return Coordinates(walkables[0], y)

    def get_tile_from_coordinates(self, coordinates: Coordinates) -> HikingTile:
        return self._map[coordinates.y][coordinates.x]

    def get_graph(self) -> Graph:
        start_crossroad = Crossroad(self.start)
        end_crossroad = Crossroad(self.end)
        crossroads: Dict[Coordinates, Crossroad] = {
            self.start: start_crossroad,
            self.end: end_crossroad,
        }
        start_tile = self.get_tile_from_coordinates(start_crossroad.coordinates)
        for direction in start_tile.value.neighbor_directions:
            self._find_pathways(start_crossroad, start_crossroad.coordinates + direction, crossroads)
        return Graph(start_crossroad, end_crossroad)

    def _find_pathways(
            self,
            from_crossroad: Crossroad,
            first_step_coordinates: Coordinates,
            crossroads: Dict[Coordinates, Crossroad]
    ):
        if first_step_coordinates in from_crossroad.signpost:
            return  # we already went this way from this crossroad

        previous_coordinates = from_crossroad.coordinates
        current_coordinates = first_step_coordinates
        length = 0

        while True:
            length += 1

            if current_coordinates in (self.end, self.start):
                to_crossroad = crossroads[current_coordinates]
                pathway = Pathway(from_crossroad, to_crossroad, length)
                from_crossroad.signpost[first_step_coordinates] = pathway
                return  # reached the end

            next_directions = self.get_tile_from_coordinates(current_coordinates).value.neighbor_directions
            next_coordinates = [current_coordinates + direction for direction in next_directions]
            next_usable_coordinates = []
            for c in next_coordinates:
                if c == previous_coordinates:
                    continue  # this would be going back
                if not self.get_tile_from_coordinates(c).value.is_walkable:
                    continue  # this would be going into forest
                next_usable_coordinates.append(c)

            if len(next_usable_coordinates) == 0:
                return  # there is no way to go
            if len(next_usable_coordinates) == 1:
                previous_coordinates = current_coordinates
                current_coordinates = next_usable_coordinates[0]
                continue  # there is no crossroad, the pathway goes on

            # we are on a crossroad
            if current_coordinates == from_crossroad.coordinates:
                return  # we returned to the crossroad where we started - no loops allowed
            if current_coordinates not in crossroads:
                # register a new crossroad
                crossroads[current_coordinates] = Crossroad(current_coordinates)
            to_crossroad = crossroads[current_coordinates]
            pathway = Pathway(from_crossroad, to_crossroad, length)
            from_crossroad.signpost[first_step_coordinates] = pathway

            # walk all the new pathways from this crossroad
            for coordinates in next_usable_coordinates:
                self._find_pathways(to_crossroad, coordinates, crossroads)
            return

    def __str__(self) -> str:
        result = ""
        for row in self._map:
            if result != "":
                result += "\n"
            result += "".join(str(item) for item in row)
        return result


@dataclass(frozen=True)
class Graph:
    start_crossroad: Crossroad
    end_crossroad: Crossroad

    def get_all_paths(
            self,
            path_so_far: Optional[List[Pathway]] = None,
            crossroads_so_far: Optional[Set[Coordinates]] = None,
    ) -> Iterable[List[Pathway]]:
        if path_so_far is None:
            path_so_far = []
            current_crossroad = self.start_crossroad
            crossroads_so_far = set()
        else:
            current_crossroad = path_so_far[-1].to_crossroad
        if crossroads_so_far is None:
            crossroads_so_far = {path.to_crossroad.coordinates for path in path_so_far}

        for next_pathway in current_crossroad.signpost.values():
            if next_pathway.to_crossroad.coordinates in crossroads_so_far:
                continue  # we already went through this crossroad

            path_so_far.append(next_pathway)
            crossroads_so_far.add(next_pathway.to_crossroad.coordinates)
            if next_pathway.to_crossroad == self.end_crossroad:
                yield list(path_so_far)  # copy of the list
            yield from self.get_all_paths(path_so_far, crossroads_so_far)
            path_so_far.pop(-1)
            crossroads_so_far.remove(next_pathway.to_crossroad.coordinates)

    def get_longest_path_length(self) -> Optional[int]:
        result = None
        for path in self.get_all_paths():
            path_length = sum(pathway.length for pathway in path)
            if result is None:
                result = path_length
            elif path_length > result:
                result = path_length
                # print(f"...{result}")
        return result

    def get_edges_and_vertices(self) -> Tuple[List[Pathway], List[Crossroad]]:
        edges: List[Pathway] = []
        vertices: List[Crossroad] = []

        vertices_to_do = [self.start_crossroad]
        while len(vertices_to_do) > 0:
            crossroad = vertices_to_do.pop()
            vertices.append(crossroad)
            for pathway in crossroad.signpost.values():
                edges.append(pathway)
                other_crossroad = pathway.to_crossroad
                if (other_crossroad in vertices) or (other_crossroad in vertices_to_do):
                    continue
                vertices_to_do.append(other_crossroad)

        return edges, vertices

    def visualize(self):
        edges_list, vertices_list = self.get_edges_and_vertices()

        g = networkx.Graph()
        for edge in edges_list:
            g.add_edge(
                vertices_list.index(edge.from_crossroad),
                vertices_list.index(edge.to_crossroad),
                weight=edge.length
            )

        plt.figure(figsize=(10, 10))
        pos = networkx.spring_layout(g, seed=6)
        networkx.draw_networkx_nodes(g, pos, node_size=100, node_color="yellow")
        networkx.draw_networkx_edges(g, pos, width=1, alpha=0.5)
        networkx.draw_networkx_labels(g, pos, font_size=6, font_family="sans-serif")
        edge_labels = networkx.get_edge_attributes(g, "weight")
        networkx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=8)
        plt.show()


def part_1(
        file_name: str,
        slippery: bool,
        expected_result: Optional[int] = None,
) -> int:
    hiking_map = TilesMap.parse(file_name, slippery)
    hiking_graph = hiking_map.get_graph()
    # hiking_graph.visualize()
    result = hiking_graph.get_longest_path_length()
    check_expectations(expected_result, result)
    return result


if __name__ == '__main__':
    print(part_1("example.txt", True, 94))
    print(part_1("input.txt", True, 2430))
    print(part_1("example.txt", False, 154))
    print(part_1("input.txt", False, 6534))
