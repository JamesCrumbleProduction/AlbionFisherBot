from fastapi import APIRouter

from ...bot import FisherBot
from ...components.schemas import Status


class BotControlApiRouter(APIRouter):

    def __init__(self, bot_instance: FisherBot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def change_status(status: Status) -> None:
            bot_instance.change_status(status)

        self.add_api_route(
            path='/change_status',
            endpoint=change_status,
            methods=['POST'],
            status_code=200
        )
