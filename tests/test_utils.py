import os
import sys

import pytest
from pptx import Presentation

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/pptlayout/input"))
)

from utils import get_slide_size, powerpoint_dataset_json_converter  # noqa: E402

PPTX_PATH = os.path.join(os.path.dirname(__file__), "./data/test.pptx")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "./data/dataset.txt")


@pytest.fixture
def load_presentation():
    """Fixture to load the presentation."""
    ppt = Presentation(PPTX_PATH)
    return ppt


@pytest.fixture
def file_path():
    """Fixture to get the file path."""
    return PPTX_PATH, DATASET_PATH


def test_get_slide_size(load_presentation):
    """Test get_slide_size function."""
    width, height = get_slide_size(load_presentation)
    assert width == 12192000
    assert height == 6858000


def test_convert_dataset(file_path, output_path):
    """Test powerpoint_dataset_json_converter function."""
    powerpoint_dataset_json_converter(file_path[0], file_path[1])
    assert os.path.exists("dataset.json")
