import time

from pynput.mouse import Listener, Button
from typing import TYPE_CHECKING

from .schemas import Status
from .world_to_screen import Region

if TYPE_CHECKING:
    from ..bot import FisherBot


class EventsLoop:

    __slots__ = (
        '_bot_instance',
        '_new_first_custom_catching_coord',
    )

    def __init__(self, bot_instance: 'FisherBot'):
        self._bot_instance = bot_instance
        self._new_first_custom_catching_coord: tuple[int, int] = None

        def _mouse_on_click_event(x: int, y: int, button: Button, is_pressed: bool):
            if self._bot_instance.status is not Status.PAUSED:
                return

            if button is Button.middle:
                if is_pressed:
                    self._new_first_custom_catching_coord = x, y
                else:
                    self._bot_instance.set_new_catching_region(
                        Region(
                            top=self._new_first_custom_catching_coord[1],
                            left=self._new_first_custom_catching_coord[0],
                            width=x, height=y
                        )
                    )
                    self._new_first_custom_catching_coord = None

        Listener(on_click=_mouse_on_click_event).start()

    def __call__(self):
        while True:
            if self._bot_instance.status is Status.PAUSING:
                self._bot_instance.change_status(Status.PAUSED)

            elif self._bot_instance.status is Status.CATCHING:
                break

            time.sleep(0.5)
