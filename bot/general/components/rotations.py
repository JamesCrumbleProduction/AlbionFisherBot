from __future__ import annotations

import os
import time
import orjson

from typing import Iterator

from .schemas import Location
from .io_controllers import CommonIOController
from .world_to_screen import Region, Coordinate
from ..services.logger import COMPONENTS_LOGGER
from .paths import ROTATIONS_FILE_PATH, LAST_LOCATION_FILE_PATH


class RotationsError(BaseException):
    ...


class RotationsStructure:

    _instance: RotationsStructure | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._locations_keys = None  # type: ignore
            cls._instance._init_locations()

        return cls._instance

    def __init__(self):
        self._locations_keys: list[str]
        self._locations: dict[str, Location]

    def _is_rotations_file_exists(self) -> bool:
        return os.path.exists(ROTATIONS_FILE_PATH) and os.path.isfile(ROTATIONS_FILE_PATH)

    def _serialize_rotations(self) -> Iterator[Location]:

        with open(ROTATIONS_FILE_PATH, 'rb') as handle:
            raw_locations_data: dict[str, dict] = orjson.loads(handle.read())

            for raw_location in raw_locations_data.values():
                raw_catching_region: list[tuple[int, int]] = raw_location['catching_region']

                yield Location(
                    key=raw_location['key'],
                    record=raw_location['record'],
                    catching_region=Region(
                        top=raw_catching_region[0][0],
                        left=raw_catching_region[0][1],
                        width=raw_catching_region[1][0],
                        height=raw_catching_region[1][1]
                    )
                )

    def _init_locations(self) -> None:
        if self._is_rotations_file_exists():
            self._locations = {
                location.key: location
                for location in self._serialize_rotations()
            }
        else:
            self._locations = dict()

    def get(self, location_key: str) -> Location:
        try:
            return self._locations[location_key]
        except KeyError:
            raise RotationsError(f'LOCATION WITH "{location_key}" KEY CANNOT BE FOUND')

    @property
    def locations(self) -> list[str]:
        if self._locations_keys is None:
            self._locations_keys = [location for location in self._locations]

        return self._locations_keys


class Rotations:

    __slots__ = (
        '_structure',
        '_current_location',
    )

    def __init__(self):
        self._structure = RotationsStructure()
        self._current_location: str = self._define_current_location()

    @property
    def current_location(self) -> str:
        return self._current_location

    @current_location.setter
    def current_location(self, value: str) -> None:
        self._current_location = value

    def _is_last_location_exists(self) -> bool:
        return os.path.exists(LAST_LOCATION_FILE_PATH) and os.path.isfile(LAST_LOCATION_FILE_PATH)

    def _define_current_location(self) -> str:
        if self._is_last_location_exists():
            with open(LAST_LOCATION_FILE_PATH, 'rb') as handle:
                last_location: str = orjson.loads(handle.read())['last_location']

                if len(self._structure.locations) == 0:
                    os.remove(LAST_LOCATION_FILE_PATH)
                    COMPONENTS_LOGGER.warning(
                        'FOUND FILE WITH LAST LOCATION DATA BUT LOCATIONS OF RELOCATIONS STRUCTURE IS EMPTY !!!'
                    )
                    return ''

                if last_location not in self._structure.locations:
                    COMPONENTS_LOGGER.warning(
                        'LOOKS LIKE LAST LOCATION FILE IS OUT OF DATE. NEW LOCATION SETTED TO START LOCATION OF RELOCATIONS'
                    )
                    return self._structure.locations[0]

                COMPONENTS_LOGGER.info(f'LOCATION TAKEN FROM LAST LOCATION FILE AND EQUAL TO "{last_location}"')

                return last_location

        if len(self._structure.locations) != 0:
            COMPONENTS_LOGGER.info(
                'LOOKS LIKE RELOCATIONS INITED IN FIRST TIME. NEW LOCATION SETTED TO START LOCATION OF RELOCATIONS'
            )
            return self._structure.locations[0]

        COMPONENTS_LOGGER.info('LOOKS LIKE RELOCATIONS DOESN\'T RECORDED')
        return ''

    def define_new_location_for_relocating(self) -> str:
        for i, location_key in enumerate(self._structure.locations, start=1):
            if location_key == self._current_location:
                if i == len(self._structure.locations):
                    return self._structure.locations[0]

                return self._structure.locations[i]

        raise RotationsError('CANNOT DEFINE NEW LOCATION FOR RELOCATING. CURRENT LOCATION SHOULD CONTAINS IN STRUCTURE')

    def get_location_data(self, location_key: str) -> Location:
        return self._structure.get(location_key)

    def resolve_path(self, location: Location) -> None:
        prev_time: float = 0

        for i, moving in enumerate(location.record):
            x, y, next_time = moving
            if i == 0:
                prev_time = next_time
                CommonIOController.move(Coordinate(x=x, y=y))
                CommonIOController.press_mouse_left_button()
            else:
                CommonIOController.constant_move((x, y))

            time.sleep(next_time - prev_time)
            prev_time = next_time

        CommonIOController.release_mouse_left_button()
