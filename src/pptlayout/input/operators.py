import copy
import math
import random
from itertools import combinations, product

import clip
import cv2
import numpy as np
import torch
from utils import decapulate, detect_location_relation, detect_size_relation


class ShuffleElements:
    def __call__(self, data):
        if "gold_bounding_boxes" not in data.keys():
            data["gold_bounding_boxes"] = copy.deepcopy(data["bounding_boxes"])

        element_number = len(data["labels"])
        shuffle_index = np.arange(element_number)
        random.shuffle(shuffle_index)
        data["bounding_boxes"] = data["bounding_boxes"][shuffle_index]
        data["gold_bounding_boxes"] = data["gold_bounding_boxes"][shuffle_index]
        data["labels"] = data["labels"][shuffle_index]
        return data


class LabelDictSort:
    """
    sort elements in one layout by their label
    """

    def __init__(self, index2label=None):
        self.index2label = index2label

    def __call__(self, data):
        # NOTE: for refinement
        if "gold_bounding_boxes" not in data.keys():
            data["gold_bounding_boxes"] = copy.deepcopy(data["bounding_boxes"])

        labels = data["labels"].tolist()
        index2label = [
            [index, self.index2label[labels[index]]] for index in range(len(labels))
        ]
        index2label_sorted = sorted(index2label, key=lambda x: x[1])
        index_sorted = [d[0] for d in index2label_sorted]
        data["bounding_boxes"], data["labels"] = (
            data["bounding_boxes"][index_sorted],
            data["labels"][index_sorted],
        )
        data["gold_bounding_boxes"] = data["gold_bounding_boxes"][index_sorted]
        return data


class LexicographicSort:
    """
    sort elements in one layout by their top and left postion
    """

    def __call__(self, data):
        if "gold_bounding_boxes" not in data.keys():
            data["gold_bounding_boxes"] = copy.deepcopy(data["bounding_boxes"])
        l, t, _, _ = data["bounding_boxes"].t()
        _zip = zip(*sorted(enumerate(zip(t, l)), key=lambda c: c[1:]))
        index = list(list(_zip)[0])
        data["original_bounding_boxes"], data["original_labels"] = (
            data["gold_bounding_boxes"],
            data["labels"],
        )
        data["bounding_boxes"], data["labels"] = (
            data["bounding_boxes"][index],
            data["labels"][index],
        )
        data["gold_bounding_boxes"] = data["gold_bounding_boxes"][index]
        return data


class AddGaussianNoise:
    """
    Add Gaussian Noise to bounding box
    """

    def __init__(
        self, mean=0.0, std=1.0, normalized: bool = True, bernoulli_beta: float = 1.0
    ):
        self.std = std
        self.mean = mean
        self.normalized = normalized
        # adding noise to every element by default
        self.bernoulli_beta = bernoulli_beta
        print(
            "Noise: mean={0}, std={1}, beta={2}".format(
                self.mean, self.std, self.bernoulli_beta
            )
        )

    def __call__(self, data):
        # Gold Label
        if "gold_bounding_boxes" not in data.keys():
            data["gold_bounding_boxes"] = copy.deepcopy(data["bounding_boxes"])

        num_elements = data["bounding_boxes"].size(0)
        beta = data["bounding_boxes"].new_ones(num_elements) * self.bernoulli_beta
        element_with_noise = torch.bernoulli(beta).unsqueeze(dim=-1)

        if self.normalized:
            data["bounding_boxes"] = (
                data["bounding_boxes"]
                + torch.randn(data["bounding_boxes"].size()) * self.std
                + self.mean
            )
        else:
            canvas_width, canvas_height = data["canvas_size"][0], data["canvas_size"][1]
            ele_x, ele_y = (
                data["bounding_boxes"][:, 0] * canvas_width,
                data["bounding_boxes"][:, 1] * canvas_height,
            )
            ele_w, ele_h = (
                data["bounding_boxes"][:, 2] * canvas_width,
                data["bounding_boxes"][:, 3] * canvas_height,
            )
            data["bounding_boxes"] = torch.stack([ele_x, ele_y, ele_w, ele_h], dim=1)
            data["bounding_boxes"] = (
                data["bounding_boxes"]
                + torch.randn(data["bounding_boxes"].size()) * self.std
                + self.mean
            )
            data["bounding_boxes"][:, 0] /= canvas_width
            data["bounding_boxes"][:, 1] /= canvas_height
            data["bounding_boxes"][:, 2] /= canvas_width
            data["bounding_boxes"][:, 3] /= canvas_height
        data["bounding_boxes"][data["bounding_boxes"] < 0] = 0.0
        data["bounding_boxes"][data["bounding_boxes"] > 1] = 1.0
        data["bounding_boxes"] = data["bounding_boxes"] * element_with_noise + data[
            "gold_bounding_boxes"
        ] * (1 - element_with_noise)
        return data

    def __repr__(self):
        return self.__class__.__name__ + "(mean={0}, std={1}, beta={2})".format(
            self.mean, self.std, self.bernoulli_beta
        )


class DiscretizeBoundingBox:
    def __init__(self, num_x_grid: int, num_y_grid: int) -> None:
        self.num_x_grid = num_x_grid
        self.num_y_grid = num_y_grid
        self.max_x = self.num_x_grid
        self.max_y = self.num_y_grid

    def discretize(self, bounding_box):
        """
        Args:
            continuous_bounding_box torch.Tensor: N * 4
        Returns:
            discrete_bounding_box torch.LongTensor: N * 4
        """
        clipped_boxes = torch.clip(bounding_box, min=0.0, max=1.0)
        x1, y1, x2, y2 = decapulate(clipped_boxes)
        discrete_x1 = torch.floor(x1 * self.max_x)
        discrete_y1 = torch.floor(y1 * self.max_y)
        discrete_x2 = torch.floor(x2 * self.max_x)
        discrete_y2 = torch.floor(y2 * self.max_y)
        return torch.stack(
            [discrete_x1, discrete_y1, discrete_x2, discrete_y2], dim=-1
        ).long()

    def continuize(self, bounding_box):
        """
        Args:
            discrete_bounding_box torch.LongTensor: N * 4

        Returns:
            continuous_bounding_box torch.Tensor: N * 4
        """
        x1, y1, x2, y2 = decapulate(bounding_box)
        cx1, cx2 = x1 / self.max_x, x2 / self.max_x
        cy1, cy2 = y1 / self.max_y, y2 / self.max_y
        return torch.stack([cx1, cy1, cx2, cy2], dim=-1).float()

    def continuize_num(self, num: int) -> float:
        return num / self.max_x

    def discretize_num(self, num: float) -> int:
        return int(math.floor(num * self.max_y))

    def __call__(self, data):
        if "gold_bounding_boxes" not in data.keys():
            data["gold_bounding_boxes"] = copy.deepcopy(data["bounding_boxes"])
        data["discrete_bounding_boxes"] = self.discretize(data["bounding_boxes"])
        data["discrete_gold_bounding_boxes"] = self.discretize(
            data["gold_bounding_boxes"]
        )
        if "content_bounding_boxes" in data.keys():
            data["discrete_content_bounding_boxes"] = self.discretize(
                data["content_bounding_boxes"]
            )
        return data


class AddCanvasElement:
    def __init__(self, use_discrete=False, discrete_fn=None):
        self.x = torch.tensor([[0.0, 0.0, 1.0, 1.0]], dtype=torch.float)
        self.y = torch.tensor([0], dtype=torch.long)
        self.use_discrete = use_discrete
        self.discrete_fn = discrete_fn

    def __call__(self, data):
        if self.use_discrete:
            data["bounding_boxes_with_canvas"] = torch.cat(
                [
                    self.x,
                    self.discrete_fn.continuize(data["discrete_gold_bounding_boxes"]),
                ],
                dim=0,
            )
        else:
            data["bounding_boxes_with_canvas"] = torch.cat(
                [self.x, data["bounding_boxes"]], dim=0
            )
        data["labels_with_canvas"] = torch.cat([self.y, data["labels"]], dim=0)
        return data


class AddRelation:
    def __init__(self, seed=1024, ratio=0.1):
        self.ratio = ratio
        self.generator = random.Random()
        if seed is not None:
            self.generator.seed(seed)
        self.type2index = RelationTypes.type2index()

    def __call__(self, data):
        data["labels_with_canvas_index"] = [0] + list(
            range(len(data["labels_with_canvas"]) - 1)
        )
        N = len(data["labels_with_canvas"])

        rel_all = list(product(range(2), combinations(range(N), 2)))
        # size = min(int(len(rel_all)                     * self.ratio), 10)
        size = int(len(rel_all) * self.ratio)
        rel_sample = set(self.generator.sample(rel_all, size))

        relations = []
        for i, j in combinations(range(N), 2):
            bi, bj = (
                data["bounding_boxes_with_canvas"][i],
                data["bounding_boxes_with_canvas"][j],
            )
            canvas = data["labels_with_canvas"][i] == 0

            if ((0, (i, j)) in rel_sample) and (not canvas):
                relation_size = detect_size_relation(bi, bj)
                relations.append(
                    [
                        data["labels_with_canvas"][i],
                        data["labels_with_canvas_index"][i],
                        data["labels_with_canvas"][j],
                        data["labels_with_canvas_index"][j],
                        self.type2index[relation_size],
                    ]
                )

            if (1, (i, j)) in rel_sample:
                relation_location = detect_location_relation(bi, bj, canvas)
                relations.append(
                    [
                        data["labels_with_canvas"][i],
                        data["labels_with_canvas_index"][i],
                        data["labels_with_canvas"][j],
                        data["labels_with_canvas_index"][j],
                        self.type2index[relation_location],
                    ]
                )

        data["relations"] = torch.as_tensor(relations).long()

        return data


class RelationTypes:
    types = ["smaller", "equal", "larger", "top", "center", "bottom", "left", "right"]
    _type2index = None
    _index2type = None

    @classmethod
    def type2index(self):
        if self._type2index is None:
            self._type2index = dict()
            for index, type in enumerate(self.types):
                self._type2index[type] = index
        return self._type2index

    @classmethod
    def index2type(self):
        if self._index2type is None:
            self._index2type = dict()
            for index, type in enumerate(self.types):
                self._index2type[index] = type
        return self._index2type


class SaliencyMapToBoundingBoxes:
    def __init__(
        self,
        threshold: int,
        is_filter_small_bounding_boxes: bool = True,
        min_side: int = 80,
        min_area: int = 6000,
    ) -> None:
        self.threshold = threshold
        self.is_filter_small_bounding_boxes = is_filter_small_bounding_boxes
        self.min_side = min_side
        self.min_area = min_area

    def _is_small_bounding_box(self, bounding_box):
        return any(
            [
                all(
                    [bounding_box[2] <= self.min_side, bounding_box[3] <= self.min_side]
                ),
                bounding_box[2] * bounding_box[3] < self.min_area,
            ]
        )

    def __call__(self, saliency_map):
        saliency_map_gray = cv2.cvtColor(saliency_map, cv2.COLOR_BGR2GRAY)
        _, threshold_map = cv2.threshold(
            saliency_map_gray, self.threshold, 255, cv2.THRESH_BINARY
        )
        contours, _ = cv2.findContours(
            threshold_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if self.is_filter_small_bounding_boxes and self._is_small_bounding_box(
                [x, y, w, h]
            ):
                continue
            bounding_boxes.append([x, y, w, h])

        bounding_boxes = sorted(bounding_boxes, key=lambda x: (x[1], x[0]))
        bounding_boxes = torch.tensor(bounding_boxes)
        return bounding_boxes


class CLIPTextEncoder:
    def __init__(self, model_name: str = "ViT-B/32"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.process = clip.load(self.model_name, self.device)

    @torch.no_grad()
    def __call__(self, text: str):
        token = clip.tokenize(text, truncate=True).to(self.device)
        text_feature = self.model.encode_text(token)
        text_feature /= text_feature.norm(dim=-1, keepdim=True)
        return text_feature
