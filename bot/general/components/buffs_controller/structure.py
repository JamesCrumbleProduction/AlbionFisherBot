import numpy as np

from pynput.mouse import Button

from .schemas import BuffConfig, BuffInfo
from ..world_to_screen import TemplateScanner
from ..io_controllers import CommonIOController
from ...services.logger import COMPONENTS_LOGGER


class Buff:

    __slots__ = (
        '_have_buff_item',
        '_cached_is_active',

        '_buff_config',
        '_is_active_scanner',
        '_empty_slot_scanner',
        '_in_inventory_item_scanner',
    )

    def __init__(
        self,
        buff_config: BuffConfig,
        is_active_scanner: TemplateScanner,
        empty_slot_scanner: TemplateScanner,
        in_inventory_item_scanner: TemplateScanner
    ) -> None:

        self._have_buff_item: bool = True
        self._cached_is_active: bool = False

        self._buff_config = buff_config
        self._is_active_scanner = is_active_scanner
        self._empty_slot_scanner = empty_slot_scanner
        self._in_inventory_item_scanner = in_inventory_item_scanner

    @property
    def is_active(self) -> bool:
        condition = self._is_active_scanner.get_condition_by_one()
        COMPONENTS_LOGGER.info(
            f'"{self._buff_config.name}" BUFF IS ACTIVE => {condition}'
        )
        return condition

    @property
    def is_available_to_activate(self) -> bool:
        condition = not self._empty_slot_scanner.get_condition_by_one()
        COMPONENTS_LOGGER.info(
            f'"{self._buff_config.name}" BUFF IS AVAILABLE TO ACTIVATE => {condition}'
        )
        return condition

    def find_and_set_item(self, inventory_part_image: np.ndarray) -> bool:
        for coord in self._in_inventory_item_scanner(
            as_custom_image=inventory_part_image
        ).iterate_all_by_first_founded():
            if coord:
                past_mouse_coord = CommonIOController.mouse_position()
                CommonIOController.move_and_click(coord, Button.right)
                CommonIOController.move(past_mouse_coord)
                return True

        return False

    @property
    def have_buff_item(self) -> bool:
        return self._have_buff_item

    @have_buff_item.setter
    def have_buff_item(self, value: bool) -> None:
        self._have_buff_item = value

    @property
    def name(self) -> str:
        return self._buff_config.name

    @property
    def activation_key(self) -> str:
        return self._buff_config.activation_key

    @property
    def buff_info(self) -> BuffInfo:
        return BuffInfo(
            name=self._buff_config.name,
            is_active=self._cached_is_active,
            is_available_to_activate=self._have_buff_item
        )
