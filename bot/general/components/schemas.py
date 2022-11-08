import io

from enum import Enum
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from .world_to_screen import Region


class Status(Enum):

    PAUSED: str = 'PAUSED'  # type: ignore
    PAUSING: str = 'PAUSING'  # type: ignore
    CATCHING: str = 'CATCHING'  # type: ignore
    RELOCATE: str = 'RELOCATE'  # type: ignore
    RELOCATING: str = 'RELOCATING'  # type: ignore


class Location(BaseModel):

    key: str
    record: list[tuple[int, int, float]]
    catching_region: Region


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
