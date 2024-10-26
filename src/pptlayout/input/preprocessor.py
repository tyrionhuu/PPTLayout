import copy

from torchvision import transforms
from transforms import (
    DiscretizeBoundingBox,
    LabelDictSort,
    LexicographicSort,
    ShuffleElements,
)


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
