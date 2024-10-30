import json
import os
import re
from collections import Counter

import pandas as pd
import torch
from pptx.enum.dml import MSO_FILL
from scipy.optimize import linear_sum_assignment


def get_fill_color(shape) -> str:
    if shape.fill.type == MSO_FILL.SOLID:
        color = shape.fill.fore_color
        if hasattr(color, "rgb"):
            return color.rgb
    return ""


def get_slide_size(presentation) -> tuple:
    return presentation.slide_width, presentation.slide_height


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
    "pptlayout": {
        0: "preset",
        1: "freeform",
        2: "text",
        3: "picture",
        4: "line",
        5: "chart",
        6: "table",
        7: "other",
    },
}

LABEL2ID_PPT = {
    "preset": 0,
    "freeform": 1,
    "text": 2,
    "picture": 3,
    "line": 4,
    "chart": 5,
    "table": 6,
    "other": 7,
}

DEFAULT_SIZE = (6868000, 12192000)


def canvas_size(domain: str, pptx_path=None) -> tuple:
    if domain == "rico":
        return 90, 160
    if domain == "publaynet":
        return 120, 160
    if domain == "posterlayout":
        return 102, 150
    if domain == "webui":
        return 120, 120
    if domain == "pptlayout":
        if pptx_path is not None:
            if not os.path.exists(pptx_path):
                raise FileNotFoundError(f"{pptx_path} not found")
            else:
                return get_slide_size(pptx_path)
        else:
            return DEFAULT_SIZE
    else:
        raise ValueError(f"Invalid domain: {domain}")


def raw_data_path(x):
    return os.path.join(os.path.dirname(__file__), f"../dataset/{x}/raw")


LAYOUT_DOMAIN = {
    "rico": "android",
    "publaynet": "document",
    "posterlayout": "poster",
    "webui": "web",
    "pptlayout": "ppt",
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
        return torch.load(f, weights_only=True)


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


# convert dataset.txt to dataset.json
def powerpoint_dataset_json_converter(
    dir_path: str, input_file: str, output_file: str
) -> list[dict]:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"{dir_path} not found")

    input_file = os.path.join(dir_path, input_file)
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found")

    output_file = os.path.join(dir_path, output_file)

    df = pd.read_csv(input_file, sep=r"\s+")

    def parse_float_string_list(string: str) -> list[float]:
        return [float(x) for x in string.split(",")]

    def parse_int_string_list(string: str) -> list[int]:
        return [int(x) for x in string.split(",")]

    grouped_data = (
        df.groupby("slide_id")
        .apply(lambda x: x.to_dict(orient="records"), include_groups=False)
        .to_dict()
    )

    data_by_slide = []
    for slide_id, slide_data in grouped_data.items():

        data_by_slide.append(
            {
                "slide_id": slide_id,
                "elements": [
                    {
                        "labels": LABEL2ID_PPT[d["element_type"]],
                        "bounding_boxes": [
                            num / 100 for num in parse_float_string_list(d["position"])
                        ],
                        "depth": int(d["z-index"]),
                        "rotation": float(d["rotation"]),
                        "text_alignment": parse_int_string_list(d["alignment"]),
                    }
                    for d in slide_data
                ],
            }
        )

    json.dump(data_by_slide, open(output_file, "w"))
    return data_by_slide


def normalize_weights(*args):
    total = sum(args)
    return [arg / total for arg in args]


def intersection(data_1, data_2):
    cnt = 0
    x = Counter(data_1)
    y = Counter(data_2)
    for k in x:
        if k in y:
            cnt += 2 * min(x[k], y[k])
    return cnt


def union(labels_1, labels_2):
    return len(labels_1) + len(labels_2)


def tensor_similarity(labels_1, labels_2):
    if isinstance(labels_1, torch.Tensor):
        labels_1 = labels_1.tolist()
    if isinstance(labels_2, torch.Tensor):
        labels_2 = labels_2.tolist()
    return intersection(labels_1, labels_2) / union(labels_1, labels_2)


def bounding_boxes_similarity(
    labels_1, bounding_boxes_1, labels_2, bounding_boxes_2, times=2
):
    """
    bounding_boxes_1: M x 4
    bounding_boxes_2: N x 4
    distance: M x N
    """
    distance = torch.cdist(bounding_boxes_1, bounding_boxes_2) * times
    distance = torch.pow(0.5, distance)
    mask = labels_1.unsqueeze(-1) == labels_2.unsqueeze(0)
    distance = distance * mask
    row_ind, col_ind = linear_sum_assignment(-distance)
    return distance[row_ind, col_ind].sum().item() / len(row_ind)


def labels_bounding_boxes_similarity(
    labels_1,
    bounding_boxes_1,
    labels_2,
    bounding_boxes_2,
    labels_weight,
    bounding_boxes_weight,
):
    labels_sim = tensor_similarity(labels_1, labels_2)
    bounding_boxes_sim = bounding_boxes_similarity(
        labels_1, bounding_boxes_1, labels_2, bounding_boxes_2
    )
    return labels_weight * labels_sim + bounding_boxes_weight * bounding_boxes_sim


def text_alignment_similarity(text_alignment_1, text_alignment_2):
    # TODO
    return 0
