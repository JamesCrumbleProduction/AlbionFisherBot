import numpy as np

from pydantic import BaseSettings

from .world_to_screen import Region, HSVRegion


class HSVConfigs(BaseSettings):

    BOBBER_RANGES: list[HSVRegion] = [
        HSVRegion(
            lower_range=np.array(
                [0, 6, 0], dtype=np.uint8, copy=False
            ),
            higher_range=np.array(
                [7, 219, 255], dtype=np.uint8, copy=False
            )
        ),
        HSVRegion(
            lower_range=np.array(
                [134, 100, 122], dtype=np.uint8, copy=False
            ),
            higher_range=np.array(
                [179, 154, 201], dtype=np.uint8, copy=False
            )
        ),
        HSVRegion(
            lower_range=np.array(
                [125, 109, 143], dtype=np.uint8, copy=False
            ),
            higher_range=np.array(
                [179, 255, 255], dtype=np.uint8, copy=False
            )
        )
    ]


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
    ]
    DRAW_STEPS: int = 60  # total times to update cursor


class ComponentsSettings(BaseSettings):

    REGIONS: Regions = Regions()
    HSV_CONFIGS: HSVConfigs = HSVConfigs()
    IO_SERVICE: IOServiceSettings = IOServiceSettings()


settings = ComponentsSettings()
