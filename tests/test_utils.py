import os
import sys

import pytest
from pptx import Presentation

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/pptlayout/ppt_operation")
    )
)

from utils import get_slide_size  # noqa: E402

PPTX_PATH = os.path.join(os.path.dirname(__file__), "./data/test.pptx")


@pytest.fixture
def load_presentation():
    """Fixture to load the presentation."""
    ppt = Presentation(PPTX_PATH)
    return ppt


def test_get_slide_size(load_presentation):
    """Test get_slide_size function."""
    width, height = get_slide_size(load_presentation)
    assert width == 12192000
    assert height == 6858000
