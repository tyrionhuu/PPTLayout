# from pptx.slide import Slide
# from .shape_extractors import (
#     BaseShapeExtractor,
#     AutoShapeExtractor,
#     ConnectorExtractor,
#     GroupShapeExtractor,
#     PictureExtractor,
#     PlaceholderExtractor,
#     GraphicFrameExtractor,
# )
# from pptx.enum.shapes import MSO_SHAPE_TYPE

# class SlideShapeExtractor:
#     def __init__(self, slide: Slide):
#         self._slide = slide

#     def extract_shapes(self) -> list:
#         shapes = []
#         for shape in self._slide.shapes:
#             shapes.append(shape)
#         return shapes

#     def extract_shape_info(self) -> list[dict]:
#         shape_info = []
#         for shape in self._slide.shapes:
#             if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
#                 shape_extractor = AutoShapeExtractor(shape)
#             elif shape.shape_type == MSO_SHAPE_TYPE.CONNECTOR:
#                 shape_extractor = ConnectorExtractor(shape)
#             elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
#                 shape_extractor = GroupShapeExtractor(shape)
#             elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
#                 shape_extractor = PictureExtractor(shape)
#             elif shape.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER:
#                 shape_extractor = PlaceholderExtractor(shape)
#             elif shape.shape_type == MSO_SHAPE_TYPE.GRAPHIC_FRAME:
#                 shape_extractor = GraphicFrameExtractor(shape)
#             else:
#                 shape_extractor = BaseShapeExtractor(shape)
#             shape_info.append(shape_extractor.extract_shape())
#         return shape_info
