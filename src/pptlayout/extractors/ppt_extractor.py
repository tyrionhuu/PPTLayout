from pptx.presentation import Presentation
from pptx.slide import Slide

from pptlayout.utils import unit_conversion

from .factories import shape_extractor_factory


class SlideShapeExtractor:
    def __init__(self, slide: Slide):
        self._slide = slide

    def extract_slide_metadate(self) -> dict:
        return {
            "slide_id": self._slide.slide_id,
            "slide_name": self._slide.name,
        }

    def extract_shapes(self) -> list:
        shapes = []
        for shape in self._slide.shapes:
            shapes.append(self._extract_shape(shape))
        return shapes

    def _extract_shape(self, shape) -> dict:
        extractor = shape_extractor_factory(shape)
        return extractor.extract_shape()

    def extract_slide(self) -> dict:
        slide_data = self.extract_slide_metadate()
        slide_data["shapes"] = self.extract_shapes()
        return slide_data


class PowerPointShapeExtractor:
    def __init__(self, ppt: Presentation, measurement_unit: str = "pt"):
        self._ppt = ppt
        self._measurement_unit = measurement_unit

    def _extract_slide_width(self) -> int | float:
        return unit_conversion(self._ppt.slide_width, self._measurement_unit)

    def _extract_slide_height(self) -> int | float:
        return unit_conversion(self._ppt.slide_height, self._measurement_unit)

    def _extract_ppt_metadata(self) -> dict:
        return {
            "slide_width": self._extract_slide_width(),
            "slide_height": self._extract_slide_height(),
        }

    def extract_slides(self) -> list:
        slides = []
        for slide in self._ppt.slides:
            slide_extractor = SlideShapeExtractor(slide)
            slides.append(slide_extractor.extract_slide())
        return slides

    def extract_ppt(self) -> dict:
        return {
            **self._extract_ppt_metadata(),
            "slides": self.extract_slides(),
        }
