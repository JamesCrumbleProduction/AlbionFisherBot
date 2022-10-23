import time
import random

from .settings import settings
from .services.logger import FISHER_BOT_LOGGER
from .components.io_controllers import CommonIOController
from .components.templates import FISHER_BOT_COMPILED_TEMPLATES
from .components.settings import settings as componenets_settings
from .components.world_to_screen import TemplateScanner, HSVBobberScanner, Region, Coordinate


class FisherBot:

    __slots__ = (
        '_bobber_scanner',
        '_hsv_bobber_scanner',
        '_bobber_pixels_threshold',
        '_catching_bobber_scanner',
        '_is_fish_checking_threshold',
        '_fish_catching_distance_scanner',
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

        self._catching_bar_mouse_hold_threshold = int(
            componenets_settings.REGIONS.CATCHING_BAR.left +
            componenets_settings.REGIONS.CATCHING_BAR.width * 0.75
        )
        self._is_fish_checking_threshold = int(
            componenets_settings.REGIONS.CATCHING_BAR.left +
            componenets_settings.REGIONS.CATCHING_BAR.width * 0.6
        )
        self._fish_catching_distance_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'fish_catched_distance'
            ), threshold=0.6, region=componenets_settings.REGIONS.CATCHING_BAR
        )
        self._catching_bobber_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'bobber_status_bar'
            ), threshold=0.6, region=componenets_settings.REGIONS.CATCHING_BAR
        )

    def _calc_bobber_offset(self, bobber_region: Region) -> int:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).count_nonzero_mask()
        bobber_offset = int(
            bobber_pixels / 100 * (100 - settings.BOBBER_CATCH_THRESHOLD)
        )
        print(bobber_pixels, bobber_offset)
        return bobber_offset

    def _need_to_catch(self, bobber_region: Region, bobber_offset: int) -> bool:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).count_nonzero_mask()
        print(bobber_pixels, bobber_offset)
        return bobber_pixels < bobber_offset

    def _find_bobber_region(self) -> Region:
        while True:
            for coordinate in self._bobber_scanner.iterate_all_by_first_founded():
                if coordinate:
                    return coordinate.region

    def _catch_when_fish_awaiting(self) -> None:
        CommonIOController.press_mouse_button_and_release(
            settings.THROW_DELAYS[random.randint(
                0, len(settings.THROW_DELAYS) - 1
            )]
        )
        time.sleep(2)

        bobber_region = self._find_bobber_region()
        bobber_offset = self._calc_bobber_offset(bobber_region)

        while True:
            condition = self._need_to_catch(bobber_region, bobber_offset)
            print(f'CONDITION OF BOBBER => {condition}')
            if condition:
                CommonIOController.mouse_left_click()
                break

            time.sleep(0.1)

    def _select_new_mouse_position_for_fishing(
        self, static_mouse_pos: Coordinate
    ) -> None:
        x_new = static_mouse_pos.x + random.randint(
            -settings.CATCHING_AREA_RANGE[0], settings.CATCHING_AREA_RANGE[0]
        )
        y_new = static_mouse_pos.y + random.randint(
            -settings.CATCHING_AREA_RANGE[1], settings.CATCHING_AREA_RANGE[1]
        )
        new_pos = Coordinate(x=x_new, y=y_new)
        CommonIOController.move(new_pos)

    def _check_if_actually_fish_catching(self) -> bool:
        print('WAIT LOWER REGION')
        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                print(
                    coord.x - coord.region.width // 2,
                    self._is_fish_checking_threshold
                )
                if coord.x - coord.region.width // 2 <= self._is_fish_checking_threshold:
                    CommonIOController.press_mouse_left_button()
                    break

            time.sleep(0.1)

        print('START')

        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                print(
                    coord.x - coord.region.width // 2,
                    self._catching_bar_mouse_hold_threshold
                )
                if coord.x - coord.region.width // 2 >= self._catching_bar_mouse_hold_threshold:
                    CommonIOController.release_mouse_left_button()
                    break

            time.sleep(0.1)
        time.sleep(0.1)

        print('START checking if actually fish')

        last_coord = self._fish_catching_distance_scanner.indentify_by_first()

        if last_coord is None:
            print('last_coord IS NONE')
            raise ValueError()

        for _ in range(10):
            if coord := self._fish_catching_distance_scanner.indentify_by_first():
                print(coord.x - coord.region.width // 2,
                      last_coord.x - last_coord.region.width // 2)
                if coord.x - coord.region.width // 2 != last_coord.x - last_coord.region.width // 2:
                    return True

        return False

    def _catch_fish(self) -> None:

        print('CATCHING FISH')

        while True:
            if bobber_coord := self._catching_bobber_scanner.indentify_by_first():
                if self._check_if_actually_fish_catching():
                    break
                CommonIOController.press_mouse_right_button()
                CommonIOController.release_mouse_right_button()
                return

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

                print(bobber_coord.x - bobber_coord.region.width // 2,
                      self._catching_bar_mouse_hold_threshold)

                if bobber_coord.x - bobber_coord.region.width // 2 <= self._catching_bar_mouse_hold_threshold:
                    CommonIOController.press_mouse_left_button()
                else:
                    CommonIOController.release_mouse_left_button()
            else:
                CommonIOController.release_mouse_left_button()
                break

            time.sleep(0.1)

    def run(self) -> None:
        time.sleep(2)

        static_mouse_pos = CommonIOController.mouse_position()

        while True:
            self._catch_when_fish_awaiting()
            self._catch_fish()
            print('awaiting for new fishing...')
            self._select_new_mouse_position_for_fishing(static_mouse_pos)
            time.sleep(2)
