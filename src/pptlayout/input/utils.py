from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE


def get_fill_color(shape) -> str:
    if shape.fill.type == MSO_FILL.SOLID:
        color = shape.fill.fore_color
        if hasattr(color, "rgb"):
            return color.rgb
    return ""


def get_slide_size(presentation) -> tuple:
    return presentation.slide_width, presentation.slide_height


def map_shape_type_to_label(shape_type) -> int:
    # Define the mapping from MSO shape types to integer labels
    mapping = {
        MSO_SHAPE_TYPE.AUTO_SHAPE: 1,
        MSO_SHAPE_TYPE.CALLOUT: 2,
        MSO_SHAPE_TYPE.CANVAS: 3,
        MSO_SHAPE_TYPE.CHART: 4,
        MSO_SHAPE_TYPE.COMMENT: 5,
        MSO_SHAPE_TYPE.DIAGRAM: 6,
        MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT: 7,
        MSO_SHAPE_TYPE.FORM_CONTROL: 8,
        MSO_SHAPE_TYPE.FREEFORM: 9,
        MSO_SHAPE_TYPE.GROUP: 10,
        MSO_SHAPE_TYPE.IGX_GRAPHIC: 11,
        MSO_SHAPE_TYPE.INK: 12,
        MSO_SHAPE_TYPE.INK_COMMENT: 13,
        MSO_SHAPE_TYPE.LINE: 14,
        MSO_SHAPE_TYPE.LINKED_OLE_OBJECT: 15,
        MSO_SHAPE_TYPE.LINKED_PICTURE: 16,
        MSO_SHAPE_TYPE.MEDIA: 17,
        MSO_SHAPE_TYPE.OLE_CONTROL_OBJECT: 18,
        MSO_SHAPE_TYPE.PICTURE: 19,
        MSO_SHAPE_TYPE.PLACEHOLDER: 20,
        MSO_SHAPE_TYPE.SCRIPT_ANCHOR: 21,
        MSO_SHAPE_TYPE.TABLE: 22,
        MSO_SHAPE_TYPE.TEXT_BOX: 23,
        MSO_SHAPE_TYPE.TEXT_EFFECT: 24,
        MSO_SHAPE_TYPE.WEB_VIDEO: 25,
        MSO_SHAPE_TYPE.MIXED: 26,  # If you have mixed types
    }
    return mapping.get(shape_type, 0)  # Default to 0 if shape type is not found


"""
A tensor or list of bounding boxes, typically represented as a 2D array where each row corresponds to a bounding box in the format [x1, y1, x2, y2].
This denotes the coordinates of the top-left and bottom-right corners of the box.
"""


def generate_bounding_box(left: int, top: int, width: int, height: int) -> list:
    return [left, top, left + width, top + height]
