import os
import time
import orjson
import string
import keyboard

from mss import mss, tools
from pydantic import BaseModel
from pynput.mouse import Listener, Button


'''
MAY BE FOR FUTURE

rotations file extension structure

delimeter is char 1
block delimeter is char 2
section delimeter is char 3

HEADER
path literal (char 1) path data start index (char 2) ... <- all existed paths in reachable order

char 3

path literal (char 2) catching mouse area (char 2) record elements ([int, int, float] char 1 ...) (char 3) ...

'''

ROOT_PATH: str = os.path.dirname(os.path.abspath(__file__))

LOCATION_KEYS: str = string.ascii_uppercase

STOP_RECORDING_BUTTON: str = '\\'
SWITCH_RECORD_TO_CLOSING_CYCLE_BUTTON: str = ']'

HELP: str = f'''HELP INFO:
    FOR STOP RECORDING PATH TO LOCATION TYPE "{STOP_RECORDING_BUTTON}" BUTTON
    FOR CHANGE RECORD TO CLOSING CYCLE LOCATION TYPE "{SWITCH_RECORD_TO_CLOSING_CYCLE_BUTTON}" BUTTON
'''


class Location(BaseModel):

    key: str

    # record how to reach this location
    # x, y, time interval
    record: list[tuple[int, int, float]] = None  # type: ignore

    # catching area of this location
    catching_region: list[tuple[int, int]]  # x, y

    def init_record(self, record: list[tuple[int, int, float]]) -> None:
        if self.record is None:
            self.record = record


class RotationsRecorder:

    def __init__(self):
        self._start_location_was_inited: bool = False
        self._cycle_was_closed: bool = False
        self._locations: list[Location] = list()
        self._is_recording: bool = False
        self._record_buffer: list[tuple[int, int, float]] = list()
        self._catching_region_buffer: list[tuple[int, int]] = list()

    @property
    def start_location_was_inited(self) -> bool:
        return self._start_location_was_inited

    @property
    def cycle_was_closed(self) -> bool:
        return self._cycle_was_closed

    def _clear_buffers(self) -> None:
        self._record_buffer.clear()
        self._catching_region_buffer.clear()

    def _mouse_on_move(self, x: int, y: int) -> None:
        if self._is_recording:
            if time.time() - self._record_buffer[-1][2] > 0.02:
                self._record_buffer.append((x, y, time.time()))

    def _mouse_on_click(self, x: int, y: int, button: Button, is_pressed: bool) -> None:
        if button is Button.middle:
            if is_pressed:
                if len(self._catching_region_buffer) < 1:
                    self._catching_region_buffer.append((x, y))
                else:
                    self._catching_region_buffer[0] = (x, y)
            if not is_pressed:
                if len(self._catching_region_buffer) < 2:
                    self._catching_region_buffer.append((x, y))
                else:
                    self._catching_region_buffer[1] = (x, y)

                print(f'SELECTED CATCHING REGION IS {self._catching_region_buffer}')

        elif button is Button.left:
            self._is_recording = is_pressed
            self._record_buffer.append((x, y, time.time()))

    def record_start_location_data(self) -> None:
        if len(self._locations) != 0:
            print('LOOKS LIKE START LOCATION ALREADY RECORDED')
            return

        print('ALL U NEED TO DO IS DEFINE CATCHING AREA. USE MIDDLE MOUSE BUTTON TO DEFINE IT')

        with Listener(on_click=self._mouse_on_click):
            while True:

                if keyboard.is_pressed(STOP_RECORDING_BUTTON):
                    break

                time.sleep(0.05)

            if len(self._catching_region_buffer) == 2:
                left_top_coord = min(self._catching_region_buffer, key=lambda v: v[0])  # type: ignore
                right_bottom_coord = max(self._catching_region_buffer, key=lambda v: v[0])  # type: ignore

                self._locations.append(Location(
                    key='A',
                    catching_region=[
                        (left_top_coord[1], left_top_coord[0]),
                        (right_bottom_coord[0], right_bottom_coord[1])
                    ]
                ))
                self._start_location_was_inited = True
                self.save_location_snapshot('A')
            else:
                print(
                    'SOMETHING WENT WRONG WITH CATCHING REGION RECORDING FOR START LOCATION\n\t'
                    f'CATCHING REGION LENGTH "{len(self._catching_region_buffer)}"'
                )

            self._clear_buffers()

    def record_new_path(self) -> None:
        if not self._start_location_was_inited:
            print('CANNOT START RECORDING PATH COUSE YOU NEED TO RECORD START LOCATION')
            return
        if self._cycle_was_closed:
            print('CANNOT START RECORDING PATH COUSE CYCLE IS ALREADY CLOSED')
            return

        to_location_key: str = LOCATION_KEYS[len(self._locations)]
        print(f'START RECORDING PATH TO "{to_location_key}" LOCATION')

        with Listener(on_move=self._mouse_on_move, on_click=self._mouse_on_click):

            while True:

                if keyboard.is_pressed(STOP_RECORDING_BUTTON):
                    if len(self._record_buffer) != 0 and (len(self._catching_region_buffer) == 2 or to_location_key == 'A'):
                        print(f'SAVING RECORD TO "{to_location_key}" LOCATION')
                        break

                    if len(self._record_buffer) == 0:
                        print('LOOKS LIKE RECORD BUFFER IS EMPTY. RECORD PATH THEN SAVE IT')

                    if len(self._catching_region_buffer) != 2:
                        print('TO SAVE LOCATION RECORD YOU NEED TO SETUP CATCHING REGION FOR THIS LOCATION')

                if keyboard.is_pressed(SWITCH_RECORD_TO_CLOSING_CYCLE_BUTTON):
                    print('RECORDING PATH TO START LOCATION (CYCLE WILL CLOSED)')
                    to_location_key = 'A'

                time.sleep(0.05)

        if to_location_key == 'A' and len(self._record_buffer) != 0:
            self._locations[0].init_record(self._record_buffer.copy())
            self._cycle_was_closed = True
            print(f'RECORD FOR "{to_location_key}" LOCATION WAS SAVED (CYCLE WAS CLOSED)')
        elif len(self._record_buffer) != 0 and len(self._catching_region_buffer) == 2 and to_location_key != 'A':

            left_top_coord = min(self._catching_region_buffer, key=lambda v: v[0])  # type: ignore
            right_bottom_coord = max(self._catching_region_buffer, key=lambda v: v[0])  # type: ignore

            self._locations.append(Location(
                key=to_location_key,
                record=self._record_buffer.copy(),
                catching_region=[
                    (left_top_coord[1], left_top_coord[0]),
                    (right_bottom_coord[0], right_bottom_coord[1])
                ]
            ))
            self.save_location_snapshot(to_location_key)
            print(f'RECORD FOR "{to_location_key}" LOCATION WAS SAVED')
        else:
            print(
                f'SOMETHING WENT WRONG WITH RECORDING TO "{to_location_key}" LOCATION\n\t'
                f'RECORD BUFFER LENGTH "{len(self._record_buffer)}", '
                f'CATCHING REGION BUFFER LENGTH "{len(self._catching_region_buffer)}"'
            )

        self._clear_buffers()

    def save_location_snapshot(self, location_key: str) -> None:
        if not os.path.exists(os.path.join(ROOT_PATH, 'locations_snapshots')):
            os.mkdir(os.path.join(ROOT_PATH, 'locations_snapshots'))

        with mss() as base:
            with open(os.path.join(ROOT_PATH, 'locations_snapshots', f'snapshot of {location_key} location.png'), 'wb') as handle:
                screenshot = base.grab((0, 0, 1024, 768))
                handle.write(tools.to_png(screenshot.rgb, screenshot.size))  # type: ignore

    def save(self) -> bool:
        if not self._cycle_was_closed:
            print(
                f'CANNOT SAVE LOCATIONS CYCLE COUSE YOU NEED TO RECORD PATH FROM "{self._locations[-1].key}"'
                ' LOCATION TO START OF CYCLE ("A" LOCATION)'
            )
            return False

        with open(os.path.join(ROOT_PATH, 'rotations.json'), 'wb') as handle:  # this filename using in bot so don't change it
            handle.write(orjson.dumps({
                location.key: location.dict()
                for location in self._locations
            }))

        return True


def main() -> int:

    sleep_seconds: int = 1
    recorder = RotationsRecorder()
    print(HELP)

    while not recorder.cycle_was_closed:
        if recorder.start_location_was_inited:
            recorder.record_new_path()
        else:
            recorder.record_start_location_data()

        print(f'SLEEP "{sleep_seconds}" SECONDS')
        time.sleep(sleep_seconds)

    recorder.save()

    return 0


if __name__ == '__main__':
    exit(main())
