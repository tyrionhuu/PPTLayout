import os
import sys

import pytest
from pptx import Presentation

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/pptlayout/input"))
)

from ppt_shape_extractor import PowerPointShapeExtractor  # noqa: E402

PPTX_PATH = os.path.join(os.path.dirname(__file__), "./data/test.pptx")
ABSOLUTE_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def load_presentation():
    """Fixture to load the presentation."""
    ppt = Presentation(PPTX_PATH)
    return ppt


def test_powerpoint_shape_extractor(load_presentation):
    ppt = load_presentation
    extractor = PowerPointShapeExtractor(ppt)
    shapes = extractor.extract_shapes()
    for slide in shapes:
        print(slide)
