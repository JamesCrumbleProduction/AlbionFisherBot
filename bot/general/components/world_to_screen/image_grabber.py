import numpy as np

from mss import mss
from numpy import ndarray
from screeninfo import get_monitors

from .structure import Region
from .exceptions import MonitorDefiningError


def _define_monitor_region() -> Region:
    for monitor in get_monitors():
        if monitor.is_primary or (monitor.x == 0 and monitor.y == 0):
            return Region(left=0, top=0, width=monitor.width, height=monitor.height)

    raise MonitorDefiningError('Cannot define default monitor region...')


DEFAULT_MONITOR_REGION = _define_monitor_region()


def validate_region(region: Region | None) -> Region:
    if region is None:
        return DEFAULT_MONITOR_REGION

    elif type(region) is Region:
        return region

    raise NotImplementedError(
        'Region should have type of Region class'
    )


def grab_screen(region: Region) -> ndarray:
    with mss() as base:
        return np.array(base.grab(region.dict()), dtype=np.uint8)
