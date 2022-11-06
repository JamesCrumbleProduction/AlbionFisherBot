from enum import Enum
from pydantic import BaseModel

from .world_to_screen import Region


class Status(Enum):

    PAUSED: str = 'PAUSED'  # type: ignore
    PAUSING: str = 'PAUSING'  # type: ignore
    CATCHING: str = 'CATCHING'  # type: ignore
    RELOCATING: str = 'RELOCATING'  # type: ignore


class Location(BaseModel):

    key: str
    record: list[tuple[int, int, float]]
    catching_region: Region
