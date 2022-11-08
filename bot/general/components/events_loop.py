import time

from typing import TYPE_CHECKING
from pynput.mouse import Listener, Button

from .schemas import Status
from .world_to_screen import Region

if TYPE_CHECKING:
    from ..bot import FisherBot


class EventsLoop:

    __slots__ = (
        '_bot_instance',
        '_new_first_catching_coord',
    )

    def __init__(self, bot_instance: 'FisherBot'):
        self._bot_instance = bot_instance
        self._new_first_catching_coord: tuple[int, int] | None = None

    def _new_catching_region_definer(self, x: int, y: int, button: Button, is_pressed: bool) -> None:
        if button is Button.middle:
            if is_pressed:
                self._new_first_catching_coord = x, y
            else:
                left_top_coord = min([self._new_first_catching_coord, (x, y)], key=lambda v: v[0])  # type: ignore
                right_bottom_coord = max([self._new_first_catching_coord, (x, y)], key=lambda v: v[0])  # type: ignore
                self._bot_instance.set_new_catching_region(
                    Region(
                        top=left_top_coord[1], left=left_top_coord[0],  # type: ignore
                        width=right_bottom_coord[0], height=right_bottom_coord[1]  # type: ignore
                    )
                )
                self._new_first_catching_coord = None

    def __call__(self):
        mouse_listener: Listener | None = None

        while True:
            if self._bot_instance.status is Status.PAUSING:
                self._bot_instance.change_status(Status.PAUSED)

            if self._bot_instance.status is Status.PAUSED and mouse_listener is None:
                mouse_listener = Listener(on_click=self._new_catching_region_definer)
                mouse_listener.start()

            elif self._bot_instance.status is Status.CATCHING:
                if mouse_listener is not None:
                    mouse_listener.stop()
                break

            elif self._bot_instance.status is Status.RELOCATE:
                self._bot_instance.relocate_to_next_location()

            time.sleep(0.5)
