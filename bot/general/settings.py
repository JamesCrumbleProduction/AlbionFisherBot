import numpy as np

from dataclasses import dataclass
from pydantic import BaseSettings


class HSVConfigs(BaseSettings):

    @dataclass
    class Bobber:
        # [Hmin, Smin, Vmin]
        LOWER_HSV_ARRAY = np.array(
            [0, 157, 206],
            dtype=np.uint8, copy=False
        )
        # [Hmax, Smax, Vmax]
        HIGHER_HSV_ARRAY = np.array(
            [3, 224, 255],
            dtype=np.uint8, copy=False
        )


class BotSettings(BaseSettings):

    # fishing rod throwing delay
    THROW_DELAY: float = 0.6
    BOBBER_CATCH_THRESHOLD: int = 40  # in percentage
    MOUSE_CATCHING_BAR_THRESHOLD: int = 60  # in percentage
    BOBBER_REGION_EXTENDED_PERCENTAGE: int = 30

    assert 0 <= BOBBER_CATCH_THRESHOLD <= 100
    assert 0 <= MOUSE_CATCHING_BAR_THRESHOLD <= 100
    assert 0 <= BOBBER_REGION_EXTENDED_PERCENTAGE <= 100


class IOServiceSettings(BaseSettings):

    CLICK_INTERVAL: float = 0.1


class Settings(BaseSettings):

    BOT = BotSettings()
    HSV_CONFIGS = HSVConfigs()
    IO_SERVICE = IOServiceSettings()


settings = Settings()
