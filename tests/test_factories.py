from unittest.mock import Mock

import pytest

from src.pptlayout.extractors.factories import (
    DEFAULT_EXTRACTOR,
    SHAPE_EXTRACTOR_MAP,
    shape_extractor_factory,
)


@pytest.mark.parametrize("shape_type, expected_extractor", SHAPE_EXTRACTOR_MAP.items())
def test_shape_extractor_factory(shape_type, expected_extractor):
    """Test to check the shape extractor factory."""
    # Create a mock shape object
    shape = Mock()
    shape.shape_type = shape_type

    # Get the shape extractor
    shape_extractor = shape_extractor_factory(shape)

    # Assert that the shape extractor is of the expected type
    assert isinstance(shape_extractor, expected_extractor)


def test_shape_extractor_factory_default():
    """Test to check the shape extractor factory with default extractor."""
    # Create a mock shape object
    shape = Mock()
    shape.shape_type = "UNKNOWN"

    # Get the shape extractor
    shape_extractor = shape_extractor_factory(shape)

    # Assert that the shape extractor is of the default type
    assert isinstance(shape_extractor, DEFAULT_EXTRACTOR)
