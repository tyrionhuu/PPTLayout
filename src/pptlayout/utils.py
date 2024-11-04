from pptx.enum.shapes import MSO_SHAPE_TYPE

from .extractors.shape_extractors import (
    AutoShapeExtractor,
    BaseShapeExtractor,
    ConnectorExtractor,
    FreeformExtractor,
    GraphicFrameExtractor,
    GroupShapeExtractor,
    PictureExtractor,
    PlaceholderExtractor,
)

SHAPE_EXTRACTOR_MAP = {
    # Auto Shape
    MSO_SHAPE_TYPE.AUTO_SHAPE: AutoShapeExtractor,
    MSO_SHAPE_TYPE.TEXT_BOX: AutoShapeExtractor,
    MSO_SHAPE_TYPE.FREEFORM: FreeformExtractor,
    MSO_SHAPE_TYPE.PLACEHOLDER: PlaceholderExtractor,
    # Graphic Frame
    MSO_SHAPE_TYPE.CHART: GraphicFrameExtractor,
    MSO_SHAPE_TYPE.TABLE: GraphicFrameExtractor,
    MSO_SHAPE_TYPE.LINKED_OLE_OBJECT: GraphicFrameExtractor,
    MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT: GraphicFrameExtractor,
    # Picture
    MSO_SHAPE_TYPE.PICTURE: PictureExtractor,
    # Connector
    MSO_SHAPE_TYPE.LINE: ConnectorExtractor,
    # Group Shape
    MSO_SHAPE_TYPE.GROUP: GroupShapeExtractor,
}

DEFAULT_EXTRACTOR = BaseShapeExtractor
