import time

from .settings import settings
from .components.io_controllers import CommonIOController
from .components.templates import FISHER_BOT_COMPILED_TEMPLATES
from .components.world_to_screen import TemplateScanner, HSVBobberScanner, Region
from .components.settings import settings as componenets_settings


class FisherBot:

    __slots__ = (
        '_bobber_scanner',
        '_hsv_bobber_scanner',
        '_bobber_pixels_threshold',
        '_catching_bobber_scanner',
        '_catching_status_bar_scanner',
        '_catching_bar_mouse_hold_threshold',
    )

    def __init__(self) -> None:

        self._bobber_pixels_threshold: int = None
        self._hsv_bobber_scanner = HSVBobberScanner(
            componenets_settings.HSV_CONFIGS.Bobber.LOWER_HSV_ARRAY,
            componenets_settings.HSV_CONFIGS.Bobber.HIGHER_HSV_ARRAY
        )
        self._bobber_scanner = TemplateScanner(
            iterable_templates=FISHER_BOT_COMPILED_TEMPLATES.bobbers.templates,
            threshold=0.6
        )

        # initing when first fish was catching
        self._catching_bar_mouse_hold_threshold: float = None
        self._catching_bobber_scanner: TemplateScanner = None
        self._catching_status_bar_scanner: TemplateScanner = None

    def _init_catching_scanner(self) -> None:

        self._catching_status_bar_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'catching_status_bar'
            ), threshold=0.7, region=None  # region was inited in the future (when catching bar was actually founded)
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
                    FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                        'bobber_status_bar'
                    ), threshold=0.7, region=catching_bar_coordinate.region
                )

                self._catching_bar_mouse_hold_threshold = catching_bar_coordinate.region.left + int(
                    catching_bar_coordinate.region.width / 100 *
                    settings.MOUSE_CATCHING_BAR_THRESHOLD
                )
                return

    def _check_if_fish_catching(self) -> bool:
        ...

    def _calc_bobber_offset(self, bobber_region: Region) -> int:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).get_pixels_of_bobber_mask()
        bobber_offset = int(
            bobber_pixels / 100 * (100 - settings.BOBBER_CATCH_THRESHOLD)
        )
        print(bobber_pixels, bobber_offset)
        return bobber_offset

    def _need_to_catch(self, bobber_region: Region, bobber_offset: int) -> bool:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).get_pixels_of_bobber_mask()
        print(bobber_pixels, bobber_offset)
        return bobber_pixels < bobber_offset

    def _find_bobber_region(self) -> Region:
        while True:
            for coordinate in self._bobber_scanner.iterate_all_by_first_founded():
                if coordinate:
                    return coordinate.region

    def _catch_when_fish_awaiting(self) -> None:
        CommonIOController.press_mouse_button_and_release(
            settings.THROW_DELAY
        )
        time.sleep(2)

        bobber_region = self._find_bobber_region(extend_region=False)
        bobber_offset = self._calc_bobber_offset(bobber_region)

        while True:
            condition = self._need_to_catch(bobber_region, bobber_offset)
            print(f'CONDITION OF BOBBER => {condition}')
            if condition:
                CommonIOController.mouse_left_click()
                break

            time.sleep(0.1)

    def _catch_fish(self) -> None:

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
            print('awaiting for new fishing...')
            time.sleep(2)
