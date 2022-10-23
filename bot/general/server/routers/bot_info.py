from fastapi import APIRouter
from typing import TYPE_CHECKING

from .schemas import BotInfo
from ...components.schemas import Status


if TYPE_CHECKING:
    from ...bot import FisherBot


class BotInfoApiRouter(APIRouter):

    def __init__(self, bot_instance: 'FisherBot', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_api_route(
            path='/status',
            endpoint=lambda: bot_instance.status,
            methods=['GET'],
            response_model=Status,
            status_code=200
        )

        self.add_api_route(
            path='/info',
            endpoint=lambda: BotInfo(
                catched_fishes=bot_instance.catched_fishes,
                catching_errors=bot_instance.catching_errors,
                skipped_non_fishes=bot_instance.skipped_non_fishes,
                session_start_datetime=bot_instance.session_start_datetime,
                buffs=list(bot_instance.buffs)
            ),
            methods=['GET'],
            response_model=BotInfo,
            status_code=200
        )
