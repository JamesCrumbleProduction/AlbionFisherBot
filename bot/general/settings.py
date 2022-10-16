from pydantic import BaseSettings


class Settings(BaseSettings):
    # fishing rod throwing delay
    THROW_DELAY: float = 0.6
    BOBBER_CATCH_THRESHOLD: int = 40  # in percentage
    MOUSE_CATCHING_BAR_THRESHOLD: int = 60  # in percentage
    BOBBER_REGION_EXTENDED_PERCENTAGE: int = 30

    assert 0 <= BOBBER_CATCH_THRESHOLD <= 100
    assert 0 <= MOUSE_CATCHING_BAR_THRESHOLD <= 100
    assert 0 <= BOBBER_REGION_EXTENDED_PERCENTAGE <= 100


settings = Settings()
