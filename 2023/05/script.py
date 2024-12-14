from __future__ import annotations
from typing import List, Optional, Union


class Range:
    def __init__(self, start: Union[int | str], length: Union[int | str] = 1):
        self.start = int(start)
        self.length = int(length)

    def __repr__(self):
        return f"{self.start}+{self.length}={self.end_excluded}"

    @property
    def end_excluded(self) -> int:
        return self.start + self.length

    def contains_point(self, point: int) -> bool:
        return self.start <= point < self.end_excluded

    def contains_whole_range(self, other: Range) -> bool:
        return (self.start <= other.start) and (other.end_excluded <= self.end_excluded)

    def break_me_into_smaller_by_overlaps_with_another_range(self, other: Range) -> List[Range]:
        points_set = set(
            p
            for p in [other.start, other.end_excluded]
            if self.contains_point(p)
        ).union([self.start, self.end_excluded])
        # set was just used to remove duplicate values
        points_list = list(points_set)
        points_list.sort()
        result: List[Range] = []
        for start, end in zip(points_list, points_list[1:]):
            result.append(Range(start, end - start))
        return result

    def break_ranges_by_overlaps_they_have_with_me(self, ranges: List[Range]) -> List[Range]:
        result: List[Range] = []
        for r in ranges:
            result += r.break_me_into_smaller_by_overlaps_with_another_range(self)
        return result

    def translate(self, source: Range, destination: Range) -> Range:
        return Range(self.start - source.start + destination.start, self.length)

    @staticmethod
    def start_sorter(ranges: List[Range]) -> List[Range]:
        ranges.sort(key=(lambda r: r.start))
        return ranges

    def merge_if_overlap(self, other: Range) -> Optional[Range]:
        smaller, bigger = Range.start_sorter([self, other])
        if smaller.end_excluded < bigger.start:
            return None
        end = max(smaller.end_excluded, bigger.end_excluded)
        return Range(smaller.start, end - smaller.start)

    @staticmethod
    def compress_overlapping_ranges(ranges: List[Range]) -> List[Range]:
        Range.start_sorter(ranges)
        for i in reversed(range(len(ranges) - 1)):
            # Variable i is going from the end because we will be removing from the list
            merged = ranges[i].merge_if_overlap(ranges[i + 1])
            if merged is None:
                continue
            del ranges[i + 1]
            ranges[i] = merged
        return ranges


def part_1(
        file_name: str,
        expected_lowest_location_1: Optional[int] = None,
        expected_lowest_location_2: Optional[int] = None,
) -> List[int]:
    step_values: List[List[Range]] = [[], []]
    next_values: List[List[Range]] = [[], []]

    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if line.startswith("seeds:"):
                numbers = line.split(":")[1].strip().split(" ")
                step_values[0] = [Range(n) for n in numbers]
                step_values[1] = [Range(*numbers[i: i + 2]) for i in range(0, len(numbers), 2)]
                continue
            if ":" in line:
                step_values = [
                    Range.compress_overlapping_ranges(step_values[task_part] + next_values[task_part])
                    for task_part in range(len(step_values))
                ]
                next_values = [[], []]
                # print("step:", step_values)
                continue
            if line == "":
                continue

            start_destination, start_source, length = [int(i) for i in line.split(" ")]
            range_destination = Range(start_destination, length)
            range_source = Range(start_source, length)
            for task_part in range(len(step_values)):
                step_values[task_part] = range_source.break_ranges_by_overlaps_they_have_with_me(step_values[task_part])
                for i in reversed(range(len(step_values[task_part]))):
                    # Variable i is going from the end because we will be removing from the list
                    r = step_values[task_part][i]
                    # r is a result of breaking a range by overlaps with range_source
                    # -> it is either completely inside range_source or completely outside range_source
                    if range_source.contains_whole_range(r):
                        step_values[task_part].remove(r)
                        next_values[task_part].append(r.translate(range_source, range_destination))

    lowest_location = [
        min(r.start for r in step_values[task_part] + next_values[task_part])
        for task_part in range(len(step_values))
    ]
    expected_lowest_location = [expected_lowest_location_1, expected_lowest_location_2]
    for task_part in range(len(expected_lowest_location)):
        if expected_lowest_location[task_part] is not None:
            msg = f"expected={expected_lowest_location[task_part]} actual={lowest_location[task_part]}"
            assert expected_lowest_location[task_part] == lowest_location[task_part], msg
    return lowest_location


if __name__ == '__main__':
    print(part_1("example.txt", 35, 46))
    print(part_1("input.txt", 240320250, 28580589))
