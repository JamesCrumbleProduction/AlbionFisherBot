import os
import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .routers import BotInfoApiRouter, BotControlApiRouter
from ..bot import FisherBot


class FisherBotServer:

    __slots__ = '_app',

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    def init_bot_data(self, bot_instance: FisherBot) -> None:
        self._app.include_router(
            BotInfoApiRouter(bot_instance),
            prefix='/bot_info',
            tags=['INFO']
        )
        self._app.include_router(
            BotControlApiRouter(bot_instance),
            prefix='/control',
            tags=['CONTROL']
        )

        @self._app.on_event('startup')
        async def on_startup():
            async def _working_event():

                while True:
                    if bot_instance.is_running is False:
                        os._exit(0)
                    await asyncio.sleep(0.5)

            asyncio.get_running_loop().create_task(
                _working_event(), name='_working_event'
            )

    @property
    def app(self) -> FastAPI:
        return self._app


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_credentials=True,
    allow_headers=['*']
)

app.add_api_route(
    '/status',
    endpoint=lambda: 1,  # type: ignore
    status_code=200,
    response_model=int
)
