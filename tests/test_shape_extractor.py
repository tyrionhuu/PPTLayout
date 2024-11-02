import pytest
from pptx import Presentation

from src.pptlayout.ppt_handler.shape_extractors import (
    BaseShapeExtractor,  # Adjust import as needed
)

PPTX_PATH = "./data/pptx/ZK7FNUZ33GBBCG7CFVYS56TQCTD72CJR.pptx"


@pytest.fixture
def sample_shape():
    # Load the presentation and get the first slide and its first shape
    presentation = Presentation(PPTX_PATH)
    slide = presentation.slides[0]
    shape = slide.shapes[0]  # Assumes there's at least one shape
    return shape


@pytest.fixture
def shape_extractor(sample_shape):
    return BaseShapeExtractor(shape=sample_shape, measurement_unit="emu")


def test_set_measurement_unit(shape_extractor):
    shape_extractor.set_measurement_unit("cm")
    assert (
        shape_extractor.measurement_unit == "cm"
    ), "Measurement unit should be 'cm' after setting."


def test_extract_shape(shape_extractor):
    shape_info = shape_extractor.extract_shape()
    print(shape_info)
    assert isinstance(shape_info, dict), "Output should be a dictionary."
    assert "name" in shape_info, "Shape info should contain 'name' key."
    assert "shape_id" in shape_info, "Shape info should contain 'shape_id' key."
    assert "shape_type" in shape_info, "Shape info should contain 'shape_type' key."
    assert (
        "measurement_unit" in shape_info
    ), "Shape info should contain 'measurement_unit' key."
    assert "height" in shape_info, "Shape info should contain 'height' key."
    assert "width" in shape_info, "Shape info should contain 'width' key."
    assert "left" in shape_info, "Shape info should contain 'left' key."
    assert "top" in shape_info, "Shape info should contain 'top' key."
