import json
import os
import re

import torch
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE


def get_fill_color(shape) -> str:
    if shape.fill.type == MSO_FILL.SOLID:
        color = shape.fill.fore_color
        if hasattr(color, "rgb"):
            return color.rgb
    return ""


def get_slide_size(presentation) -> tuple:
    return presentation.slide_width, presentation.slide_height


def map_shape_type_to_label(shape_type) -> int:
    # Define the mapping from MSO shape types to integer labels
    mapping = {
        MSO_SHAPE_TYPE.AUTO_SHAPE: 1,
        MSO_SHAPE_TYPE.CALLOUT: 2,
        MSO_SHAPE_TYPE.CANVAS: 3,
        MSO_SHAPE_TYPE.CHART: 4,
        MSO_SHAPE_TYPE.COMMENT: 5,
        MSO_SHAPE_TYPE.DIAGRAM: 6,
        MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT: 7,
        MSO_SHAPE_TYPE.FORM_CONTROL: 8,
        MSO_SHAPE_TYPE.FREEFORM: 9,
        MSO_SHAPE_TYPE.GROUP: 10,
        MSO_SHAPE_TYPE.IGX_GRAPHIC: 11,
        MSO_SHAPE_TYPE.INK: 12,
        MSO_SHAPE_TYPE.INK_COMMENT: 13,
        MSO_SHAPE_TYPE.LINE: 14,
        MSO_SHAPE_TYPE.LINKED_OLE_OBJECT: 15,
        MSO_SHAPE_TYPE.LINKED_PICTURE: 16,
        MSO_SHAPE_TYPE.MEDIA: 17,
        MSO_SHAPE_TYPE.OLE_CONTROL_OBJECT: 18,
        MSO_SHAPE_TYPE.PICTURE: 19,
        MSO_SHAPE_TYPE.PLACEHOLDER: 20,
        MSO_SHAPE_TYPE.SCRIPT_ANCHOR: 21,
        MSO_SHAPE_TYPE.TABLE: 22,
        MSO_SHAPE_TYPE.TEXT_BOX: 23,
        MSO_SHAPE_TYPE.TEXT_EFFECT: 24,
        MSO_SHAPE_TYPE.WEB_VIDEO: 25,
        MSO_SHAPE_TYPE.MIXED: 26,  # If you have mixed types
    }
    return mapping.get(shape_type, 0)  # Default to 0 if shape type is not found


ID2LABEL = {
    "publaynet": {1: "text", 2: "title", 3: "list", 4: "table", 5: "figure"},
    "rico": {
        1: "text",
        2: "image",
        3: "icon",
        4: "list item",
        5: "text button",
        6: "toolbar",
        7: "web view",
        8: "input",
        9: "card",
        10: "advertisement",
        11: "background image",
        12: "drawer",
        13: "radio button",
        14: "checkbox",
        15: "multi-tab",
        16: "pager indicator",
        17: "modal",
        18: "on/off switch",
        19: "slider",
        20: "map view",
        21: "button bar",
        22: "video",
        23: "bottom navigation",
        24: "number stepper",
        25: "date picker",
    },
    "posterlayout": {1: "text", 2: "logo", 3: "underlay"},
    "webui": {
        0: "text",
        1: "link",
        2: "button",
        3: "title",
        4: "description",
        5: "image",
        6: "background",
        7: "logo",
        8: "icon",
        9: "input",
    },
}


CANVAS_SIZE = {
    "rico": (90, 160),
    "publaynet": (120, 160),
    "posterlayout": (102, 150),
    "webui": (120, 120),
}


def raw_data_path(x):
    return os.path.join(os.path.dirname(__file__), f"../dataset/{x}/raw")


LAYOUT_DOMAIN = {
    "rico": "android",
    "publaynet": "document",
    "posterlayout": "poster",
    "webui": "web",
}


def clean_text(text: str, remove_summary: bool = False):
    if remove_summary:
        text = re.sub(r"#.*?#", "", text)
    text = text.replace("[#]", " ")
    text = text.replace("#", " ")
    text = text.replace("\n", " ")
    text = text.replace(",", ", ")
    text = text.replace(".", ". ").strip()
    text = re.sub(r"[ ]+", " ", text)
    return text


def read_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def read_pt(filename):
    with open(filename, "rb") as f:
        return torch.load(f)


def write_pt(filename, obj):
    with open(filename, "wb") as f:
        torch.save(obj, f)


def decapulate(bounding_box):
    if len(bounding_box.size()) == 2:
        x1, y1, x2, y2 = bounding_box.T
    else:
        x1, y1, x2, y2 = bounding_box.permute(2, 0, 1)
    return x1, y1, x2, y2


def detect_size_relation(b1, b2):
    REL_SIZE_ALPHA = 0.1
    a1, a2 = b1[2] * b1[3], b2[2] * b2[3]
    a1_sm = (1 - REL_SIZE_ALPHA) * a1
    a1_lg = (1 + REL_SIZE_ALPHA) * a1

    if a2 <= a1_sm:
        return "smaller"

    if a1_sm < a2 and a2 < a1_lg:
        return "equal"

    if a1_lg <= a2:
        return "larger"

    raise RuntimeError(b1, b2)


def detect_location_relation(b1, b2, canvas=False):
    if canvas:
        yc = b2[1] + b2[3] / 2
        y_sm, y_lg = 1.0 / 3, 2.0 / 3

        if yc <= y_sm:
            return "top"

        if y_sm < yc and yc < y_lg:
            return "center"

        if y_lg <= yc:
            return "bottom"

    else:
        l1, t1, r1, b1 = convert_ltwh_to_ltrb(b1)
        l2, t2, r2, b2 = convert_ltwh_to_ltrb(b2)

        if b2 <= t1:
            return "top"

        if b1 <= t2:
            return "bottom"

        if t1 < b2 and t2 < b1:
            if r2 <= l1:
                return "left"

            if r1 <= l2:
                return "right"

            if l1 < r2 and l2 < r1:
                return "center"

    raise RuntimeError(b1, b2, canvas)


def convert_ltwh_to_ltrb(bounding_box):
    if len(bounding_box.size()) == 1:
        left, top, width, height = bounding_box
        right = left + width
        bottom = top + height
        return left, top, right, bottom
    left, top, width, height = decapulate(bounding_box)
    right = left + width
    bottom = top + height
    return torch.stack([left, top, right, bottom], axis=-1)
