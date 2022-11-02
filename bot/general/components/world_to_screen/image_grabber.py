import numpy as np

from mss import mss
from numpy import ndarray
from screeninfo import get_monitors

from .schemas import Region, Coordinate, ScreenPart
from .exceptions import MonitorDefiningError, WrongScreenResolution

BOBBER_CORNER_EXPAND_PERCENTAGE: int = 5


def _define_monitor_region() -> Region:
    for monitor in get_monitors():
        if monitor.is_primary or (monitor.x == 0 and monitor.y == 0):
            if monitor.width == 1024 and monitor.height == 768:
                return Region(left=0, top=0, width=monitor.width, height=monitor.height)

            raise WrongScreenResolution('Support only 1024x768 screen resolution')  # noqa

    raise MonitorDefiningError('Cannot define default monitor region...')


def monitor_center() -> Coordinate:
    monitor_region = _define_monitor_region()
    return Coordinate(
        x=monitor_region.width // 2,
        y=monitor_region.height // 2
    )


def get_screen_part_region(screen_part: ScreenPart) -> Region:
    monitor_center_ = monitor_center()
    monitor_region_ = _define_monitor_region()

    match screen_part:
        case ScreenPart.TOP_LEFT:
            return Region(
                top=0,
                left=0,
                width=int(monitor_center_.x + monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                height=int(monitor_center_.y + monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100))  # noqa
            )
        case ScreenPart.TOP_RIGHT:
            return Region(
                top=0,
                left=int(monitor_center_.x - monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                width=int(monitor_center_.x + monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                height=int(monitor_center_.y + monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100))  # noqa
            )
        case ScreenPart.BOTTOM_LEFT:
            return Region(
                top=int(monitor_center_.y - monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                left=0,
                width=int(monitor_center_.x + monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                height=int(monitor_center_.y + monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100))  # noqa
            )
        case ScreenPart.BOTTOM_RIGHT:
            return Region(
                top=int(monitor_center_.y - monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                left=int(monitor_center_.x - monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                width=int(monitor_center_.x + monitor_region_.width * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100)),  # noqa
                height=int(monitor_center_.y + monitor_region_.height * (BOBBER_CORNER_EXPAND_PERCENTAGE / 100))  # noqa
            )

    raise ValueError(
        f'Unknown value of "screen_part" variable => {screen_part}')


def validate_region(region: Region | None = None) -> Region:
    if region is None:
        return _define_monitor_region()

    elif type(region) is Region:
        return region

    raise NotImplementedError('Region should have type of Region class')


def grab_screen(region: Region) -> ndarray:
    with mss() as base:
        return np.array(base.grab(region.dict()), dtype=np.uint8)
