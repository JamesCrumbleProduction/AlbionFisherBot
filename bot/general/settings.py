from pydantic import BaseSettings


class Settings(BaseSettings):
    # fishing rod throwing delay
    THROW_DELAYS: list[float] = [
        0.4, 0.45,
        0.5, 0.55,
        0.6, 0.65,
        0.7, 0.75,
        0.8,
    ]
    CATCHING_AREA_RANGE: tuple[int, int] = (30, 30)  # (x, y)
    BOBBER_CATCH_THRESHOLD: int = 40  # in percentage

    assert 0 <= BOBBER_CATCH_THRESHOLD <= 100


settings = Settings()
