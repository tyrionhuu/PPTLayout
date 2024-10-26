import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/pptlayout/input"))
)

from utils import (  # noqa: E402
    generate_bounding_box,
    get_fill_color,
    get_slide_size,
    map_shape_type_to_label,
)


class SlideShapeExtractor:
    """
    Extract the shapes from a slide in a presentation to a csv file, which is formatted as follows:
    Slide Number, Shape Type, Shape Index, Left Position, Top Position, Width, Height, Fill color
    """

    def __init__(self, slide, slide_number: int):
        self.slide = slide
        self.slide_number = slide_number
        self.shapes = self._extract_shapes()

    def _extract_shapes(self) -> list:
        shapes = []
        for shape in self.slide.shapes:
            shapes.append(shape)
        return shapes

    def extract_shapes(self):
        for i, shape in enumerate(self.shapes):
            slide_number = self.slide_number

            try:
                shape_type = shape.shape_type
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

            if hasattr(shape, "fill"):
                fill_color = get_fill_color(shape)
            else:
                fill_color = ""

            yield (
                slide_number,
                shape_type,
                shape_index,
                left_position,
                top_position,
                width,
                height,
                fill_color,
            )


class InputFormatter:
    def __init__(self, data):
        self.label = map_shape_type_to_label(data[1])
        self.bounding_box = generate_bounding_box(data[3], data[4], data[5], data[6])


class PowerPointShapeExtractor:
    """
    Extract the shapes from a PowerPoint presentation to a csv file, which is formatted as follows:
    Slide Number, Shape Type, Shape Index, Left Position, Top Position, Width, Height, Fill color
    """

    def __init__(self, presentation):
        self.presentation = presentation
        self.slides = self._extract_slides()
        self.width, self.height = get_slide_size(self.presentation)

    def _extract_slides(self) -> list:
        slides = []
        for i, slide in enumerate(self.presentation.slides):
            slides.append(SlideShapeExtractor(slide, i + 1))
        return slides

    def extract_shapes_to_csv(self, output_dir: str, output_file: str = "shapes.csv"):
        output_file = os.path.join(output_dir, output_file)
        if not os.path.exists(output_dir):
            print(f"Creating directory: {output_dir}")
            os.makedirs(output_dir)
        with open(output_file, "w") as f:
            f.write(
                "Slide Number, Shape Type, Shape Index, Left Position, Top Position, Width, Height, Fill color\n"
            )
            for slide in self.slides:
                shapes = slide.extract_shapes()
                for shape in shapes:
                    f.write(",".join(map(str, shape)) + "\n")
