import numpy as np

from dataclasses import dataclass
from pydantic import BaseSettings

from .world_to_screen import Region


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


class Regions(BaseSettings):
    ACTIVE_BUFFS: Region = Region(
        top=60,
        left=50,
        height=89,
        width=214
    )
    CATCHING_BAR: Region = Region(
        top=382,
        left=426,
        height=38,
        width=172
    )
    BUFFS_UTILITY_BAR: Region = Region(
        left=525,
        top=710,
        height=50,
        width=117
    )
    INVENTORY: Region = Region(
        top=363,
        left=760,
        height=314,
        width=233
    )


class IOServiceSettings(BaseSettings):

    CLICK_INTERVAL: float = 0.1
    MOUSE_MOVING_TIME_RANGES: list[float] = [
        0.15,
        0.2,
        0.25,
        0.3,
        0.35,
        0.4
    ]
    DRAW_STEPS: int = 150  # total times to update cursor


class ComponentsSettings(BaseSettings):

    REGIONS = Regions()
    HSV_CONFIGS = HSVConfigs()
    IO_SERVICE = IOServiceSettings()


settings = ComponentsSettings()
