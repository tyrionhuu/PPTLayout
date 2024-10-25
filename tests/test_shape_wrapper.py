import os
import sys

import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/pptlayout/ppt_operator")
    )
)

from shape_wrappers import BaseShapeWrapper  # noqa: E402


@pytest.fixture
def sample_presentation():
    """Fixture to create a sample PowerPoint presentation with a slide and shapes."""
    # Create a sample presentation
    ppt = Presentation()

    # Add a slide with a title and content layout
    slide_layout = ppt.slide_layouts[5]  # Choosing a blank slide layout
    slide = ppt.slides.add_slide(slide_layout)

    # Add a shape to the slide (rectangle, for example)
    left = Inches(1)
    top = Inches(1)
    width = Inches(2)
    height = Inches(1)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.text = "Test Shape"

    # Add another shape (e.g., ellipse)
    ellipse = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(4), Inches(2), Inches(3), Inches(2)
    )

    return ppt, slide, shape, ellipse


def test_base_shape_wrapper(sample_presentation):
    """Test the BaseShapeWrapper class with sample shapes."""
    ppt, slide, shape, ellipse = sample_presentation

    # Create BaseShapeWrapper instances for each shape
    shape_wrapper = BaseShapeWrapper(shape)
    ellipse_wrapper = BaseShapeWrapper(ellipse)

    # Assertions for testing
    assert "AUTO_SHAPE" in shape_wrapper.shape_description
    assert "Position: left=914400, top=914400" in shape_wrapper.position_info
    assert "Size: width=1828800, height=914400" in shape_wrapper.size_info
    assert shape_wrapper.text_info is None

    assert "AUTO_SHAPE" in ellipse_wrapper.shape_description
    assert ellipse_wrapper.size_info == f"Size: width={Inches(3)}, height={Inches(2)}\n"

    print("All tests passed!")


if __name__ == "__main__":
    pytest.main()
