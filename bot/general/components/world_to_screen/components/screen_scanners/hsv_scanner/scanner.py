from __future__ import annotations

import cv2

from numpy import ndarray

from ...helpers import source_auto_update
from ....structure import Region
from ....image_grabber import grab_screen, validate_region


class HSVBobberScanner:

    __slots__ = (
        'region',
        '_hsv_mask',
        '_hsv_matrix',

        '_source_kwargs',
        '_lower_range_hsv_array',
        '_higher_range_hsv_array',
    )

    def __init__(
        self,
        lower_range_hsv_array: ndarray,
        higher_range_hsv_array: ndarray,
        region: Region = None,
    ) -> None:
        self.region = validate_region(region)
        self._hsv_mask: ndarray = None
        self._hsv_matrix: ndarray = None

        self._lower_range_hsv_array: ndarray = lower_range_hsv_array
        self._higher_range_hsv_array: ndarray = higher_range_hsv_array

        self._source_kwargs = dict()

    def __call__(self, /, as_custom_region: Region) -> HSVBobberScanner:
        self._source_kwargs['as_custom_region'] = as_custom_region
        return self

    @source_auto_update
    def get_pixels_of_bobber_mask(self) -> int:
        # cv2.imwrite('test.png', cv2.bitwise_and(
        #     self._hsv_matrix, self._hsv_matrix, self._hsv_mask
        # ))

        pixels = cv2.countNonZero(self._hsv_mask)
        # cv2.imwrite('test.png', self._hsv_mask)
        return pixels

    def update_source(self, as_custom_region: Region = None) -> None:
        self._hsv_matrix = cv2.cvtColor(
            grab_screen(
                self.region if as_custom_region is None else as_custom_region
            ),
            cv2.COLOR_BGR2HSV
        )
        self._hsv_mask = cv2.inRange(
            self._hsv_matrix,
            self._lower_range_hsv_array,
            self._higher_range_hsv_array
        )
