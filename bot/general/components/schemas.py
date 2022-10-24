from enum import Enum


class Status(Enum):

    PAUSED: str = 'PAUSED'
    PAUSING: str = 'PAUSING'
    CATCHING: str = 'CATCHING'
