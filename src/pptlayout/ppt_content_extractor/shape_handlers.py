from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.shapes.base import BaseShape
from pptx.util import Length


class BaseShapeHandler:
    def __init__(self, shape: BaseShape):
        self._shape = shape
        self._shape_type = shape.shape_type
        self._shape_id = shape.shape_id
        self._name = shape.name
        self._height = shape.height
        self._width = shape.width
        self._left = shape.left
        self._top = shape.top

    @property
    def shape_type(self) -> MSO_SHAPE_TYPE:
        return self._shape_type

    @property
    def shape_id(self) -> int:
        return self._shape_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def height(self) -> Length:
        return self._height

    @property
    def width(self) -> Length:
        return self._width

    @property
    def left(self) -> Length:
        return self._left

    @property
    def top(self) -> Length:
        return self._top
