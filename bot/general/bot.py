import time
import random

from typing import Iterator

from .settings import settings
from .services.logger import FISHER_BOT_LOGGER
from .components.events_loop import EventsLoop
from .components.info_interface import InfoInterface
from .components.io_controllers import CommonIOController
from .components.templates import FISHER_BOT_COMPILED_TEMPLATES
from .components.settings import settings as componenets_settings
from .components.buffs_controller import Buff, BuffConfig, BuffInfo, BuffsController
from .components.world_to_screen import (
    Region,
    Coordinate,
    monitor_center,
    monitor_region,
    TemplateScanner,
    HSVBobberScanner,
    ThreadedTemplateScanner,
)


class FisherBot(InfoInterface):

    __slots__ = (
        'is_running',
        '_events_loop',
        '_bobber_scanner',
        '_buffs_controller',
        '_hsv_bobber_scanner',
        '_custom_catching_region',
        '_catching_bobber_scanner',
        '_fish_catching_distance_scanner',
        '_is_fish_checking_threshold_left',
        '_is_fish_checking_threshold_right',
        '_catching_bar_mouse_hold_threshold',
    )

    def __init__(self) -> None:
        super().__init__()

        self.is_running: bool = True
        self._events_loop = EventsLoop(self)

        self._custom_catching_region: Region = None

        self._init_bobber_scanners()
        self._init_catching_scanners()
        self._init_buffs_controller()

    @property
    def buffs(self) -> Iterator[BuffInfo]:
        yield from self._buffs_controller.buffs

    def set_new_catching_region(self, new_region: Region):
        self._custom_catching_region = new_region
        FISHER_BOT_LOGGER.info(
            f'NEW "{self._custom_catching_region}" CATCHING REGION WAS SETTED UP'
        )

    def _init_bobber_scanners(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING BOBBER SCANNERS')
        self._hsv_bobber_scanner = HSVBobberScanner(
            componenets_settings.HSV_CONFIGS.BOBBER_RANGES
        )
        self._bobber_scanner = ThreadedTemplateScanner(
            iterable_templates=FISHER_BOT_COMPILED_TEMPLATES.bobbers.templates,
            threshold=0.6
        )

    def _init_catching_scanners(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING CATCHING SCANNERS')
        self._catching_bar_mouse_hold_threshold = int(
            componenets_settings.REGIONS.CATCHING_BAR.left +
            componenets_settings.REGIONS.CATCHING_BAR.width * 0.7
        )
        self._is_fish_checking_threshold_left = int(
            componenets_settings.REGIONS.CATCHING_BAR.left +
            componenets_settings.REGIONS.CATCHING_BAR.width * 0.4
        )
        self._is_fish_checking_threshold_right = int(
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
        FISHER_BOT_LOGGER.debug('INITING BUFFS CONTROLLER')

        bait_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('bait')
        eat_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('eat')

        self._buffs_controller = BuffsController(
            Buff(
                buff_config=BuffConfig(
                    name=bait_buff.name,
                    activation_key='1'
                ),
                is_active_scanner=TemplateScanner(
                    iterable_templates=bait_buff.is_active,
                    threshold=0.6, region=componenets_settings.REGIONS.ACTIVE_BUFFS
                ),
                empty_slot_scanner=TemplateScanner(
                    bait_buff.empty_slot,
                    threshold=0.7, region=componenets_settings.REGIONS.BUFFS_UTILITY_BAR
                ),
                in_inventory_item_scanner=TemplateScanner(
                    bait_buff.item,
                    threshold=0.7, region=componenets_settings.REGIONS.INVENTORY
                )
            ),
            Buff(
                buff_config=BuffConfig(
                    name=eat_buff.name,
                    activation_key='2'
                ),
                is_active_scanner=TemplateScanner(
                    iterable_templates=eat_buff.is_active,
                    threshold=0.7, region=componenets_settings.REGIONS.ACTIVE_BUFFS
                ),
                empty_slot_scanner=TemplateScanner(
                    eat_buff.empty_slot,
                    threshold=0.7, region=componenets_settings.REGIONS.BUFFS_UTILITY_BAR
                ),
                in_inventory_item_scanner=TemplateScanner(
                    eat_buff.item,
                    threshold=0.7, region=componenets_settings.REGIONS.INVENTORY
                )
            )
        )

    def _get_bobber_corner(self) -> Region:

        monitor_center_ = monitor_center()
        monitor_region_ = monitor_region()
        mouse_position = CommonIOController.mouse_position()

        if mouse_position.y < monitor_center_.y:
            if mouse_position.x < monitor_center_.x:
                region = Region(
                    top=0,
                    left=0,
                    width=int(
                        monitor_center_.x + monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    height=int(
                        monitor_center_.y + monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    )
                )
            else:
                region = Region(
                    top=0,
                    left=int(
                        monitor_center_.x - monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    width=int(
                        monitor_center_.x + monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    height=int(
                        monitor_center_.y + monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    )
                )

        else:
            if mouse_position.x < monitor_center_.x:
                region = Region(
                    top=int(
                        monitor_center_.y - monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    left=0,
                    width=int(
                        monitor_center_.x + monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    height=int(
                        monitor_center_.y + monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    )
                )
            else:
                region = Region(
                    top=int(
                        monitor_center_.y - monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    left=int(
                        monitor_center_.x - monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    width=int(
                        monitor_center_.x + monitor_region_.width * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    ),
                    height=int(
                        monitor_center_.y + monitor_region_.height * (
                            settings.BOBBER_CORNER_EXPAND_PERCENTAGE / 100
                        )
                    )
                )

        return region

    def _cancel_any_action(self) -> None:
        CommonIOController.press(settings.CANCEL_ANY_ACTION_BUTTON)

    def _calc_bobber_offset(self, bobber_region: Region) -> int:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).count_nonzero_mask()
        bobber_offset = int(
            bobber_pixels / 100 * (100 - settings.BOBBER_CATCH_THRESHOLD)
        )

        FISHER_BOT_LOGGER.debug(
            f'CALC BOBBER OFFSET: PIXELS = "{bobber_pixels}", OFFSET = "{bobber_offset}"'
        )

        return bobber_offset

    def _need_to_catch(self, bobber_region: Region, bobber_offset: int) -> bool:
        bobber_pixels: int = self._hsv_bobber_scanner(
            as_custom_region=bobber_region
        ).count_nonzero_mask()

        condition: bool = bobber_pixels < bobber_offset

        FISHER_BOT_LOGGER.debug(
            f'NEED TO CATCH => {condition}\n\tPIXELS = "{bobber_pixels}" < OFFSET = "{bobber_offset}"'
        )

        return condition

    def _find_bobber_region(self) -> Region:
        while True:
            for coordinate in self._bobber_scanner(
                as_custom_region=self._get_bobber_corner()
            ).iterate_all_by_first_founded():
                if coordinate:
                    return coordinate.region

    def _catch_when_fish_awaiting(self) -> None:
        CommonIOController.press_mouse_button_and_release(
            settings.THROW_DELAYS[random.randint(
                0, len(settings.THROW_DELAYS) - 1
            )]
        )
        time.sleep(1)

        bobber_region = self._find_bobber_region()
        bobber_offset = self._calc_bobber_offset(bobber_region)

        while True:
            condition = self._need_to_catch(bobber_region, bobber_offset)
            if condition:
                CommonIOController.mouse_left_click()
                break

            time.sleep(0.1)

    def _select_new_mouse_position_for_fishing(self, static_mouse_pos: Coordinate) -> None:
        if self._custom_catching_region is None:
            x_new = max(0, static_mouse_pos.x + random.randint(
                -settings.CATCHING_AREA_RANGE[0], settings.CATCHING_AREA_RANGE[0]
            ))
            y_new = max(0, static_mouse_pos.y + random.randint(
                -settings.CATCHING_AREA_RANGE[1], settings.CATCHING_AREA_RANGE[1]
            ))
        else:
            x_new = random.randint(
                self._custom_catching_region.left, self._custom_catching_region.width
            )
            y_new = random.randint(
                self._custom_catching_region.top, self._custom_catching_region.height
            )

        CommonIOController.move(Coordinate(x=x_new, y=y_new))

    def _check_if_actually_fish_catching(self) -> bool:
        FISHER_BOT_LOGGER.info('CHECKING IF ACTUALLY FISH CATCHING')

        FISHER_BOT_LOGGER.info('REACHING LEFT BORDER')
        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                bobber_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'BOBBER POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} <= {self._is_fish_checking_threshold_left}'
                )
                if bobber_position <= self._is_fish_checking_threshold_left:
                    FISHER_BOT_LOGGER.info('REACHED LEFT BORDER')
                    CommonIOController.press_mouse_left_button()
                    break

            time.sleep(0.1)

        FISHER_BOT_LOGGER.info('REACHING RIGHT BORDER')
        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                bobber_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'BOBBER POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} >= {self._is_fish_checking_threshold_right}'
                )
                if bobber_position >= self._is_fish_checking_threshold_right:
                    FISHER_BOT_LOGGER.info('REACHED RIGHT BORDER')
                    CommonIOController.release_mouse_left_button()
                    break

            time.sleep(0.1)
        time.sleep(0.2)

        FISHER_BOT_LOGGER.info('CHECKING FOR ACTUALLY FISH')

        last_fish_distance_pos = self._fish_catching_distance_scanner.indentify_by_first()
        if last_fish_distance_pos is None:
            FISHER_BOT_LOGGER.warning(
                'CANNOT FIND "last_fish_distance_pos" ...'
            )
            return False

        last_fish_distance_pos = (
            last_fish_distance_pos.x - last_fish_distance_pos.region.width // 2
        )

        for _ in range(10):
            if coord := self._fish_catching_distance_scanner.indentify_by_first():
                fish_distance_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'FISH DISTANCE POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} >= {last_fish_distance_pos}'
                )
                if fish_distance_position != last_fish_distance_pos:
                    FISHER_BOT_LOGGER.info('FISH RECOGNIZED')
                    return True

            time.sleep(0.05)

        FISHER_BOT_LOGGER.info('LOOKS LIKE NOT FISH. SKIPPING')
        return False

    def _prepare_for_catching(self) -> bool:

        FISHER_BOT_LOGGER.info('PREPARE FOR CATCHING')

        for _ in range(10):
            if self._catching_bobber_scanner.indentify_by_first():
                if self._check_if_actually_fish_catching():
                    return True

                self._cancel_any_action()
                self._skipped_non_fishes += 1

                return False

            time.sleep(0.1)
        else:
            FISHER_BOT_LOGGER.warning(
                'CANNOT FIND BOBBER ON CATCHING BAR WHEN PREPARING FOR CATCHING'
            )
            return False

    def _catch_fish(self) -> None:

        FISHER_BOT_LOGGER.info('CATCHING FISH')

        while True:
            if bobber_coord := self._catching_bobber_scanner.indentify_by_first():

                bobber_pos = bobber_coord.x - bobber_coord.region.width // 2
                need_to_pool = bobber_pos <= self._catching_bar_mouse_hold_threshold

                FISHER_BOT_LOGGER.debug(
                    f'NEED TO POOL BOBBER => {need_to_pool}\n\t'
                    f'BOBBER POSITION: {bobber_pos} <= CATCHING MOUSE THRESHOLD: {self._catching_bar_mouse_hold_threshold}'
                )

                if need_to_pool:
                    CommonIOController.press_mouse_left_button()
                else:
                    CommonIOController.release_mouse_left_button()
                    time.sleep(0.3)
                    CommonIOController.press_mouse_left_button()
            else:
                FISHER_BOT_LOGGER.info('CATCHED')
                CommonIOController.release_mouse_left_button()
                self._catched_fishes += 1
                break

            time.sleep(0.1)

    def run(self) -> None:
        static_mouse_pos = CommonIOController.mouse_position()

        while True:
            self._events_loop()

            self._buffs_controller.check_and_activate_buffs()
            self._select_new_mouse_position_for_fishing(static_mouse_pos)
            self._catch_when_fish_awaiting()

            if self._prepare_for_catching():
                self._catch_fish()
            else:
                continue

            FISHER_BOT_LOGGER.info(
                f'WAITING "{settings.NEW_FISH_CATCHING_AWAITING}" SECONDS BEFORE NEW CATCHING'
            )
            time.sleep(settings.NEW_FISH_CATCHING_AWAITING)


FISHER_BOT = FisherBot()
