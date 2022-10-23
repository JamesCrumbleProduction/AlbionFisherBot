import time
import random

from .settings import settings
from .services.logger import FISHER_BOT_LOGGER
from .components.io_controllers import CommonIOController
from .components.templates import FISHER_BOT_COMPILED_TEMPLATES
from .components.settings import settings as componenets_settings
from .components.buffs_controller import Buff, BuffConfig, BuffsController
from .components.world_to_screen import TemplateScanner, HSVBobberScanner, Region, Coordinate


class FisherBot:

    __slots__ = (
        '_bobber_scanner',
        '_buffs_controller',
        '_hsv_bobber_scanner',
        '_catching_bobber_scanner',
        '_is_fish_checking_threshold',
        '_fish_catching_distance_scanner',
        '_catching_bar_mouse_hold_threshold',
    )

    def __init__(self) -> None:

        self._init_bobber_scanners()
        self._init_catching_scanners()
        self._init_buffs_controller()

    def _init_bobber_scanners(self) -> None:
        self._hsv_bobber_scanner = HSVBobberScanner(
            componenets_settings.HSV_CONFIGS.Bobber.LOWER_HSV_ARRAY,
            componenets_settings.HSV_CONFIGS.Bobber.HIGHER_HSV_ARRAY
        )
        self._bobber_scanner = TemplateScanner(
            iterable_templates=FISHER_BOT_COMPILED_TEMPLATES.bobbers.templates,
            threshold=0.6
        )

    def _init_catching_scanners(self) -> None:
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
            ), threshold=0.8, region=componenets_settings.REGIONS.CATCHING_BAR
        )
        self._catching_bobber_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'bobber_status_bar'
            ), threshold=0.8, region=componenets_settings.REGIONS.CATCHING_BAR
        )

    def _init_buffs_controller(self) -> None:
        bait_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('bait')
        eat_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('eat')

        self._buffs_controller = BuffsController(
            Buff(
                buff_config=BuffConfig(
                    name=bait_buff.name,
                    activation_key='o'
                ),
                is_active_scanner=TemplateScanner(
                    iterable_templates=bait_buff.is_active,
                    threshold=0.8, region=componenets_settings.REGIONS.ACTIVE_BUFFS
                ),
                empty_slot_scanner=TemplateScanner(
                    bait_buff.empty_slot,
                    threshold=0.8, region=componenets_settings.REGIONS.BUFFS_UTILITY_BAR
                ),
                in_inventory_item_scanner=TemplateScanner(
                    bait_buff.item,
                    threshold=0.7, region=componenets_settings.REGIONS.INVENTORY
                )
            ),
            # TODO: update templates for this buff
            # Buff(
            #     buff_config=BuffConfig(
            #         name=eat_buff.name,
            #         activation_key='p'
            #     ),
            #     is_active_scanner=TemplateScanner(
            #         iterable_templates=eat_buff.is_active,
            #         threshold=0.8, region=componenets_settings.REGIONS.ACTIVE_BUFFS
            #     ),
            #     empty_slot_scanner=TemplateScanner(
            #         eat_buff.empty_slot,
            #         threshold=0.8, region=componenets_settings.REGIONS.BUFFS_UTILITY_BAR
            #     ),
            #     in_inventory_item_scanner=TemplateScanner(
            #         eat_buff.item,
            #         threshold=0.7, region=componenets_settings.REGIONS.INVENTORY
            #     )
            # )
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
                    self._is_fish_checking_threshold
                )
                if coord.x - coord.region.width // 2 >= self._is_fish_checking_threshold:
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

            time.sleep(0.05)

        return False

    def _catch_fish(self) -> None:

        print('CATCHING FISH')

        for _ in range(10):
            if bobber_coord := self._catching_bobber_scanner.indentify_by_first():
                if self._check_if_actually_fish_catching():
                    break
                CommonIOController.press_mouse_right_button()
                CommonIOController.release_mouse_right_button()
                return

            time.sleep(0.1)
        else:
            print('SOMETHING WENT WRONG')
            return

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
            self._buffs_controller.check_and_activate_buffs()
            self._select_new_mouse_position_for_fishing(static_mouse_pos)
            self._catch_when_fish_awaiting()
            self._catch_fish()
            print('awaiting for new fishing...')
            time.sleep(2)
