import os
import time
import orjson
import keyboard

from typing import Any
from pynput.mouse import Listener, Controller, Button


MOUSE = Controller()
ROOT_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


is_recording: bool = False

record: list[tuple] = list()
catching_point_catching_region: dict = dict()


def _mouse_on_move(x: int, y: int) -> None:
    global is_recording

    print(x, y)

    if is_recording:
        record.append((x, y, time.monotonic()))


def _mouse_on_click(x: int, y: int, button: Button, is_pressed: bool) -> None:
    global is_recording, start_time

    if button is Button.middle:
        if is_pressed:
            catching_point_catching_region['left_top'] = (x, y)
        if not is_pressed:
            catching_point_catching_region['height_width'] = (x, y)

    elif button is Button.left:
        if is_pressed:
            is_recording = True
        elif not is_pressed:
            is_recording = False

        record.append((x, y, time.monotonic()))


def record_path():
    with Listener(on_move=_mouse_on_move, on_click=_mouse_on_click):

        while True:

            if keyboard.is_pressed('\\'):
                break

            time.sleep(0.05)

    with open('path_record.json', 'wb') as handle:
        handle.write(orjson.dumps({
            'record': record,
            'catching_point_catching_region': catching_point_catching_region
        }))


def reproduce_path() -> None:
    with open(os.path.join(ROOT_PATH, 'rotations.json'), 'rb') as handle:
        locations: dict[str, dict[str, Any]] = orjson.loads(handle.read())

    locations_: list[str] = [
        location for location in list(locations.keys())[1:]
    ]
    locations_.append('A')
    attempts: int = 0

    while True:
        attempts += 1

        print(f'START ATTEMPT NUMBER {attempts}')
        for location in locations_:

            path_data = locations[location]

            record: list = path_data['record']
            catching_area = path_data['catching_region']

            time.sleep(5)

            x, y, prev_time, *_ = record[0]
            prev_time: float
            MOUSE.position = (x, y)
            MOUSE.press(Button.left)

            for moving in record[1:]:
                x, y, next_time, *is_pressed = moving
                MOUSE.position = (x, y)

                time.sleep(next_time - prev_time)

                if len(is_pressed) != 0:
                    print(moving, next_time - prev_time)
                    if is_pressed[0] == 1:
                        MOUSE.press(Button.left)
                    elif is_pressed[0] == 0:
                        MOUSE.release(Button.left)

                prev_time = next_time

            MOUSE.release(Button.left)
            print(catching_area)

        print(f'FINISH ATTEMPT NUMBER {attempts}')
        time.sleep(5.4)


# record_path()
reproduce_path()
