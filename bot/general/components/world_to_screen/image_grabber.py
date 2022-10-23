import numpy as np

from mss import mss
from numpy import ndarray
from screeninfo import get_monitors

from .schemas import Region
from .exceptions import MonitorDefiningError, WrongScreenResolution


def _define_monitor_region() -> Region:
    for monitor in get_monitors():
        if monitor.is_primary or (monitor.x == 0 and monitor.y == 0):
            # if monitor.width == 1024 and monitor.height == 768:
            return Region(left=0, top=0, width=monitor.width, height=monitor.height)

            # raise WrongScreenResolution('Support only 1024x768 screen resolution')  # noqa

    raise MonitorDefiningError('Cannot define default monitor region...')


def validate_region(region: Region = None) -> Region:
    if region is None:
        return _define_monitor_region()

    elif type(region) is Region:
        return region

    raise NotImplementedError('Region should have type of Region class')


def grab_screen(region: Region) -> ndarray:
    with mss() as base:
        return np.array(base.grab(region.dict()), dtype=np.uint8)
