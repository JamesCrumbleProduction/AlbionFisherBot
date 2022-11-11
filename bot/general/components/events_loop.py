import time

from pynput.mouse import Listener, Button
from typing import TYPE_CHECKING, Callable

from .world_to_screen import Region
from .schemas import Status, AdditionalEvent
from ..services.logger import COMPONENTS_LOGGER

if TYPE_CHECKING:
    from ..bot import FisherBot


class EventsLoop:

    __slots__ = (
        '_bot_instance',
        '_additional_events',
        '_new_first_catching_coord',
    )

    def __init__(self, bot_instance: 'FisherBot'):
        self._bot_instance = bot_instance
        self._additional_events: dict[str, AdditionalEvent] = dict()
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

            for event_name, event in self._additional_events.items():
                if self._bot_instance.status in event.execute_on_statuses:
                    COMPONENTS_LOGGER.info(f'STARTING ADDITIONAL "{event_name}" EVENT')
                    event.event()

            if self._bot_instance.status is Status.CATCHING:
                if mouse_listener is not None:
                    mouse_listener.stop()
                break

            elif self._bot_instance.status is Status.RELOCATE:
                self._bot_instance.relocate_to_next_location()

            time.sleep(0.5)

    def add_event(self, *, event_name: str, event: Callable, execute_on_statuses: list[Status] | None = None) -> None:
        if event_name not in self._additional_events:
            self._additional_events[event_name] = AdditionalEvent(
                name=event_name,
                event=event,
                **{'execute_on_statuses': execute_on_statuses} if execute_on_statuses is not None else {}
            )
