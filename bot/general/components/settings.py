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


class IOServiceSettings(BaseSettings):

    CLICK_INTERVAL: float = 0.1


class ComponentsSettings(BaseSettings):

    HSV_CONFIGS = HSVConfigs()
    IO_SERVICE = IOServiceSettings()


settings = ComponentsSettings()
