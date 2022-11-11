import io

from enum import Enum
from typing import Callable
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from .world_to_screen import Region


class Status(Enum):

    PAUSED: str = 'PAUSED'  # type: ignore
    PAUSING: str = 'PAUSING'  # type: ignore
    CATCHING: str = 'CATCHING'  # type: ignore
    RELOCATE: str = 'RELOCATE'  # type: ignore
    RELOCATING: str = 'RELOCATING'  # type: ignore
    INVENTORY_LOADED: str = 'INVENTORY_LOADED'  # type: ignore


class Location(BaseModel):

    key: str
    record: list[tuple[int, int, float] | tuple[int, int, float, int]]
    catching_region: Region


class AdditionalEvent(BaseModel):

    name: str
    event: Callable
    execute_on_statuses: list[Status] = [
        status for status in Status
    ]


class LastSnapshot(StreamingResponse):

    def __init__(
        self,
        content: io.BytesIO,
        filename: str
    ) -> None:
        super().__init__(
            content,
            headers={
                'Content-Disposition': f'attachment; filename={filename}.png'
            }
        )
