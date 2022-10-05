from __future__ import annotations

import cv2
import numpy as np

from ...helpers import source_auto_update
from ....structure import Region
from ....image_grabber import grab_screen, validate_region


class HSVBobberScanner:

    __slots__ = (
        'region',
        '_image',
        '_hsv_mask',

        '_source_kwargs',
        '_lower_range_hsv_array',
        '_higher_range_hsv_array',
    )

    def __init__(
        self,
        lower_range_hsv_array: np.ndarray,
        higher_range_hsv_array: np.ndarray,
        region: Region = None,
    ) -> None:
        self.region = validate_region(region)
        self._image: np.ndarray = None
        self._hsv_mask: np.ndarray = None

        self._lower_range_hsv_array: np.ndarray = lower_range_hsv_array
        self._higher_range_hsv_array: np.ndarray = higher_range_hsv_array

        self._source_kwargs = dict()

    def __call__(self, /, as_custom_region: Region) -> HSVBobberScanner:
        self._source_kwargs['as_custom_region'] = as_custom_region
        return self

    @source_auto_update
    def get_pixels_of_bobber_mask(self) -> int:
        bitwise: np.ndarray = cv2.bitwise_and(
            self._image, self._image, mask=self._hsv_mask
        )
        pixels_count = np.count_nonzero(bitwise)
        return pixels_count

    def update_source(self, as_custom_region: Region = None) -> None:
        self._image = grab_screen(
            self.region if as_custom_region is None else as_custom_region
        )
        self._hsv_mask = cv2.inRange(
            cv2.cvtColor(self._image, cv2.COLOR_BGR2HSV),
            self._lower_range_hsv_array,
            self._higher_range_hsv_array
        )
