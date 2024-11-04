from typing import TypeAlias, Union

from pptx.shapes.autoshape import Shape as AutoShape
from pptx.shapes.base import BaseShape
from pptx.shapes.connector import Connector
from pptx.shapes.graphfrm import GraphicFrame
from pptx.shapes.group import GroupShape
from pptx.shapes.picture import Picture
from pptx.shapes.placeholder import BasePlaceholder

from pptlayout.utils import DEFAULT_EXTRACTOR, SHAPE_EXTRACTOR_MAP

from .shape_extractors import (
    AutoShapeExtractor,
    BaseShapeExtractor,
    ConnectorExtractor,
    FreeformExtractor,
    GroupShapeExtractor,
    PictureExtractor,
    PlaceholderExtractor,
)

ShapeExtractor: TypeAlias = Union[
    BaseShapeExtractor,
    AutoShapeExtractor,
    ConnectorExtractor,
    FreeformExtractor,
    GroupShapeExtractor,
    PictureExtractor,
    PlaceholderExtractor,
]

Shape: TypeAlias = Union[
    BaseShape,
    AutoShape,
    Connector,
    GraphicFrame,
    GroupShape,
    Picture,
    BasePlaceholder,
]


def shape_extractor_factory(shape: Shape) -> ShapeExtractor:
    """Factory function to create a shape extractor based on the shape type."""
    shape_type = shape.shape_type
    extractor = SHAPE_EXTRACTOR_MAP.get(shape_type, DEFAULT_EXTRACTOR)
    return extractor(shape)
