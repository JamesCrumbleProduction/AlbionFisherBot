import time
import httpx
import orjson
import random

from typing import Iterator

from .settings import settings
from .components.rotations import Rotations
from .services.logger import FISHER_BOT_LOGGER
from .components.events_loop import EventsLoop
from .components.schemas import Status, Location
from .components.info_interface import InfoInterface
from .components.paths import LAST_LOCATION_FILE_PATH
from .components.io_controllers import CommonIOController
from .components.templates import FISHER_BOT_COMPILED_TEMPLATES
from .components.settings import settings as components_settings
from .components.exceptions import FishAwaitingError, IsActuallyFishCatchingError
from .components.buffs_controller import Buff, BuffConfig, BuffInfo, BuffsController
from .components.world_to_screen import (
    Region,
    HSVScanner,
    Coordinate,
    ScreenPart,
    monitor_center,
    TemplateScanner,
    get_screen_part_region,
    ThreadedTemplateScanner,
)


class FisherBot(InfoInterface):

    __slots__ = (
        'is_running',
        '_rotations',
        '_events_loop',
        '_bobber_scanner',
        '_catching_region',
        '_buffs_controller',
        '_hsv_bobber_scanner',
        '_mouted_buff_scanner',
        '_is_machine_registered',
        '_inventory_load_scanner',
        '_catching_bobber_scanner',
        '_fish_catching_distance_scanner',
        '_fish_distance_catched_threshold',
        '_is_fish_checking_threshold_left',
        '_is_fish_checking_threshold_right',
        '_catching_bar_mouse_hold_threshold',
    )

    def __init__(self) -> None:
        super().__init__()

        self.is_running: bool = True
        self._is_machine_registered: bool = False

        self._rotations: Rotations = Rotations()
        self._events_loop: EventsLoop = EventsLoop(self)
        self._events_loop.add_event(
            event_name='INVENTORY LOADED',
            event=self._inventory_loaded_event,
            execute_on_statuses=[Status.CATCHING, Status.INVENTORY_LOADED]
        )

        self._inventory_load_scanner: HSVScanner = HSVScanner(
            hsv_ranges=components_settings.HSV_CONFIGS.INVETORY_LOAD,
            region=components_settings.REGIONS.INVENTORY_LOAD
        )

        self._catching_region: Region | None = self._init_catching_region()

        self._init_scanners()
        self._init_catching_thresholds()
        self._init_buffs_controller()

    @property
    def buffs(self) -> Iterator[BuffInfo]:
        yield from self._buffs_controller.buffs

    @property
    def current_location(self) -> str:
        return self._rotations.current_location

    def _is_inventory_loaded(self) -> bool:
        return not bool(self._inventory_load_scanner.count_nonzero_mask())

    def _inventory_loaded_event(self) -> None:
        if self._is_inventory_loaded():
            self.change_status(Status.INVENTORY_LOADED)
        elif self.status is Status.INVENTORY_LOADED:
            self.change_status(Status.CATCHING)

    def set_new_catching_region(self, new_region: Region) -> None:
        self._catching_region = new_region
        FISHER_BOT_LOGGER.info(
            f'NEW "{self._catching_region}" CATCHING REGION WAS SETTED UP'
        )

    def change_status(self, status: Status, call_from_server: bool = False) -> None:
        if self._status is Status.RELOCATING and call_from_server:
            FISHER_BOT_LOGGER.info('CANNOT CHANGE STATUS COUSE BOT IS RELOCATING')
            return

        if status is Status.INVENTORY_LOADED and call_from_server:
            FISHER_BOT_LOGGER.info(f'CANNOT CHANGE TO "{status.value}" STATUS FROM SERVER')
            return

        if self._status is Status.INVENTORY_LOADED and status is not Status.CATCHING:
            FISHER_BOT_LOGGER.info('STATUS "INVENTORY_LOADED" CAN CHANGE TO "CATCHING" STATUS ONLY')
            return

        if status is Status.CATCHING and self._catching_region is None:
            FISHER_BOT_LOGGER.warning('CANNOT START CATCHING FISH COUSE CATCHING REGION WAS NOT SETTED UP')
            return

        if self._status is not Status.PAUSING and status is Status.PAUSED:
            status = Status.PAUSING

        self._status = status

    def save_current_location(self) -> None:
        if self.current_location == '':
            return

        with open(LAST_LOCATION_FILE_PATH, 'wb') as handle:
            handle.write(orjson.dumps({'last_location': self.current_location}))

    def _init_catching_region(self) -> Region | None:
        if self.current_location == '':
            return

        return self._rotations.get_location_data(self.current_location).catching_region

    def _init_bobber_scanners(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING BOBBER SCANNERS')
        self._hsv_bobber_scanner = HSVScanner(
            components_settings.HSV_CONFIGS.BOBBER_RANGES
        )

        bobber_templates_scanner = ThreadedTemplateScanner if settings.THREADED_BOBBER_SCANNER else TemplateScanner
        self._bobber_scanner = bobber_templates_scanner(
            iterable_templates=FISHER_BOT_COMPILED_TEMPLATES.bobbers.templates,
            threshold=0.65
        )

    def _init_catching_thresholds(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING CATCHING THRESHOLDS')
        self._fish_distance_catched_threshold = int(
            components_settings.REGIONS.CATCHING_BAR.left
            + components_settings.REGIONS.CATCHING_BAR.width * 0.8
        )
        self._catching_bar_mouse_hold_threshold = int(
            components_settings.REGIONS.CATCHING_BAR.left
            + components_settings.REGIONS.CATCHING_BAR.width * 0.7
        )
        self._is_fish_checking_threshold_left = int(
            components_settings.REGIONS.CATCHING_BAR.left
            + components_settings.REGIONS.CATCHING_BAR.width * 0.4
        )
        self._is_fish_checking_threshold_right = int(
            components_settings.REGIONS.CATCHING_BAR.left
            + components_settings.REGIONS.CATCHING_BAR.width * 0.65
        )

    def _init_scanners(self) -> None:
        self._init_bobber_scanners()
        self._init_catching_scanners()
        self._mouted_buff_scanner: TemplateScanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.other.get('mounted_buff'),
            region=components_settings.REGIONS.ACTIVE_BUFFS,
            threshold=0.7
        )

    def _init_catching_scanners(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING CATCHING SCANNERS')
        self._fish_catching_distance_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'fish_catched_distance'
            ), threshold=0.8, region=components_settings.REGIONS.CATCHING_BAR
        )
        self._catching_bobber_scanner = TemplateScanner(
            FISHER_BOT_COMPILED_TEMPLATES.status_bar_components.get(
                'bobber_status_bar'
            ), threshold=0.8, region=components_settings.REGIONS.CATCHING_BAR
        )

    def _init_buffs_controller(self) -> None:
        FISHER_BOT_LOGGER.debug('INITING BUFFS CONTROLLER')

        bait_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('bait')
        eat_buff = FISHER_BOT_COMPILED_TEMPLATES.buffs.get('pie_eat')

        self._buffs_controller = BuffsController(
            Buff(
                buff_config=BuffConfig(
                    name=bait_buff.name,
                    activation_key='1'
                ),
                is_active_scanner=TemplateScanner(
                    iterable_templates=bait_buff.is_active,
                    threshold=0.6, region=components_settings.REGIONS.ACTIVE_BUFFS
                ),
                empty_slot_scanner=TemplateScanner(
                    bait_buff.empty_slot,
                    threshold=0.7, region=components_settings.REGIONS.BUFFS_UTILITY_BAR
                ),
                in_inventory_item_scanner=TemplateScanner(
                    bait_buff.item,
                    threshold=0.7, region=components_settings.REGIONS.INVENTORY
                )
            ),
            Buff(
                buff_config=BuffConfig(
                    name=eat_buff.name,
                    activation_key='2'
                ),
                is_active_scanner=TemplateScanner(
                    iterable_templates=eat_buff.is_active,
                    threshold=0.7, region=components_settings.REGIONS.ACTIVE_BUFFS
                ),
                empty_slot_scanner=TemplateScanner(
                    eat_buff.empty_slot,
                    threshold=0.7, region=components_settings.REGIONS.BUFFS_UTILITY_BAR
                ),
                in_inventory_item_scanner=TemplateScanner(
                    eat_buff.item,
                    threshold=0.7, region=components_settings.REGIONS.INVENTORY
                )
            )
        )

    def _get_bobber_corner(self) -> Region:
        monitor_center_ = monitor_center()
        mouse_position = CommonIOController.mouse_position()

        if mouse_position.y < monitor_center_.y:
            if mouse_position.x < monitor_center_.x:
                return get_screen_part_region(ScreenPart.TOP_LEFT)
            else:
                return get_screen_part_region(ScreenPart.TOP_RIGHT)

        else:
            if mouse_position.x < monitor_center_.x:
                return get_screen_part_region(ScreenPart.BOTTOM_LEFT)
            else:
                return get_screen_part_region(ScreenPart.BOTTOM_RIGHT)

    def _cancel_any_action(self) -> None:
        CommonIOController.press(settings.CANCEL_ANY_ACTION_BUTTON)

    def _define_sleep_value(self, fish_is_catched: bool) -> float:
        '''Used for testing purposes only'''
        return settings.NEW_FISH_CATCHING_AWAITING

    def _should_relocate(self) -> bool:
        if self.current_location == '':
            return False

        if self._is_inventory_loaded():
            return False

        if self._skipped_in_row % 2 == 0 and self._skipped_in_row != 0:
            return True

        return False

    def _calc_bobber_offset(self, bobber_region: Region, in_cycle: bool = True) -> int:

        max_bobber_offset: int = 0
        sleep_per_cycle: float = (1 / settings.BOBBER_OFFSET_CALCULATION_CYCLES) if in_cycle else 0

        for _ in range(settings.BOBBER_OFFSET_CALCULATION_CYCLES if in_cycle else 1):
            bobber_pixels: int = self._hsv_bobber_scanner(as_custom_region=bobber_region).count_nonzero_mask()
            bobber_offset = int(bobber_pixels / 100 * (100 - settings.BOBBER_CATCH_THRESHOLD))

            if max_bobber_offset < bobber_offset:
                max_bobber_offset = bobber_offset

            time.sleep(sleep_per_cycle)

        FISHER_BOT_LOGGER.debug(f'DEFINED BOBBER OFFSET = "{max_bobber_offset}"')
        return max_bobber_offset

    def _need_to_catch(self, bobber_region: Region, bobber_offset: int) -> bool:
        bobber_pixels: int = self._hsv_bobber_scanner(as_custom_region=bobber_region).count_nonzero_mask()
        condition: bool = bobber_pixels < bobber_offset

        FISHER_BOT_LOGGER.debug(
            f'NEED TO CATCH => {condition}\n\tPIXELS = "{bobber_pixels}" < OFFSET = "{bobber_offset}"'
        )
        return condition

    def _find_bobber_region_with_timeout(self, timeout: float | None = None) -> Region | None:
        st: float = time.monotonic()
        bobber_finding_attempts: int = 0

        while True:
            for coordinate in self._bobber_scanner(as_custom_region=self._get_bobber_corner()).iterate_all_by_first_founded():
                if coordinate:
                    FISHER_BOT_LOGGER.info(f'FOUND BOBBER REGION FROM "{bobber_finding_attempts}" TEMPLATE')
                    return coordinate.region

                bobber_finding_attempts += 1

            if timeout is not None and time.monotonic() - st > timeout:
                return

            time.sleep(0.15)

    def _find_bobber_region(self) -> Region:
        return self._find_bobber_region_with_timeout()  # type: ignore

    def _catch_when_fish_awaiting(self) -> None:
        CommonIOController.press_mouse_button_and_release(
            settings.THROW_DELAYS[random.randint(0, len(settings.THROW_DELAYS) - 1)]
        )
        time.sleep(1)

        bobber_region = self._find_bobber_region_with_timeout(
            timeout=settings.BOBBER_REGION_TIMEOUT_FINDING
        )
        if bobber_region is None:
            raise FishAwaitingError(
                f'CANNOT FIND BOBBER REGION FOR "{settings.BOBBER_REGION_TIMEOUT_FINDING}" SECONDS'
            )

        bobber_offset = self._calc_bobber_offset(bobber_region, in_cycle=False)
        last_offset_calc_time: float = time.monotonic()

        while True:
            if self._need_to_catch(bobber_region, bobber_offset):
                CommonIOController.mouse_left_click()
                break

            if bobber_offset == 0:
                if time.monotonic() - last_offset_calc_time > settings.RECALC_BOBBER_OFFSET_TIMEOUT:
                    raise FishAwaitingError(f'BOBBER OFFSET EQUALS 0 FOR "{settings.RECALC_BOBBER_OFFSET_TIMEOUT}" SECONDS')

                if new_bobber_region := self._find_bobber_region_with_timeout(timeout=5):
                    bobber_offset = self._calc_bobber_offset(new_bobber_region)
                else:
                    raise FishAwaitingError(
                        'BOBBER OFFSET EQUALS 0 AND BOBBER REGION CANNOT BE DEFINED '
                        f'FOR "{settings.RECALC_BOBBER_OFFSET_TIMEOUT}" SECONDS'
                    )

            if time.monotonic() - last_offset_calc_time > settings.RECALC_BOBBER_OFFSET_TIMEOUT:
                last_offset_calc_time = time.monotonic()
                bobber_offset = self._calc_bobber_offset(bobber_region, in_cycle=False)
                FISHER_BOT_LOGGER.info(f'NEW BOBBER OFFSET => "{bobber_offset}"')

            time.sleep(0.1)

    def _select_new_mouse_position_for_fishing(self) -> None:
        if self._catching_region is None:
            raise ValueError('CATGHING REGION CANNOT BE NULL')

        x_new = random.randint(
            *sorted([self._catching_region.left, self._catching_region.width])
        )
        y_new = random.randint(
            *sorted([self._catching_region.top, self._catching_region.height])
        )

        CommonIOController.move(Coordinate(x=x_new, y=y_new))

    def _check_if_actually_fish_catching(self) -> bool:
        FISHER_BOT_LOGGER.info('CHECKING IF ACTUALLY FISH CATCHING')

        FISHER_BOT_LOGGER.info('REACHING LEFT BORDER')
        st: float = time.monotonic()
        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                st = time.monotonic()
                bobber_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'BOBBER POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} <= {self._is_fish_checking_threshold_left}'
                )
                if bobber_position <= self._is_fish_checking_threshold_left:
                    FISHER_BOT_LOGGER.info('REACHED LEFT BORDER')
                    CommonIOController.press_mouse_left_button()
                    break
            elif time.monotonic() - st >= settings.REAL_FISH_BOBBER_FINDING_TIMEOUT:
                raise IsActuallyFishCatchingError('CANNOT FIND BOBBER OF CATCHING BAR WHEN REACHING LEFT BORDER')

            time.sleep(0.1)

        FISHER_BOT_LOGGER.info('REACHING RIGHT BORDER')
        st: float = time.monotonic()
        while True:
            if coord := self._catching_bobber_scanner.indentify_by_first():
                st = time.monotonic()
                bobber_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'BOBBER POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} >= {self._is_fish_checking_threshold_right}'
                )
                if bobber_position >= self._is_fish_checking_threshold_right:
                    FISHER_BOT_LOGGER.info('REACHED RIGHT BORDER')
                    CommonIOController.release_mouse_left_button()
                    break
            elif time.monotonic() - st >= settings.REAL_FISH_BOBBER_FINDING_TIMEOUT:
                raise IsActuallyFishCatchingError('CANNOT FIND BOBBER OF CATCHING BAR WHEN REACHING RIGHT BORDER')

            time.sleep(0.1)
        time.sleep(0.3)

        FISHER_BOT_LOGGER.info('CHECKING FOR ACTUALLY FISH')

        last_fish_distance_pos = self._fish_catching_distance_scanner.indentify_by_first()
        if last_fish_distance_pos is None:
            raise IsActuallyFishCatchingError('CANNOT FIND FISH PROGRESSION OF DISTANCE BAR ON CATCHING BAR')

        last_fish_distance_pos = (
            last_fish_distance_pos.x - last_fish_distance_pos.region.width // 2
        )

        for _ in range(5):
            if coord := self._fish_catching_distance_scanner.indentify_by_first():
                fish_distance_position = coord.x - coord.region.width // 2
                FISHER_BOT_LOGGER.debug(
                    f'FISH DISTANCE POSITION = "{bobber_position}"\n\t'
                    f'{bobber_position} >= {last_fish_distance_pos}'
                )
                if fish_distance_position != last_fish_distance_pos:
                    FISHER_BOT_LOGGER.info('FISH RECOGNIZED')
                    return True

            time.sleep(0.1)

        FISHER_BOT_LOGGER.info('LOOKS LIKE NOT FISH. SKIPPING')
        return False

    def _catch_fish(self) -> bool:

        FISHER_BOT_LOGGER.info('CATCHING FISH')
        last_fish_distance_position: int = 0
        fish_is_catched: bool = False

        while True:
            if bobber_coord := self._catching_bobber_scanner.indentify_by_first():

                if fish_distance_coord := self._fish_catching_distance_scanner.indentify_by_first():
                    last_fish_distance_position = (
                        fish_distance_coord.x - fish_distance_coord.region.width // 2
                    )

                bobber_pos = bobber_coord.x - bobber_coord.region.width // 2
                need_to_release = bobber_pos >= self._catching_bar_mouse_hold_threshold

                FISHER_BOT_LOGGER.debug(
                    f'NEED TO RELEASE BUTTON => {need_to_release}\n\t'
                    f'BOBBER POSITION: {bobber_pos} <= CATCHING BAR MOUSE THRESHOLD: {self._catching_bar_mouse_hold_threshold}'
                )

                if need_to_release:
                    CommonIOController.release_mouse_left_button()
                    time.sleep(0.09)
                    CommonIOController.press_mouse_left_button()
                else:
                    CommonIOController.press_mouse_left_button()
            else:
                CommonIOController.release_mouse_left_button()

                FISHER_BOT_LOGGER.debug(
                    f'LAST FISH DISTANCE: {last_fish_distance_position} '
                    f'>= FISH DISTANCE THRESHOLD: {self._fish_distance_catched_threshold}'
                )

                if (
                    last_fish_distance_position is not None
                    and last_fish_distance_position >= self._fish_distance_catched_threshold
                ):
                    FISHER_BOT_LOGGER.info('CATCHED')
                    self._catched_fishes += 1
                    fish_is_catched = True
                else:
                    FISHER_BOT_LOGGER.info(
                        'LOOKS LIKE FISH CATCHING WAS FAILED'
                    )
                    self._catching_errors += 1

                break

            time.sleep(0.1)

        CommonIOController.release_mouse_left_button()
        return fish_is_catched

    def _sit_on_animal(self) -> None:
        CommonIOController.press(settings.SIT_TO_ANIMAL_BUTTON)

        while True:
            if self._mouted_buff_scanner.get_condition_by_one():
                break
            time.sleep(1)

    def _get_down_of_animal(self) -> None:
        CommonIOController.press(settings.SIT_TO_ANIMAL_BUTTON)

        while True:
            if not self._mouted_buff_scanner.get_condition_by_one():
                break
            time.sleep(1)

    def _prepare_to_relocate(self) -> None:
        self._sit_on_animal()

    def _prepare_to_catching_when_relocated(self, location: Location) -> None:
        self._get_down_of_animal()
        self.set_new_catching_region(location.catching_region)

    def relocate_to_next_location(self) -> None:
        if self.current_location == '':
            FISHER_BOT_LOGGER.debug(
                'CANNOT RELOCATE COUSE LOOK LIKE RELOCATION RECORDS WAS NOT FOUNDED OR DOES NOT EXISTED'
            )
            return

        self.change_status(Status.RELOCATING)

        new_location_key = self._rotations.define_new_location_for_relocating()
        location = self._rotations.get_location_data(new_location_key)

        self._prepare_to_relocate()
        self._rotations.resolve_path(location)
        self._prepare_to_catching_when_relocated(location)

        self.change_status(Status.CATCHING)
        self._rotations.current_location = location.key
        time.sleep(0.5)

    def _register_machine(self) -> None:
        if self._is_machine_registered:
            return

        if settings.VM_NAME == '' or settings.MONITORING_SERVER_HOST == '':
            FISHER_BOT_LOGGER.warning(
                'CANNOT REGISTER MACHINE COUSE VM NAME OR MONITORING SERVER HOST IS NOT DEFINED'
            )
            return

        try:
            with httpx.Client() as client:
                client.post(
                    f'http://{settings.MONITORING_SERVER_HOST}:{settings.MONITORING_SERVER_PORT}/register_machine',
                    params={'vm_name': settings.VM_NAME, 'port': settings.SERVER_PORT}, timeout=1
                )
        except Exception as exception:
            FISHER_BOT_LOGGER.error(f'CANNOT REGISTER MACHINE ON MONITORING SERVER => {exception}')
        else:
            self._is_machine_registered = True

    def run(self) -> None:
        while True:
            fish_is_catched: bool = False
            self._register_machine()
            self._save_last_snapshot()

            if self._should_relocate():
                self.relocate_to_next_location()

            self._events_loop()
            self._buffs_controller.check_and_activate_buffs()
            self._select_new_mouse_position_for_fishing()

            sleep_time: float = 0

            try:
                self._catch_when_fish_awaiting()
                need_to_catch: bool = self._check_if_actually_fish_catching()
            except (FishAwaitingError, IsActuallyFishCatchingError) as exception:
                FISHER_BOT_LOGGER.warning(exception)
                self._catching_errors += 1
                self._cancel_any_action()
            else:
                if need_to_catch:
                    fish_is_catched = self._catch_fish()
                    if fish_is_catched:
                        self._skipped_in_row = 0
                        sleep_time = self._define_sleep_value(fish_is_catched)
                else:
                    self._skipped_non_fishes += 1
                    self._skipped_in_row += 1
                    self._cancel_any_action()

            FISHER_BOT_LOGGER.info(
                f'WAITING "{sleep_time}" SECONDS BEFORE NEW CATCHING'
            )
            time.sleep(sleep_time)


FISHER_BOT = FisherBot()
