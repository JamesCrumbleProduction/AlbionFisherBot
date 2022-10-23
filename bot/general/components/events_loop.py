import time

from typing import TYPE_CHECKING

from .schemas import Status

if TYPE_CHECKING:
    from ..bot import FisherBot


class EventsLoop:

    def __call__(self, bot_instance: 'FisherBot'):
        while True:
            if bot_instance.status is Status.PAUSING:
                bot_instance.change_status(Status.PAUSED)

            elif bot_instance.status is Status.CATCHING:
                break

            time.sleep(0.5)
