from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property, cache

from expectations_check import validate_result


@dataclass(frozen=True)
class Device:
    name: str
    outputs_to: tuple[str, ...]

    @classmethod
    def parse(cls, row: str) -> Device:
        name, outputs = row.split(": ")
        return cls(name=name, outputs_to=tuple(outputs.split()))


class DevicesPile[DeviceType](dict[str, DeviceType]):
    def add_device(self, device: DeviceType, ignore_if_exists: bool = False) -> None:
        if device.name in self:
            if ignore_if_exists:
                return
            raise KeyError(f"Device '{device.name}' already exists.")
        self[device.name] = device

    @cached_property
    def start(self) -> DeviceType:
        return self["you"]

    @cached_property
    def end(self) -> DeviceType:
        return self["out"]


@dataclass(frozen=True)
class ConnectedDevice:
    name: str
    outputs_to: set[ConnectedDevice] = field(default_factory=set)
    inputs_from: set[ConnectedDevice] = field(default_factory=set)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


def load_from_file(file_name: str) -> DevicesPile[ConnectedDevice]:
    loaded_devices: DevicesPile[Device] = DevicesPile[Device]()
    with open(file_name) as f:
        for line in f:
            device = Device.parse(line)
            loaded_devices.add_device(device)
    all_device_names = set(
        device_name
        for device_name in loaded_devices
    )
    for device in loaded_devices.values():
        all_device_names |= set(device.outputs_to)
    connected_devices: DevicesPile[ConnectedDevice] = DevicesPile[ConnectedDevice]()
    for device_name in all_device_names:
        connected_devices.add_device(ConnectedDevice(device_name))
    for device in connected_devices.values():
        if device.name not in loaded_devices:
            continue
        loaded_device = loaded_devices[device.name]
        for output_device_name in loaded_device.outputs_to:
            output_device = connected_devices[output_device_name]
            device.outputs_to.add(output_device)
            output_device.inputs_from.add(device)
    return connected_devices


@cache
def count_paths(start_device: ConnectedDevice, target_device: ConnectedDevice) -> int:
    if target_device is start_device:
        return 1
    return sum(
        count_paths(start_device, previous_from_last_device)
        for previous_from_last_device in target_device.inputs_from
    )


@validate_result
def part1(file_name: str):
    devices_pile = load_from_file(file_name)
    return count_paths(devices_pile.start, devices_pile.end)


def main():
    part1("example.txt", expected_result=5)
    part1("input.txt", expected_result=607)


if __name__ == "__main__":
    main()
