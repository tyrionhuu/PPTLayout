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
    print(df.head())
    grouped_data = (
        df.groupby("slide_id")
        .apply(lambda x: x.to_dict(orient="records"), include_groups=False)
        .to_dict()
    )

    def parse_float_string_list(string: str) -> list[float]:
        return [float(x) for x in string.split(",")]

    def parse_int_string_list(string: str) -> list[int]:
        return [int(x) for x in string.split(",")]

    def get_bounding_box_lists(data: list[dict]) -> torch.Tensor:
        original_lists = [d["position"] for d in data]
        float_lists = [parse_float_string_list(d) for d in original_lists]
        normalized_lists = []
        for list in float_lists:
            normalized_lists.append([d / 100 for d in list])
        return torch.tensor(normalized_lists)

    def get_labels_list(data: list[dict]) -> torch.Tensor:
        original_list = [d["element_type"] for d in data]
        id_list = [LABEL2ID_PPT[d] for d in original_list]
        return torch.tensor(id_list)

    def get_depth_list(data: list[dict]) -> torch.Tensor:
        original_list = [d["z-index"] for d in data]
        int_list = [int(d) for d in original_list]
        return torch.tensor(int_list)

    def get_rotation_list(data: list[dict]) -> torch.Tensor:
        original_list = [d["rotation"] for d in data]
        float_list = [float(d) for d in original_list]
        return torch.tensor(float_list)

    def get_alignment_lists(data: list[dict]) -> torch.Tensor:
        original_lists = [d["alignment"] for d in data]
        int_lists = [parse_int_string_list(d) for d in original_lists]
        return torch.tensor(int_lists)

    data_by_slide = []
    for slide_id, data in grouped_data.items():
        data_by_slide.append(
            {
                "slide_id": slide_id,
                "bounding_boxes": get_bounding_box_lists(data),
                "labels": get_labels_list(data),
                "depth": get_depth_list(data),
                "rotation": get_rotation_list(data),
                "text_alignment": get_alignment_lists(data),
            }
        )
    # print(data_by_slide)
    write_pt(output_file, data_by_slide)
    return data_by_slide


def normalize_weights(*args):
    total = sum(args)
    return [arg / total for arg in args]


def labels_similarity(labels_1, labels_2):
    def _intersection(labels_1, labels_2):
        cnt = 0
        x = Counter(labels_1)
        y = Counter(labels_2)
        for k in x:
            if k in y:
                cnt += 2 * min(x[k], y[k])
        return cnt

    def _union(labels_1, labels_2):
        return len(labels_1) + len(labels_2)

    if isinstance(labels_1, torch.Tensor):
        labels_1 = labels_1.tolist()
    if isinstance(labels_2, torch.Tensor):
        labels_2 = labels_2.tolist()
    return _intersection(labels_1, labels_2) / _union(labels_1, labels_2)


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
    labels_sim = labels_similarity(labels_1, labels_2)
    bounding_boxes_sim = bounding_boxes_similarity(
        labels_1, bounding_boxes_1, labels_2, bounding_boxes_2
    )
    return labels_weight * labels_sim + bounding_boxes_weight * bounding_boxes_sim


def depth_similarity(depth_1: int, depth_2: int) -> int:
    return 1 if depth_1 == depth_2 else 0


def rotation_similarity(rotation_1: float, rotation_2: float) -> float:
    return 1 - abs(rotation_1 - rotation_2) / 360


def alignment_similarity(alignment_1: list[int], alignment_2: list[int]) -> float:
    return sum(
        [1 if a1 == a2 else 0 for a1, a2 in zip(alignment_1, alignment_2)]
    ) / len(alignment_1)
