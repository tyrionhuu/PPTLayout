import copy

from operators import (
    AddCanvasElement,
    AddGaussianNoise,
    AddRelation,
    DiscretizeBoundingBox,
    LabelDictSort,
    LexicographicSort,
    SaliencyMapToBoundingBoxes,
    ShuffleElements,
)
from pandas import DataFrame
from torchvision import transforms


class Processor:
    def __init__(
        self, index2label: dict, canvas_width: int, canvas_height: int, *args, **kwargs
    ):
        self.index2label = index2label
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.sort_by_position = kwargs.get("sort_by_position", None)
        self.shuffle_before_sort_by_label = kwargs.get(
            "shuffle_before_sort_by_label", None
        )
        self.sort_by_position_before_sort_by_label = kwargs.get(
            "sort_by_position_before_sort_by_label", None
        )

        if not any(
            [
                self.sort_by_position,
                self.shuffle_before_sort_by_label,
                self.sort_by_position_before_sort_by_label,
            ]
        ):
            raise ValueError(
                "At least one of sort_by_position, shuffle_before_sort_by_label, or sort_by_position_before_sort_by_label must be True."
            )
        self.transform_functions = self._config_base_transform()

    def _config_base_transform(self):
        transform_functions = list()
        if self.sort_by_position:
            transform_functions.append(LexicographicSort())
        else:
            if self.shuffle_before_sort_by_label:
                transform_functions.append(ShuffleElements())
            elif self.sort_by_position_before_sort_by_label:
                transform_functions.append(LexicographicSort())
            transform_functions.append(LabelDictSort(self.index2label))
        transform_functions.append(
            DiscretizeBoundingBox(
                num_x_grid=self.canvas_width, num_y_grid=self.canvas_height
            )
        )
        return transform_functions

    def __call__(self, data):
        _data = self.transform(copy.deepcopy(data))
        return {k: _data[k] for k in self.return_keys}


class BasicElementProcessor(Processor):
    return_keys = [
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
    ]

    def __init__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        sort_by_position: bool = False,
        shuffle_before_sort_by_label: bool = False,
        sort_by_position_before_sort_by_label: bool = True,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform = transforms.Compose(self.transform_functions)


class SizedElementProcessor(Processor):
    return_keys = [
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
    ]

    def __init__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        sort_by_position: bool = False,
        shuffle_before_sort_by_label: bool = True,
        sort_by_position_before_sort_by_label: bool = False,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform = transforms.Compose(self.transform_functions)


class RelationalElementProcessor(Processor):
    return_keys = [
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
        "relations",
    ]

    def __init__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        sort_by_position: bool = False,
        shuffle_before_sort_by_label: bool = True,
        sort_by_position_before_sort_by_label: bool = False,
        relation_constrained_discrete_before_induce_relations: bool = False,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform_functions = self.transform_functions[:-1]
        if relation_constrained_discrete_before_induce_relations:
            self.transform_functions.append(
                DiscretizeBoundingBox(
                    num_x_grid=self.canvas_width, num_y_grid=self.canvas_height
                )
            )
            self.transform_functions.append(
                AddCanvasElement(
                    use_discrete=True, discrete_fn=self.transform_functions[-1]
                )
            )
            self.transform_functions.append(AddRelation())
        else:
            self.transform_functions.append(AddCanvasElement())
            self.transform_functions.append(AddRelation())
            self.transform_functions.append(
                DiscretizeBoundingBox(
                    num_x_grid=self.canvas_width, num_y_grid=self.canvas_height
                )
            )
        self.transform = transforms.Compose(self.transform_functions)


class CompletionProcessor(Processor):
    return_keys = [
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
    ]

    def __inti__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        sort_by_position: bool = True,
        shuffle_before_sort_by_label: bool = False,
        sort_by_position_before_sort_by_label: bool = False,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform = transforms.Compose(self.transform_functions)


class RefinementProcessor(Processor):
    return_keys = [
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
    ]

    def __init__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        sort_by_position: bool = True,
        shuffle_before_sort_by_label: bool = False,
        sort_by_position_before_sort_by_label: bool = False,
        gaussian_noise_mean: float = 0.0,
        gaussian_noise_std: float = 0.01,
        train_bernoulli_beta: float = 1.0,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform_functions = [
            AddGaussianNoise(
                mean=gaussian_noise_mean,
                std=gaussian_noise_std,
                train_bernoulli_beta=train_bernoulli_beta,
            )
        ] + self.transform_functions
        self.transform = transforms.Compose(self.transform_functions)


class ContentAwareProcessor(Processor):
    return_keys = [
        "index",
        "labels",
        "bounding_boxes",
        "gold_bounding_boxes",
        "discrete_bounding_boxes",
        "discrete_gold_bounding_boxes",
        "discrete_content_bounding_boxes",
    ]

    def __init__(
        self,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        metadata: DataFrame,
        sort_by_position: bool = True,
        shuffle_before_sort_by_label: bool = False,
        sort_by_position_before_sort_by_label: bool = False,
        filter_threshold: int = 100,
        max_element_numbers: int = 10,
        original_width: float = 513.0,
        original_height: float = 750.0,
    ):
        super().__init__(
            index2label=index2label,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            sort_by_position=sort_by_position,
            shuffle_before_sort_by_label=shuffle_before_sort_by_label,
            sort_by_position_before_sort_by_label=sort_by_position_before_sort_by_label,
        )
        self.transform = transforms.Compose(self.transform_functions)
        self.metadata = metadata
        self.max_element_numbers = max_element_numbers
        self.original_width = original_width
        self.original_height = original_height
        self.saliency_map_to_bounding_boxes = SaliencyMapToBoundingBoxes(
            filter_threshold
        )
        self.possible_labels: list = []
