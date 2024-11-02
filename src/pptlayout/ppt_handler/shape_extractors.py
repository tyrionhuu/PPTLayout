from typing import Union

from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.shapes.base import BaseShape
from pptx.util import Length

MEASUREMENT_UNITS_MAP = {
    "inches": Length.inches,
    "cm": Length.cm,
    "mm": Length.mm,
    "pt": Length.pt,
    "emu": Length.emu,
}


class BaseShapeExtractor:
    def __init__(self, shape: BaseShape, measurement_unit: str = "pt"):
        self._shape = shape
        self.measurement_unit = measurement_unit

    def set_measurement_unit(self, unit: str) -> None:
        self.measurement_unit = unit

    def _extract_shape_type(self) -> str:
        shape_type = self._shape.shape_type
        # Check if the shape type is a valid MSO_SHAPE_TYPE enum member
        if isinstance(shape_type, MSO_SHAPE_TYPE):
            return shape_type.name  # Returns the name of the enum member
        return str(shape_type)  # Fallback in case it's not in the enum

    def _unit_conversion(self, value: Length, unit: str) -> Union[int, float]:
        return MEASUREMENT_UNITS_MAP[unit](value)

    def _extract_height(self) -> Union[int, float]:
        return self._unit_conversion(self._shape.height, self.measurement_unit)

    def _extract_width(self) -> Union[int, float]:
        return self._unit_conversion(self._shape.width, self.measurement_unit)

    def _extract_left(self) -> Union[int, float]:
        return self._unit_conversion(self._shape.left, self.measurement_unit)

    def _extract_top(self) -> Union[int, float]:
        return self._unit_conversion(self._shape.top, self.measurement_unit)

    def extract_shape(self) -> dict:
        return {
            "name": self._shape.name,
            "shape_id": self._shape.shape_id,
            "shape_type": self._extract_shape_type(),
            "measurement_unit": self.measurement_unit,
            "height": self._extract_height(),
            "width": self._extract_width(),
            "left": self._extract_left(),
            "top": self._extract_top(),
        }
