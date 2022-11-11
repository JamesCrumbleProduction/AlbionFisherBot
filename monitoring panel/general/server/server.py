import os
import asyncio

from fastapi import FastAPI
from typing import TYPE_CHECKING
from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from ..tmp_panel import Panel


class MonitoringPanelServer:

    __slots__ = '_app',

    def __init__(self, app: FastAPI):
        self._app = app

    def init_panel_data(self, panel_instance: 'Panel') -> None:
        self._app.add_api_route(
            path='/register_machine',
            endpoint=panel_instance.register_machine,  # type: ignore
            methods=['POST']
        )

        @self._app.on_event('startup')
        async def on_startup():
            async def _working_event():

                while True:
                    if panel_instance.is_running is False:
                        os._exit(0)
                    await asyncio.sleep(0.5)

            asyncio.get_running_loop().create_task(
                _working_event(), name='_working_event'
            )


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_credentials=True,
    allow_headers=['*']
)
app.add_api_route(
    path='/status',
    endpoint=lambda: 1,  # type: ignore
    methods=['GET']
)
