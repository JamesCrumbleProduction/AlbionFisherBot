from __future__ import annotations

import cv2
import numpy as np

from ...helpers import source_auto_update
from ....schemas import Image, Region, HSVRegion
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
        self._image: Image = None
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
        max_pixels_count: int = 0

        for hsv_range in self._hsv_ranges:
            hsv_mask = cv2.inRange(
                cv2.cvtColor(self._image.data, cv2.COLOR_BGR2HSV),
                hsv_range.lower_range,
                hsv_range.higher_range
            )
            bitwise: np.ndarray = cv2.bitwise_and(
                self._image.data, self._image.data, mask=hsv_mask
            )
            pixels_count = np.count_nonzero(bitwise)
            if max_pixels_count < pixels_count:
                max_pixels_count = pixels_count
        return max_pixels_count

    def update_source(self, **kwargs) -> None:
        image_region = (
            self.region if kwargs.get('as_custom_region') is None
            else kwargs.get('as_custom_region')
        )
        image_data = (
            grab_screen(image_region)
            if kwargs.get('as_custom_image') is None
            else kwargs.get('as_custom_image')
        )
        self._image = Image(
            data=image_data,
            region=image_region
        )
