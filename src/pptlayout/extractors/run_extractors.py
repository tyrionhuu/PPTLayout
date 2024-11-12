import os

from pptx import Presentation

from .ppt_extractor import PowerPointShapeExtractor

# Replace with your actual PPTX file path
# pptx_path = "/data/tianyuhu/PPTLayout/data/pptx/ZK7FNUZ33GBBCG7CFVYS56TQCTD72CJR.pptx"


# ppt = Presentation(pptx_path)
# shape_extractor = PowerPointShapeExtractor(ppt)
# extracted_info = shape_extractor.extract_ppt()
# print(dumps(extracted_info, indent=4))
def run_extractors(pptx_path: str) -> dict:
    if not pptx_path:
        raise ValueError("pptx_path is required")
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"File not found: {pptx_path}")
    ppt = Presentation(pptx_path)
    shape_extractor = PowerPointShapeExtractor(ppt)
    extracted_info = shape_extractor.extract_ppt()
    return extracted_info
