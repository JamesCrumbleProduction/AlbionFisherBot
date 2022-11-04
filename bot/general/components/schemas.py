from enum import Enum


class Status(Enum):

    PAUSED: str = 'PAUSED'  # type: ignore
    PAUSING: str = 'PAUSING'  # type: ignore
    CATCHING: str = 'CATCHING'  # type: ignore
