import cv2
import time
import numpy as np

from mss import mss
from screeninfo import get_monitors


def _define_monitor_region() -> dict:
    for monitor in get_monitors():
        if monitor.is_primary or (monitor.x == 0 and monitor.y == 0):
            return dict(left=0, top=0, width=monitor.width, height=monitor.height)


MONITOR = _define_monitor_region()
print(f'MONITOR => {MONITOR}')


def hsv():
    LOWER_HSV_ARRAY = np.array(
        [0, 157, 206],
        dtype=np.uint8, copy=False
    )
    # [Hmax, Smax, Vmax]
    HIGHER_HSV_ARRAY = np.array(
        [3, 224, 255],
        dtype=np.uint8, copy=False
    )

    with mss() as base:
        image = np.array(base.grab(MONITOR), dtype=np.uint8)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv_mask = cv2.inRange(
            hsv,
            LOWER_HSV_ARRAY,
            HIGHER_HSV_ARRAY
        )

        cv2.imwrite('test.png', cv2.bitwise_and(image, image, mask=hsv_mask))


def regions():

    REGION: dict[str, int] = dict(
        top=0,
        left=0,
        width=0,
        height=0
    )

    def region() -> dict:
        for value in REGION.values():
            if value != 0:
                break
        else:
            return MONITOR

        return REGION

    while True:
        with mss() as base:
            image = np.array(base.grab(region()), dtype=np.uint8)
            cv2.imwrite('test.png', image)

        time.sleep(0.2)


regions()
