import time
import numpy as np

from typing import Iterator
from pynput.keyboard import KeyCode


from .structure import Buff
from ..templates import CompiledTemplate, to_cvt_color
from ..world_to_screen import TemplateScanner, grab_screen
from ..io_controllers import CommonIOController, ScrollDirection

BUFF_COOLDOWN: float = 1.0
ITEM_USED_TO_UTILITY_BAR_COOLDOWN: float = 8.0
OPEN_INVENTORY_KEYCODE: KeyCode = KeyCode.from_char('i')


class BuffsController:

    __slots__ = (
        '_buffs',
        '_inventory_is_opened',
    )

    def __init__(self, *buffs: Buff):
        self._buffs = buffs
        self._inventory_is_opened: bool = False

    def _open_inventory(self) -> None:
        if not self._inventory_is_opened:
            CommonIOController.press(OPEN_INVENTORY_KEYCODE)
            self._inventory_is_opened = True

    def _close_inventory(self) -> None:
        if self._inventory_is_opened:
            CommonIOController.press(OPEN_INVENTORY_KEYCODE)
            self._inventory_is_opened = False

    def _iterate_through_inventory(self) -> Iterator[np.ndarray]:
        CommonIOController.move()  # Inventory region + 3 pixels gap inside

        past_inventory_image = grab_screen()  # Inventory region
        yield past_inventory_image
        CommonIOController.scroll(1, ScrollDirection.DOWN)
        time.sleep(1.5)

        while True:

            new_inventory_image = grab_screen()

            if TemplateScanner(CompiledTemplate(
                label='',
                template_data=to_cvt_color(past_inventory_image)
            ), threshold=0.97)(as_custom_image=new_inventory_image).get_condition_by_one():
                break

            yield new_inventory_image
            CommonIOController.scroll(1, ScrollDirection.DOWN)
            time.sleep(1.5)

    def _set_items_to_utility_bar(self, initing_buffs: list[Buff]) -> tuple[float | None, list[Buff]]:
        past_mouse_position = CommonIOController.mouse_position()
        self._open_inventory()

        setted_buffs: list[Buff] = list()
        last_setted_buff_time: float = None

        def setted_buffs_contains(buff: Buff) -> bool:
            for setted_buff in setted_buffs:
                if buff.name == setted_buff.name:
                    return True

            return False

        for inventory_part_image in self._iterate_through_inventory():
            for buff in initing_buffs:
                if not setted_buffs_contains(buff) and buff.find_and_set_item(inventory_part_image):
                    setted_buffs.append(buff)
                    last_setted_buff_time = time.time()

            if len(setted_buffs) == len(initing_buffs):
                CommonIOController.move(past_mouse_position)
                self._close_inventory()
                return last_setted_buff_time, setted_buffs

        CommonIOController.move(past_mouse_position)
        self._close_inventory()
        return last_setted_buff_time, setted_buffs

    def _activate_buff(buff: Buff) -> None:
        CommonIOController.press(buff.activation_key)
        time.sleep(BUFF_COOLDOWN)

    def check_and_activate_buffs(self) -> None:

        need_to_init_buffs: list[Buff] = list()

        for buff in self._buffs:
            if buff.have_buff_item:
                if not buff.is_active and buff.is_available_to_activate:
                    self._activate_buff(buff)
                else:
                    need_to_init_buffs.append(buff)

        if need_to_init_buffs:
            last_setted_buff_time, setted_buffs = self._set_items_to_utility_bar(
                need_to_init_buffs
            )

            if last_setted_buff_time is not None:
                time.sleep(ITEM_USED_TO_UTILITY_BAR_COOLDOWN - (
                    time.time() - last_setted_buff_time
                ))

                for buff in setted_buffs:
                    self._activate_buff(buff)

    @property
    def buffs(self) -> Iterator[Buff]:
        for buff in self._buffs:
            yield buff.buff_info
