from pptx.slide import Slide

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
