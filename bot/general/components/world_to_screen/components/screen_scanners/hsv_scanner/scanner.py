from __future__ import annotations

import cv2
import numpy as np

from ...helpers import source_auto_update
from ....schemas import Region, HSVRegion
from ....image_grabber import grab_screen, validate_region


class HSVBobberScanner:

    __slots__ = (
        'region',
        '_image',

        '_hsv_ranges',
        '_source_kwargs',
    )

    def __init__(
        self,
        hsv_ranges: list[HSVRegion],
        region: Region = None,
    ) -> None:
        self.region = validate_region(region)
        self._image: np.ndarray = None
        self._hsv_ranges = hsv_ranges
        self._source_kwargs = dict()

    def __call__(self, /, as_custom_region: Region = None, as_custom_image: np.ndarray = None) -> HSVBobberScanner:
        if as_custom_region is not None:
            self._source_kwargs['as_custom_region'] = as_custom_region
        if as_custom_image is not None:
            self._source_kwargs['as_custom_image'] = as_custom_image
        return self

    @source_auto_update
    def count_nonzero_mask(self) -> int:
        pixel_counts: list[int] = list()

        for hsv_range in self._hsv_ranges:
            hsv_mask = cv2.inRange(
                cv2.cvtColor(self._image, cv2.COLOR_BGR2HSV),
                hsv_range.lower_range,
                hsv_range.higher_range
            )
            bitwise: np.ndarray = cv2.bitwise_and(
                self._image, self._image, mask=hsv_mask
            )
            pixels_count = np.count_nonzero(bitwise)
            pixel_counts.append(pixels_count)

        return max(pixel_counts)

    def update_source(self, **kwargs) -> None:
        self._image = grab_screen(
            self.region
            if kwargs.get('as_custom_region') is None
            else kwargs.get('as_custom_region')
        )
