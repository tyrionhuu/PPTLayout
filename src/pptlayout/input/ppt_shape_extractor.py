from utils import convert_ltwh_to_ltrb, get_slide_size, map_shape_type_to_label


class SlideShapeExtractor:
    """
    Extract the shapes from a slide in a presentation to a csv file, which is formatted as follows:
    Slide Number, Shape Type, Shape Index, Left Position, Top Position, Width, Height, Fill color
    """

    def __init__(self, slide, slide_number: int):
        self.slide = slide
        self.slide_number = slide_number
        self.shapes = self._extract_shapes()

    # return a list of shape classes
    def _extract_shapes(self) -> list:
        shapes = []
        for shape in self.slide.shapes:
            shapes.append(shape)
        return shapes

    def shapes_to_list(self) -> list:
        shapes = []
        for i, shape in enumerate(self.shapes):
            slide_number = self.slide_number

            try:
                shape_type = str(shape.shape_type)
            except AttributeError:
                shape_type = ""

            try:
                shape_index = shape.shape_id
            except AttributeError:
                shape_index = ""

            try:
                left_position = shape.left
            except AttributeError as e:
                print(f"Error: {e}")

            try:
                top_position = shape.top
            except AttributeError as e:
                print(f"Error: {e}")

            try:
                width = shape.width
            except AttributeError as e:
                print(f"Error: {e}")

            try:
                height = shape.height
            except AttributeError as e:
                print(f"Error: {e}")

            shapes.append(
                [
                    slide_number,
                    shape_type,
                    shape_index,
                    left_position,
                    top_position,
                    width,
                    height,
                ]
            )
        return [shapes]


class InputFormatter:
    def __init__(self, data):
        self.label = map_shape_type_to_label(data[1])
        # self.label = str(data[1])
        self.bounding_box = convert_ltwh_to_ltrb([data[3], data[4], data[5], data[6]])


HEADER = [
    "Slide Number",
    "Shape Type",
    "Shape Index",
    "Left Position",
    "Top Position",
    "Width",
    "Height",
]


class PowerPointShapeExtractor:
    """
    Extract the shapes from a PowerPoint presentation to a csv file, which is formatted as follows:
    Slide Number, Shape Type, Shape Index, Left Position, Top Position, Width, Height, Fill color
    """

    def __init__(self, presentation):
        self.presentation = presentation
        self.slides = self.presentation.slides
        self.width, self.height = get_slide_size(self.presentation)

    # return [[shape1, shape2, ...], [shape1, shape2, ...], ...]
    def extract_shapes(self) -> list:
        slides = []
        for i, slide in enumerate(self.slides):
            slide_shapes = []
            slide_extractor = SlideShapeExtractor(slide, i)
            slide_shapes = slide_extractor.shapes_to_list()
            slides.extend(slide_shapes)
        return slides
