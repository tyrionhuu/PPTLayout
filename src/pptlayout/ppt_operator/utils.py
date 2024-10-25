from pptx.enum.dml import MSO_FILL


def get_fill_color(shape) -> str:
    if shape.fill.type == MSO_FILL.SOLID:
        color = shape.fill.fore_color
        if hasattr(color, "rgb"):
            return color.rgb
    return ""
