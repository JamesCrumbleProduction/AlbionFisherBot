from logging.config import listen
import os
import cv2
import time
import numpy as np

from mss import mss
from pydantic import BaseModel
from screeninfo import get_monitors
from pynput.mouse import Listener


class ValidatedTemplateData(BaseModel):
    location_x: np.ndarray
    location_y: np.ndarray
    height: int
    width: int

    class Config:
        arbitrary_types_allowed = 'allow'


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
        top=60,
        left=50,
        height=89,
        width=214
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


def serching_template():

    REGION: dict[str, int] = dict(
        top=60,
        left=50,
        height=89,
        width=214
    )
    ALL_TEMPLATES: bool = True

    def region() -> dict:
        for value in REGION.values():
            if value != 0:
                break
        else:
            return MONITOR

        return REGION

    current_path = os.getcwd()
    templates_dir = os.path.join(
        current_path, 'bot', 'general', 'components', 'templates', 'raw_templates', 'fisher_bot', 'buffs', 'bait', 'is_active'
    )

    if ALL_TEMPLATES:
        templates: list[np.ndarray] = [
            cv2.cvtColor(
                cv2.imread(
                    template_path.path
                ), cv2.COLOR_BGR2RGB

            ) for template_path in os.scandir(templates_dir)
        ]
    else:
        templates: list[np.ndarray] = [
            cv2.cvtColor(
                cv2.imread(
                    os.path.join(templates_dir, 'item.png')
                ), cv2.COLOR_BGR2RGB

            )
        ]

    def validate_template(img, template, threshold):
        height, width = template.shape[:-1]
        res = cv2.matchTemplate(
            img,
            template,
            cv2.TM_CCOEFF_NORMED
        )
        location_y, location_x = np.where(res >= threshold)

        if location_y.size > 0 and location_x.size > 0:
            return ValidatedTemplateData(
                location_x=location_x,
                location_y=location_y,
                height=height,
                width=width
            )

    while True:

        with mss() as base:
            image = cv2.cvtColor(
                np.array(base.grab(region()), dtype=np.uint8),
                cv2.COLOR_BGR2RGB
            )

            for i, template in enumerate(templates):

                template_data = validate_template(
                    image, template, threshold=0.7
                )
                print(
                    f'TEMPLATE NUMBER "{i}" IS FOUNDED => "{bool(template_data)}"'
                )
                if template_data is None:
                    continue

                if template_data := validate_template(
                    image, template, threshold=0.7
                ):

                    for x, y in zip(template_data.location_x, template_data.location_y):
                        image = cv2.rectangle(
                            image, (x, y),
                            (
                                x + template_data.width,
                                y + template_data.height
                            ),
                            (0, 0, 255), 1
                        )
                    break

            cv2.imwrite('test.png', image)

        time.sleep(0.2)


def mouse_scroll_listener():

    def on_click(x, y, button, condition):
        print(x, y, button, condition)

    def on_scroll(x, y, dx, dy):
        print(x, y, dx, dy)
        print(f"Scrolled {'down' if dy < 0 else 'up'} by {(x, y)}")

    listener = Listener(on_scroll=on_scroll, on_click=on_click)
    listener.start()
    for _ in range(50):
        time.sleep(0.25)
    listener.stop()

    # with  as listener:
    #     listener.join()
    # listener.stop()
    # print('fewfewfwef')


mouse_scroll_listener()
