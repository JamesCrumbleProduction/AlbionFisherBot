import numpy as np

from pydantic import BaseModel, ValidationError


class ValidatedTemplateData(BaseModel):
    location_x: np.ndarray
    location_y: np.ndarray
    height: int
    width: int

    class Config:
        arbitrary_types_allowed = 'allow'


class Region(BaseModel):
    width: int
    height: int
    left: int
    top: int


class HSVRegion(BaseModel):

    lower_range: np.ndarray
    higher_range: np.ndarray

    class Config:
        arbitrary_types_allowed = 'allow'

    def validate_range(cls, value: np.ndarray):
        if len(value) != 3:
            raise ValidationError(
                ['length of hsv range should be exactly 3 elements'], cls
            )

        if 0 >= value[0] >= 179:
            raise ValidationError(
                ['H value should be in 0-179 range'], cls
            )

        if 0 >= value[1] >= 255 or 0 >= value[2] >= 255:
            raise ValidationError(
                ['S and V values should be in 0-255 range'], cls
            )

        return value


class Coordinate(BaseModel):
    x: int
    y: int

    region: Region = None

    def tuple_format(self) -> tuple[int, int]:
        return self.x, self.y


class Image(BaseModel):

    data: np.ndarray
    region: Region

    class Config:
        arbitrary_types_allowed = 'allow'
