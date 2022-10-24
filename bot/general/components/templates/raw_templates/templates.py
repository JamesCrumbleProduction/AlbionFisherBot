import os

from warnings import warn
from dataclasses import dataclass
from typing import Iterator, Generator

from .exceptions import BuffTemplatesError
from .schemas import RawTemplate, BuffRawTemplates


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def templates_generator(templates_folder: str) -> Generator[RawTemplate, None, None]:
    return (
        RawTemplate(
            label=str(*template.split('.')[:-1]),
            path=os.path.join(templates_folder, template)
        )
        for template in os.listdir(templates_folder)
        if os.path.isfile(os.path.join(templates_folder, template))
    )


def buff_templates_iterator(buffs_folder: str) -> Iterator[BuffRawTemplates]:
    for buff_folder in os.listdir(buffs_folder):

        buff_folder_path: str = os.path.join(buffs_folder, buff_folder)
        if not os.path.isdir(buff_folder_path):
            warn(
                'Buffs folder should contains only folders '
                f'with buff like structure actually but found => {buff_folder_path}'
            )
            continue

        buff_item_template_path = os.path.join(buff_folder_path, 'item.png')  # noqa
        if not os.path.exists(buff_item_template_path):
            raise BuffTemplatesError(
                f'"{buff_folder}" buff folder should contain "item.png" file'
            )

        buff_empty_slot_template_path = os.path.join(buff_folder_path, 'empty_slot.png')  # noqa
        if not os.path.exists(buff_empty_slot_template_path):
            raise BuffTemplatesError(
                f'"{buff_folder}" buff folder should contain "empty_slot.png" file'
            )

        buff_is_active_folder_path = os.path.join(buff_folder_path, 'is_active')  # noqa
        if (
            not os.path.exists(buff_is_active_folder_path)
            or not os.path.isdir(buff_is_active_folder_path)
        ):
            raise BuffTemplatesError(
                f'"{buff_folder}" buff folder should contain "is_active" folder '
                'with templates which indicates about buff is active\n\t'
                f'Checked folder => {buff_is_active_folder_path}'
            )

        yield BuffRawTemplates(
            name=buff_folder,
            item=RawTemplate(
                label='item',
                path=buff_item_template_path
            ),
            empty_slot=RawTemplate(
                label='empty_slot',
                path=buff_empty_slot_template_path
            ),
            is_active=templates_generator(buff_is_active_folder_path)
        )


@dataclass
class Paths:

    @dataclass
    class FisherBotTemplates:

        __fisher_bot_templates = os.path.join(ROOT_PATH, 'fisher_bot')

        bobbers = os.path.join(__fisher_bot_templates, 'bobbers')
        status_bar_components = os.path.join(__fisher_bot_templates, 'status_bar_components')  # noqa
        buffs = os.path.join(__fisher_bot_templates, 'buffs')


@dataclass
class RawTemplates:

    @dataclass
    class FisherBotRawTemplates:
        bobbers = templates_generator(Paths.FisherBotTemplates.bobbers)  # noqa
        status_bar_components = templates_generator(Paths.FisherBotTemplates.status_bar_components)  # noqa
        buffs = buff_templates_iterator(Paths.FisherBotTemplates.buffs)
