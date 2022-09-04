import cv2
import time
import numpy as np


from .io_controllers import CommonIOController
from .templates import FISHER_BOT_COMPILED_TEMPLATES
from .world_to_screen import TemplateScanner, HSVBobberScanner, Region


THROW_DELAY: float = 0.6
CATCHING_MOUSE_HOLD_PERCENTAGE_THRESHOLD: float = 60
BOBBER_CATCHING_THRESHOLD: int = 45  # %
assert 0 < CATCHING_MOUSE_HOLD_PERCENTAGE_THRESHOLD <= 100


# [Hmin, Smin, Vmin]
BOBBER_LOWER_HSV_ARRAY = np.array(
    [0, 157, 206],
    dtype=np.uint8, copy=False
)
# [Hmax, Smax, Vmax]
BOBBER_HIGHER_HSV_ARRAY = np.array(
    [3, 224, 255],
    dtype=np.uint8, copy=False
)


class FisherBot:

    __slots__ = (
        '_bobber_scanner',
        '_bobber_pixels_threshold',
        '_catching_bobber_scanner',
        '_catching_status_bar_scanner',
        '_catching_bar_mouse_hold_threshold',
    )

    def __init__(self) -> None:

        self._bobber_pixels_threshold: int = None
        self._bobber_scanner = HSVBobberScanner(
            BOBBER_LOWER_HSV_ARRAY, BOBBER_HIGHER_HSV_ARRAY,
            Region(width=1920, height=1080, left=0, top=0)
        )
        # self._bobber_scanner = TemplateScanner(
        #     iterable_templates=FISHER_BOT_COMPILED_TEMPLATES.bobbers.templates,
        #     threshold=0.95, region=Region(width=1920, height=1080, left=0, top=0)
        # )

        # initing when first fish was catching
        self._catching_bar_mouse_hold_threshold: float = None
        self._catching_bobber_scanner: TemplateScanner = None
        self._catching_status_bar_scanner: TemplateScanner = None

    def _init_catching_scanner(self) -> None:

        self._catching_status_bar_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.other_templates.get(
                'catching_status_bar'
            ), threshold=0.65, region=None  # region was inited in the future (when catching bar was actually founded)
        )

        while True:
            if catching_bar_coordinate := self._catching_status_bar_scanner.indentify_by_first():
                print((
                    f'FOUND CATCHING BAR COORDINATE => '
                    f'X: {catching_bar_coordinate.x} '
                    f'Y: {catching_bar_coordinate.y}\n\t'
                    f'REGION: {catching_bar_coordinate.region}'
                ))

                self._catching_status_bar_scanner.region = catching_bar_coordinate.region
                self._catching_bobber_scanner = TemplateScanner(
                    FISHER_BOT_COMPILED_TEMPLATES.bobbers.get(
                        'bobber_status_bar'
                    ), threshold=0.7, region=catching_bar_coordinate.region
                )
                # self._catching_bobber_scanner.update_source()

                # cv2.imwrite('test.png', self._catching_bobber_scanner._image_rgb)

                self._catching_bar_mouse_hold_threshold = catching_bar_coordinate.region.left + int(
                    catching_bar_coordinate.region.width / 100 *
                    CATCHING_MOUSE_HOLD_PERCENTAGE_THRESHOLD
                )
                return

    def _need_to_catch(self, after_throw_value: int) -> bool:
        bobber_pixels: int = self._bobber_scanner.get_pixels_of_bobber_mask()

        value = after_throw_value / 100 * BOBBER_CATCHING_THRESHOLD

        print(bobber_pixels, value)

        condition = bobber_pixels < value

        return condition

        # values = [self._bobber_scanner.iterate_all_by_first_founded()]
        # need_to_catch = values.count(None) == len(values)

        # print(f'need to catch -> {need_to_catch}')

        # return need_to_catch

    def _catch_when_fish_awaiting(self) -> None:
        CommonIOController.press_mouse_button_and_release(THROW_DELAY)
        time.sleep(1.5)

        after_throw_value = self._bobber_scanner.get_pixels_of_bobber_mask()

        while True:
            condition = self._need_to_catch(after_throw_value)
            print(f'CONDITION OF BOBBER => {condition}')
            if condition:
                CommonIOController.mouse_left_click()
                break

            time.sleep(0.1)

    def _catch_fish(self) -> None:
        # CommonIOController.press_mouse_left_button()

        if self._catching_status_bar_scanner is None:
            print('INITING CATCHING SCANNER')
            self._init_catching_scanner()

        print('PREPARE FOR CATCHING FISH')

        while True:
            if bobber_coord := self._catching_bobber_scanner.indentify_by_first():
                break

            time.sleep(0.1)

        while True:
            bobber_coord = self._catching_bobber_scanner.indentify_by_first()

            print(CommonIOController.mouse_left_button_is_pressed)

            if bobber_coord:

                print((
                    f'FOUND BOBBER ON CATCHING BAR => '
                    f'X: {bobber_coord.x} '
                    f'Y: {bobber_coord.y}\n\t'
                    f'REGION: {bobber_coord.region}'
                ))

                print(bobber_coord.x - bobber_coord.region.width,
                      self._catching_bar_mouse_hold_threshold)

                if bobber_coord.x - bobber_coord.region.width <= self._catching_bar_mouse_hold_threshold:
                    CommonIOController.press_mouse_left_button()
                else:
                    CommonIOController.release_mouse_left_button()
            else:
                CommonIOController.release_mouse_left_button()
                break

            time.sleep(0.1)

    def run(self) -> None:
        time.sleep(2)

        while True:
            self._catch_when_fish_awaiting()
            self._catch_fish()
            print(CommonIOController.mouse_left_button_is_pressed)
            print('awaiting for new fishing...')
            time.sleep(2)

        # while True:
        #     pixels = self._bobber_scanner.get_pixels_of_bobber_mask()
        #     print(pixels)

        #     time.sleep(0.05)
