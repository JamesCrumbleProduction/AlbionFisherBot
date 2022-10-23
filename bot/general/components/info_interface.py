from .schemas import Status
from datetime import datetime


class InfoInterface:

    __slots__ = (
        '_status',
        '_catched_fishes',
        '_catching_errors',
        '_skipped_non_fishes',
        '_session_start_datetime',
    )

    def __init__(self) -> None:
        self._status: Status = Status.PAUSED
        self._catched_fishes: int = 0
        self._catching_errors: int = 0
        self._skipped_non_fishes: int = 0
        self._session_start_datetime: datetime = datetime.now()

    @property
    def catched_fishes(self) -> int:
        return self._catched_fishes

    @property
    def catching_errors(self) -> int:
        return self._catching_errors

    @property
    def skipped_non_fishes(self) -> int:
        return self._skipped_non_fishes

    @property
    def session_start_datetime(self) -> datetime:
        return self._session_start_datetime

    @property
    def status(self) -> Status:
        return self._status

    def change_status(self, status: Status) -> None:
        if self._status is not Status.PAUSING and status is Status.PAUSED:
            status = Status.PAUSING

        self._status = status
