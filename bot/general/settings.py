import logging

from pydantic import BaseSettings


class Settings(BaseSettings):

    LOGGING_LEVEL: int = logging.DEBUG
    LOGGING_FILENAME: str = 'logging.log'
    CLEAR_LOGGING_FILE_SIZE_LIMIT: int = 10  # MB

    # fishing rod throwing delay
    THROW_DELAYS: list[float] = [
        # 0.4, 0.45,
        # 0.5, 0.55,
        # 0.6, 0.65,
        # 0.7, 0.75,
        1, 1.05, 1.07, 1.073, 1.1
    ]
    BOBBER_CORNER_EXPAND_PERCENTAGE: int = 5
    CANCEL_ANY_ACTION_BUTTON: str = 's'
    NEW_FISH_CATCHING_AWAITING: float = 1.8
    CATCHING_AREA_RANGE: tuple[int, int] = (30, 100)  # (x, y)
    BOBBER_CATCH_THRESHOLD: int = 40  # in percentage

    SERVER_PORT: int = 4000
    SERVER_HOST: str = '0.0.0.0'

    assert 0 <= BOBBER_CATCH_THRESHOLD <= 100


settings = Settings()
