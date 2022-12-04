from concurrent.futures import Future, ThreadPoolExecutor
from pynput.mouse import Listener, Controller
from screeninfo import get_monitors
from pydantic import BaseModel
from mss import mss
import numpy as np
import time
import cv2
import os


class ValidatedTemplateData(BaseModel):
    location_x: np.ndarray
    location_y: np.ndarray
    height: int
    width: int

    class Config:
        arbitrary_types_allowed = 'allow'


def _define_monitor_region() -> dict[str, int]:
    for monitor in get_monitors():
        if monitor.is_primary or (monitor.x == 0 and monitor.y == 0):
            return dict(left=0, top=0, width=monitor.width, height=monitor.height)

    return dict()


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


def get_bobber_corner(return_: bool = False) -> dict | None:

    expand_percentage = 5
    region: dict = dict()

    monitor_res = _define_monitor_region()

    center_x, center_y = monitor_res['width'] // 2, monitor_res['height'] // 2

    while True:
        mouse_x, mouse_y = Controller().position

        if mouse_y < center_y:
            if mouse_x < center_x:
                region = dict(
                    top=0,
                    left=0,
                    width=center_x + int(monitor_res["width"] * (expand_percentage / 100)),
                    height=center_y + int(monitor_res["height"] * (expand_percentage / 100))
                )
                # print(f'''LEFT TOP CORNER{region}''')
            else:
                region = dict(
                    top=0,
                    left=center_x - int(monitor_res["width"] * (expand_percentage / 100)),
                    width=int(center_x + monitor_res["width"] * (expand_percentage / 100)),
                    height=int(center_y + monitor_res["height"] * (expand_percentage / 100))
                )
                # print(f'''RIGHT TOP CORNER{region}''')
        else:
            if mouse_x < center_x:
                region = dict(
                    top=center_y - int(monitor_res["height"] * (expand_percentage / 100)),
                    left=0,
                    width=center_x + int(monitor_res["width"] * (expand_percentage / 100)),
                    height=center_y + int(monitor_res["height"] * (expand_percentage / 100))
                )
                # print(f'''LEFT BOTTOM CORNER {region}''')
            else:
                region = dict(
                    top=center_y - int(monitor_res["height"] * (expand_percentage / 100)),
                    left=center_x - int(monitor_res["width"] * (expand_percentage / 100)),
                    width=int(center_x + monitor_res["width"] * (expand_percentage / 100)),
                    height=int(center_y + monitor_res["height"] * (expand_percentage / 100))
                )
                # print(f'''RIGHT BOTTOM CORNER{region}''')
        if return_:
            return region
        with mss() as base:
            image = np.array(base.grab(region), dtype=np.uint8)
            cv2.imwrite('test.png', image)

        time.sleep(0.2)


def check_for_bobbers_templates():

    CHECK_FROM_SCREENSHOT: bool = False

    current_path = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(
        current_path, '..', 'general', 'components', 'templates', 'raw_templates', 'fisher_bot', 'bobbers'
    )
    executor = ThreadPoolExecutor(max_workers=6)

    templates: list[np.ndarray] = [
        cv2.cvtColor(
            cv2.imread(
                template_path.path
            ), cv2.COLOR_BGR2RGB

        ) for template_path in os.scandir(templates_dir)
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
                np.array(cv2.imread(os.path.join(current_path, 'test.png')), dtype=np.uint8)
                if CHECK_FROM_SCREENSHOT else np.array(base.grab(get_bobber_corner(return_=True)), dtype=np.uint8),  # type: ignore # noqa
                cv2.COLOR_BGR2RGB
            )

        futures: list[tuple[int, Future]] = list()

        passed_templates_data: list = list()

        for i, template in enumerate(templates):
            future = executor.submit(
                validate_template,
                image, template, threshold=0.65
            )
            futures.append((i, future,))

        while futures:
            for i, future_info in enumerate(futures):
                template_index, future = future_info

                if future.done():
                    template_data = future.result()

                    print(
                        f"TEMPLATE \"{template_index}\" CONDITION => {template_data is not None}"
                    )

                    if template_data is not None:
                        passed_templates_data.append(template_data)

                    futures.pop(i)
                    break

        for template_data in passed_templates_data:
            for x, y in zip(template_data.location_x, template_data.location_y):
                image = cv2.rectangle(
                    image, (x, y),
                    (
                        x + template_data.width,
                        y + template_data.height
                    ),
                    (0, 0, 255), 1
                )
        cv2.imwrite('test.png', image)

        print('SLEEP 2 sec')
        time.sleep(2)


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


check_for_bobbers_templates()
