import logging

from pydantic import BaseSettings


class Settings(BaseSettings):

    LOGGING_LEVEL: int = logging.DEBUG
    LOGGING_FILENAME: str = 'logging.log'
    CLEAR_LOGGING_FILE_SIZE_LIMIT: int = 10  # MB

    # fishing rod throwing delay
    THROW_DELAYS: list[float] = [
        1, 1.05, 1.07, 1.073, 1.1
    ]

    SIT_TO_ANIMAL_BUTTON: str = 'a'
    SIT_TO_ANIMAL_TIMEOUT: float = 4.0
    CANCEL_ANY_ACTION_BUTTON: str = 's'
    NEW_FISH_CATCHING_AWAITING: float = 1.8
    BOBBER_CATCH_THRESHOLD: int = 30  # in percentage
    BOBBER_OFFSET_CALCULATION_CYCLES: int = 10
    BOBBER_REGION_TIMEOUT_FINDING: float = 10.0
    RECALC_BOBBER_OFFSET_TIMEOUT: float = 10.0  # in seconds
    REAL_FISH_BOBBER_FINDING_TIMEOUT: float = 2.0
    THREADED_BOBBER_SCANNER: bool = True

    SERVER_PORT: int = 4000
    SERVER_HOST: str = '0.0.0.0'

    assert 0 <= BOBBER_CATCH_THRESHOLD <= 100


settings = Settings()
