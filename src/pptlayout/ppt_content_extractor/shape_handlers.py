from pptx.shapes.base import BaseShape


class BaseShapeHandler:
    def __init__(self, shape: BaseShape):
        self._shape = shape
        self._shape_type = shape.shape_type
        self._shape_id = shape.shape_id
        self._shape_name = shape.name
        self._height = shape.height
        self._width = shape.width
        self._left = shape.left
        self._top = shape.top

    @property
    def shape_type(self):
        return self._shape_type

    @property
    def shape_id(self):
        return self._shape_id

    @property
    def shape_name(self):
        return self._shape_name

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def left(self):
        return self._left

    @property
    def top(self):
        return self._top
