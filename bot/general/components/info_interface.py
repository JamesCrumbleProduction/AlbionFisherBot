import io
import mss as mss

from mss.tools import to_png
from datetime import datetime, timedelta

from .schemas import Status, LastSnapshot
from .world_to_screen import monitor_region


class InfoInterface:

    __slots__ = (
        '_status',
        '_catched_fishes',
        '_catching_errors',
        '_skipped_non_fishes',
        '_skipped_in_row',
        '_snapshot_in_progress',
        '_last_snapshot',
        '_last_snapshot_datetime',
        '_session_start_datetime',
    )

    def __init__(self) -> None:
        self._status: Status = Status.PAUSED
        self._catched_fishes: int = 0
        self._catching_errors: int = 0
        self._skipped_non_fishes: int = 0
        self._skipped_in_row: int = 0

        self._snapshot_in_progress: bool = False
        self._last_snapshot: io.BytesIO | None = None
        self._last_snapshot_datetime: datetime | None = None
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
    def skipped_in_row(self) -> int:
        return self._skipped_in_row

    @property
    def session_start_datetime(self) -> datetime:
        return self._session_start_datetime

    @property
    def status(self) -> Status:
        return self._status

    def _save_last_snapshot(self) -> None:
        if (
            self._last_snapshot_datetime is None
            or datetime.now() >= self._last_snapshot_datetime - timedelta(seconds=10.0)
        ):
            self._snapshot_in_progress = True
            with mss.mss() as base:
                snapshot = base.grab(monitor_region().dict())
                self._last_snapshot = io.BytesIO(to_png(snapshot.rgb, snapshot.size))  # type: ignore
            self._snapshot_in_progress = False
            self._last_snapshot_datetime = datetime.now()

    def get_last_snapshot(self) -> LastSnapshot | None:
        if self._last_snapshot is not None and not self._snapshot_in_progress:
            self._last_snapshot.seek(0)
            return LastSnapshot(self._last_snapshot, 'last_snapshot.png')
