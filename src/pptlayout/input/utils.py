from pptx.enum.dml import MSO_FILL


def get_fill_color(shape) -> str:
    if shape.fill.type == MSO_FILL.SOLID:
        color = shape.fill.fore_color
        try:
            return color.rgb
        except AttributeError:
            pass
    return ""


def get_slide_size(presentation) -> tuple:
    return presentation.slide_width, presentation.slide_height
