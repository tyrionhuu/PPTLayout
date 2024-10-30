import random

import cv2
import numpy as np
from utils import (
    alignment_similarity,
    canvas_size,
    depth_similarity,
    labels_bounding_boxes_similarity,
    labels_similarity,
    normalize_weights,
    rotation_similarity,
)


class ExemplarSelector:
    def __init__(
        self,
        train_data: list,
        candidate_size: int,
        num_prompt: int,
        shuffle: bool = True,
    ):
        self.train_data = train_data
        self.candidate_size = candidate_size
        self.num_prompt = num_prompt
        self.shuffle = shuffle
        if self.candidate_size > 0:
            random.shuffle(self.train_data)
            self.train_data = self.train_data[: self.candidate_size]

    def __call__(self, test_data: dict):
        pass

    def _is_filter(self, data):
        return (data["discrete_gold_bounding_boxes"][:, 2:] == 0).sum().bool().item()

    def _retrieve_exemplars(self, scores: list):
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        exemplars = []
        for i in range(len(self.train_data)):
            if not self._is_filter(self.train_data[scores[i][0]]):
                exemplars.append(self.train_data[scores[i][0]])
                if len(exemplars) == self.num_prompt:
                    break
        if self.shuffle:
            random.shuffle(exemplars)
        return exemplars


class BasicElementExemplarSelector(ExemplarSelector):
    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"]
            score = labels_similarity(train_labels, test_labels)
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class SizedElementExemplarSelector(ExemplarSelector):
    labels_weight = 0.5
    bounding_boxes_weight = 0.5

    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"]
        test_bounding_boxes = test_data["bounding_boxes"][:, 2:]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"]
            train_bounding_boxes = self.train_data[i]["bounding_boxes"][:, 2:]
            score = labels_bounding_boxes_similarity(
                train_labels,
                train_bounding_boxes,
                test_labels,
                test_bounding_boxes,
                self.labels_weight,
                self.bounding_boxes_weight,
            )
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class RelationalElementExemplarSelector(ExemplarSelector):
    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"]
            score = labels_similarity(train_labels, test_labels)
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class CompletionExemplarSelector(ExemplarSelector):
    labels_weight = 0.0
    bounding_boxes_weight = 1.0

    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"][:1]
        test_bounding_boxes = test_data["bounding_boxes"][:1, :]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"][:1]
            train_bounding_boxes = self.train_data[i]["bounding_boxes"][:1, :]
            score = labels_bounding_boxes_similarity(
                train_labels,
                train_bounding_boxes,
                test_labels,
                test_bounding_boxes,
                self.labels_weight,
                self.bounding_boxes_weight,
            )
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class RefinementExemplarSelector(ExemplarSelector):
    labels_weight = 0.5
    bounding_boxes_weight = 0.5

    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"]
        test_bounding_boxes = test_data["bounding_boxes"]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"]
            train_bounding_boxes = self.train_data[i]["bounding_boxes"]
            score = labels_bounding_boxes_similarity(
                train_labels,
                train_bounding_boxes,
                test_labels,
                test_bounding_boxes,
                self.labels_weight,
                self.bounding_boxes_weight,
            )
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class ContentAwareExemplarSelector(ExemplarSelector):
    canvas_width, canvas_height = canvas_size["posterlayout"]

    def _to_binary_image(self, content_bounding_boxes):
        binary_image = np.zeros((self.canvas_height, self.canvas_width), dtype=np.uint8)
        content_bounding_boxes = content_bounding_boxes.tolist()
        for content_bbox in content_bounding_boxes:
            l, t, w, h = content_bbox
            cv2.rectangle(binary_image, (l, t), (l + w, t + h), 255, thickness=-1)
        return binary_image

    def __call__(self, test_data: dict):
        scores = []
        test_content_bounding_boxes = test_data["discrete_content_bounding_boxes"]
        test_binary = self._to_binary_image(test_content_bounding_boxes)
        for i in range(len(self.train_data)):
            train_content_bounding_boxes = self.train_data[i][
                "discrete_content_bounding_boxes"
            ]
            train_binary = self._to_binary_image(train_content_bounding_boxes)
            intersection = cv2.bitwise_and(train_binary, test_binary)
            union = cv2.bitwise_or(train_binary, test_binary)
            iou = (np.sum(intersection) + 1) / (np.sum(union) + 1)
            scores.append([i, iou])
        return self._retrieve_exemplars(scores)


class TextToLayoutExemplarSelector(ExemplarSelector):
    def __call__(self, test_data: dict):
        scores = []
        test_embedding = test_data["embedding"]
        for i in range(len(self.train_data)):
            train_embedding = self.train_data[i]["embedding"]
            score = (train_embedding @ test_embedding.T).item()
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


class PowerPointExemplarSelector(ExemplarSelector):
    label_weight = 5
    bounding_box_weight = 5
    depth_weight = 1
    rotation_weight = 1
    alignment_weight = 1

    (
        label_weight,
        bounding_box_weight,
        depth_weight,
        rotation_weight,
        alignment_weight,
    ) = normalize_weights(
        label_weight,
        bounding_box_weight,
        depth_weight,
        rotation_weight,
        alignment_weight,
    )

    def __call__(self, test_data: dict):
        scores = []
        test_labels = test_data["labels"]
        test_bounding_boxes = test_data["bounding_boxes"]
        test_depth = test_data["depth"]
        test_rotation = test_data["rotation"]
        test_alignment = test_data["text_alignment"]
        for i in range(len(self.train_data)):
            train_labels = self.train_data[i]["labels"]
            train_bounding_boxes = self.train_data[i]["bounding_boxes"]
            train_depth = self.train_data[i]["depth"]
            train_rotation = self.train_data[i]["rotation"]
            train_alignment = self.train_data[i]["text_alignment"]
            score = (
                labels_similarity(train_labels, test_labels) * self.label_weight
                + labels_bounding_boxes_similarity(
                    train_labels,
                    train_bounding_boxes,
                    test_labels,
                    test_bounding_boxes,
                    self.label_weight,
                    self.bounding_box_weight,
                )
                + depth_similarity(train_depth, test_depth) * self.depth_weight
                + rotation_similarity(train_rotation, test_rotation)
                * self.rotation_weight
                + alignment_similarity(train_alignment, test_alignment)
                * self.alignment_weight
            )
            scores.append([i, score])
        return self._retrieve_exemplars(scores)


SELECTOR_MAP = {
    "gent": BasicElementExemplarSelector,
    "gents": SizedElementExemplarSelector,
    "genr": RelationalElementExemplarSelector,
    "completion": CompletionExemplarSelector,
    "refinement": RefinementExemplarSelector,
    "content": ContentAwareExemplarSelector,
    "text": TextToLayoutExemplarSelector,
    "pptlayout": PowerPointExemplarSelector,
}


def create_selector(task, train_data, candidate_size, num_prompt, *args, **kwargs):
    selector_cls = SELECTOR_MAP[task]
    selector = selector_cls(
        train_data=train_data,
        candidate_size=candidate_size,
        num_prompt=num_prompt,
        *args,
        **kwargs,
    )
    return selector
