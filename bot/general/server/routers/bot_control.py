from fastapi import APIRouter
from typing import TYPE_CHECKING

from ...components.schemas import Status

if TYPE_CHECKING:
    from ...bot import FisherBot


class BotControlApiRouter(APIRouter):

    def __init__(self, bot_instance: 'FisherBot', *args, **kwargs):
        super().__init__(*args, **kwargs)

        def change_status(status: Status) -> None:
            bot_instance.change_status(status)

        self.add_api_route(
            path='/change_status',
            endpoint=change_status,
            methods=['POST'],
            status_code=200
        )
