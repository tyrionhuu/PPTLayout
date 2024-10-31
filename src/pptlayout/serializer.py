from operators import RelationTypes
from utils import ID2LABEL, canvas_size

HTML_PREFIX = """<html>
<body>
<div class="canvas" style="left: 0px; top: 0px; width: {}px; height: {}px"></div>
"""

HTML_SUFFIX = """</body>
</html>"""

HTML_TEMPLATE = """<div class="{}" style="left: {}px; top: {}px; width: {}px; height: {}px"></div>
"""

HTML_TEMPLATE_WITH_INDEX = """<div class="{}" style="index: {}; left: {}px; top: {}px; width: {}px; height: {}px"></div>
"""


class Serializer:
    def __init__(
        self,
        input_format: str,
        output_format: str,
        index2label: dict,
        canvas_width: int,
        canvas_height: int,
        add_index_token: bool = True,
        add_separation_token: bool = True,
        separation_token: str = "|",
        add_unknown_token: bool = False,
        unknown_token: str = "<unknown>",  # unknown token
    ):
        self.input_format = input_format
        self.output_format = output_format
        self.index2label = index2label
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.add_index_token = add_index_token
        self.add_separation_token = add_separation_token
        self.separation_token = separation_token
        self.add_unknown_token = add_unknown_token
        self.unknown_token = unknown_token

    def build_input(self, data):
        if self.input_format == "sequence":
            return self._build_sequence_input(data)
        elif self.input_format == "html":
            return self._build_html_input(data)
        else:
            raise ValueError(f"Unsupported input format: {self.input_format}")

    def _build_sequence_input(self, data):
        raise NotImplementedError

    def _build_html_input(self, data):
        raise NotImplementedError

    def build_output(
        self, data, label_key="labels", bounding_box_key="discrete_gold_bounding_boxes"
    ):  # bounding_box_key: bounding box key
        if self.output_format == "sequence":
            return self._build_sequence_output(data, label_key, bounding_box_key)
        elif self.output_format == "html":
            return self._build_html_output(data, label_key, bounding_box_key)

    def _build_sequence_output(self, data, label_key, bounding_box_key):
        labels = data[label_key]
        bounding_boxes = data[bounding_box_key]
        tokens = []

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            bounding_box = bounding_boxes[index].tolist()
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(index))
            tokens.extend(map(str, bounding_box))
            if self.add_separation_token and index < len(labels) - 1:
                tokens.append(self.separation_token)
        return " ".join(tokens)

    def _build_html_output(self, data, label_key, bounding_box_key):
        labels = data[label_key]
        bounding_boxes = data[bounding_box_key]
        htmls = [HTML_PREFIX.format(self.canvas_width, self.canvas_height)]
        _TEMPLATE = HTML_TEMPLATE_WITH_INDEX if self.add_index_token else HTML_TEMPLATE

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            bounding_box = bounding_boxes[index].tolist()
            element = [label]
            if self.add_index_token:
                element.append(str(index))
            element.extend(map(str, bounding_box))
            htmls.append(_TEMPLATE.format(*element))
        htmls.append(HTML_SUFFIX)
        return "".join(htmls)


class BasicElementSerializer(Serializer):
    task_type = "generation conditioned on given element types"
    constraint_type = ["Element Type Constraint: "]
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN = '<div class="{}"></div>\n'
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX = (
        '<div class="{}" style="index: {}"></div>\n'
    )

    def _build_sequence_input(self, data):
        labels = data["labels"]
        tokens = []

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(index))
            if self.add_unknown_token:
                tokens += [self.unknown_token] * 4
            if self.add_separation_token and index < len(labels) - 1:
                tokens.append(self.separation_token)
        return " ".join(tokens)

    def _build_html_input(self, data):
        labels = data["labels"]
        htmls = [HTML_PREFIX.format(self.canvas_width, self.canvas_height)]
        if self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE_WITH_INDEX
        elif self.add_index_token and not self.add_unknown_token:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX
        elif not self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE
        else:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            element = [label]
            if self.add_index_token:
                element.append(str(index))
            if self.add_unknown_token:
                element += [self.unknown_token] * 4
            htmls.append(_TEMPLATE.format(*element))
        htmls.append(HTML_SUFFIX)
        return "".join(htmls)

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


class SizedElementSerializer(Serializer):
    task_type = "generation conditioned on given element types and sizes"
    constraint_type = ["Element Type and Size Constraint: "]
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN = (
        '<div class="{}" style="width: {}px; height: {}px"></div>\n'
    )
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX = (
        '<div class="{}" style="index: {}; width: {}px; height: {}px"></div>\n'
    )

    def _build_sequence_input(self, data):
        labels = data["labels"]
        bounding_boxes = data["discrete_gold_bounding_boxes"]
        tokens = []

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            bounding_box = bounding_boxes[index].tolist()
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(index))
            if self.add_unknown_token:
                tokens += [self.unknown_token] * 2
            tokens.extend(map(str, bounding_box[2:]))
            if self.add_separation_token and index < len(labels) - 1:
                tokens.append(self.separation_token)
        return " ".join(tokens)

    def _build_html_input(self, data):
        labels = data["labels"]
        bounding_boxes = data["discrete_gold_bounding_boxes"]
        htmls = [HTML_PREFIX.format(self.canvas_width, self.canvas_height)]
        if self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE_WITH_INDEX
        elif self.add_index_token and not self.add_unknown_token:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX
        elif not self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE
        else:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            bounding_box = bounding_boxes[index].tolist()
            element = [label]
            if self.add_index_token:
                element.append(str(index))
            if self.add_unknown_token:
                element += [self.unknown_token] * 2
            element.extend(map(str, bounding_box[2:]))
            htmls.append(_TEMPLATE.format(*element))
        htmls.append(HTML_SUFFIX)
        return "".join(htmls)

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


class RelationalElementSerializer(Serializer):
    task_type = (
        "generation conditioned on given element relationships\n"
        "'A left B' means that the center coordinate of A is to the left of the center coordinate of B. "
        "'A right B' means that the center coordinate of A is to the right of the center coordinate of B. "
        "'A top B' means that the center coordinate of A is above the center coordinate of B. "
        "'A bottom B' means that the center coordinate of A is below the center coordinate of B. "
        "'A center B' means that the center coordinate of A and the center coordinate of B are very close. "
        "'A smaller B' means that the area of A is smaller than the ares of B. "
        "'A larger B' means that the area of A is larger than the ares of B. "
        "'A equal B' means that the area of A and the ares of B are very close. "
        "Here, center coordinate = (left + width / 2, top + height / 2), "
        "area = width * height"
    )
    constraint_type = ["Element Type Constraint: ", "Element Relationship Constraint: "]
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN = '<div class="{}"></div>\n'
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX = (
        '<div class="{}" style="index: {}"></div>\n'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index2type = RelationTypes.index2type()

    def _build_sequence_input(self, data):
        labels = data["labels"]
        relations = data["relations"]
        tokens = []
        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(index))
            if self.add_unknown_token:
                tokens += [self.unknown_token] * 4
            if self.add_separation_token and index < len(labels) - 1:
                tokens.append(self.separation_token)
        type_conditions = " ".join(tokens)
        if len(relations) == 0:
            return self.constraint_type[0] + type_conditions
        tokens = []
        for index in range(len(relations)):
            label_i = relations[index][2]
            index_i = relations[index][3]
            if label_i != 0:
                tokens.append("{} {}".format(self.index2label[int(label_i)], index_i))
            else:
                tokens.append("canvas")
            tokens.append(self.index2type[int(relations[index][4])])
            label_j = relations[index][0]
            index_j = relations[index][1]
            if label_j != 0:
                tokens.append("{} {}".format(self.index2label[int(label_j)], index_j))
            else:
                tokens.append("canvas")
            if self.add_separation_token and index < len(relations) - 1:
                tokens.append(self.separation_token)
        relation_conditions = " ".join(tokens)
        return (
            self.constraint_type[0]
            + type_conditions
            + "\n"
            + self.constraint_type[1]
            + relation_conditions
        )

    def _build_html_input(self, data):
        labels = data["labels"]
        relations = data["relations"]
        htmls = [HTML_PREFIX.format(self.canvas_width, self.canvas_height)]
        if self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE_WITH_INDEX
        elif self.add_index_token and not self.add_unknown_token:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX
        elif not self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE
        else:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            element = [label]
            if self.add_index_token:
                element.append(str(index))
            if self.add_unknown_token:
                element += [self.unknown_token] * 4
            htmls.append(_TEMPLATE.format(*element))
        htmls.append(HTML_SUFFIX)
        type_conditions = "".join(htmls)
        if len(relations) == 0:
            return self.constraint_type[0] + type_conditions
        tokens = []
        for index in range(len(relations)):
            label_i = relations[index][2]
            index_i = relations[index][3]
            if label_i != 0:
                tokens.append("{} {}".format(self.index2label[int(label_i)], index_i))
            else:
                tokens.append("canvas")
            tokens.append(self.index2type[int(relations[index][4])])
            label_j = relations[index][0]
            index_j = relations[index][1]
            if label_j != 0:
                tokens.append("{} {}".format(self.index2label[int(label_j)], index_j))
            else:
                tokens.append("canvas")
            if self.add_separation_token and index < len(relations) - 1:
                tokens.append(self.separation_token)
        relation_conditions = " ".join(tokens)
        return (
            self.constraint_type[0]
            + type_conditions
            + "\n"
            + self.constraint_type[1]
            + relation_conditions
        )


class CompletionSerializer(Serializer):
    task_type = "layout completion"
    constraint_type = ["Partial Layout: "]

    def _build_sequence_input(self, data):
        data["partial_labels"] = data["labels"][:1]
        data["partial_bounding_boxes"] = data["discrete_bounding_boxes"][:1, :]
        return self._build_sequence_output(
            data, "partial_labels", "partial_bounding_boxes"
        )

    def _build_html_input(self, data):
        data["partial_labels"] = data["labels"][:1]
        data["partial_bounding_boxes"] = data["discrete_bounding_boxes"][:1, :]
        return self._build_html_output(data, "partial_labels", "partial_bounding_boxes")

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


class RefinementSerializer(Serializer):
    task_type = "layout refinement"
    constraint_type = ["Noise Layout: "]

    def _build_sequence_input(self, data):
        return self._build_sequence_output(data, "labels", "discrete_bounding_boxes")

    def _build_html_input(self, data):
        return self._build_html_output(data, "labels", "discrete_bounding_boxes")

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


class ContentAwareSerializer(Serializer):
    task_type = (
        "content-aware layout generation\n"
        "Please place the following elements to avoid salient content, and underlay must be the background of text or logo."
    )
    constraint_type = ["Content Constraint: ", "Element Type Constraint: "]
    CONTENT_TEMPLATE = "left {}px, top {}px, width {}px, height {}px"

    def _build_sequence_input(self, data):
        labels = data["labels"]
        content_bounding_boxes = data["discrete_content_bounding_boxes"]

        tokens = []
        for idx in range(len(content_bounding_boxes)):
            content_bounding_box = content_bounding_boxes[idx].tolist()
            tokens.append(self.CONTENT_TEMPLATE.format(*content_bounding_box))
            if self.add_index_token and idx < len(content_bounding_boxes) - 1:
                tokens.append(self.separation_token)
        content_cons = " ".join(tokens)

        tokens = []
        for idx in range(len(labels)):
            label = self.index2label[int(labels[idx])]
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(idx))
            if self.add_unknown_token:
                tokens += [self.unknown_token] * 4
            if self.add_separation_token and idx < len(labels) - 1:
                tokens.append(self.separation_token)
        type_cons = " ".join(tokens)
        return (
            self.constraint_type[0]
            + content_cons
            + "\n"
            + self.constraint_type[1]
            + type_cons
        )


class TextToLayoutSerializer(Serializer):
    task_type = (
        "text-to-layout\n"
        "There are ten optional element types, including: image, icon, logo, background, title, description, text, link, input, button. "
        "Please do not exceed the boundaries of the canvas. "
        "Besides, do not generate elements at the edge of the canvas, that is, reduce top: 0px and left: 0px predictions as much as possible."
    )
    constraint_type = ["Text: "]

    def _build_sequence_input(self, data):
        return data["text"]

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


class PowerPointLayoutSerializer(Serializer):
    task_type = "powerpoint layout generation conditioned on given element types from a powerpoint slide"
    constraint_type = ["Element Type Constraint: "]
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN = '<div class="{}"></div>\n'
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX = (
        '<div class="{}" style="index: {}"></div>\n'
    )

    def _build_sequence_input(self, data):
        labels = data["labels"]
        tokens = []

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            tokens.append(label)
            if self.add_index_token:
                tokens.append(str(index))
            if self.add_unknown_token:
                tokens += [self.unknown_token] * 4
            if self.add_separation_token and index < len(labels) - 1:
                tokens.append(self.separation_token)
        return " ".join(tokens)

    def _build_html_input(self, data):
        labels = data["labels"]
        htmls = [HTML_PREFIX.format(self.canvas_width, self.canvas_height)]
        if self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE_WITH_INDEX
        elif self.add_index_token and not self.add_unknown_token:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX
        elif not self.add_index_token and self.add_unknown_token:
            _TEMPLATE = HTML_TEMPLATE
        else:
            _TEMPLATE = self.HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN

        for index in range(len(labels)):
            label = self.index2label[int(labels[index])]
            element = [label]
            if self.add_index_token:
                element.append(str(index))
            if self.add_unknown_token:
                element += [self.unknown_token] * 4
            htmls.append(_TEMPLATE.format(*element))
        htmls.append(HTML_SUFFIX)
        return "".join(htmls)

    def build_input(self, data):
        return self.constraint_type[0] + super().build_input(data)


SERIALIZER_MAP = {
    "gent": BasicElementSerializer,
    "gents": SizedElementSerializer,
    "genr": RelationalElementSerializer,
    "completion": CompletionSerializer,
    "refinement": RefinementSerializer,
    "content": ContentAwareSerializer,
    "text": TextToLayoutSerializer,
    "pptlayout": PowerPointLayoutSerializer,
}


def create_serializer(
    dataset,
    task,
    input_format,
    output_format,
    add_index_token,
    add_separation_token,
    add_unknown_token,
    pptx_path=None,
):
    serializer_cls = SERIALIZER_MAP[task]
    index2label = ID2LABEL[dataset]
    canvas_width, canvas_height = canvas_size(dataset, pptx_path)
    serializer = serializer_cls(
        input_format=input_format,
        output_format=output_format,
        index2label=index2label,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        add_index_token=add_index_token,
        add_separation_token=add_separation_token,
        add_unknown_token=add_unknown_token,
    )
    return serializer


# if __name__ == "__main__":
#     import torch

#     ls = RefinementSerializer(
#         input_format="sequence",
#         output_format="html",
#         index2label=ID2LABEL["publaynet"],
#         canvas_width=120,
#         canvas_height=160,
#         add_separation_token=True,
#         add_unknown_token=False,
#         add_index_token=True,
#     )
#     labels = torch.tensor([4, 4, 1, 1, 1, 1])
#     bounding_boxes = torch.tensor(
#         [
#             [29, 14, 59, 2],
#             [10, 18, 99, 57],
#             [10, 79, 99, 4],
#             [10, 85, 99, 7],
#             [10, 99, 47, 50],
#             [61, 99, 47, 50],
#         ]
#     )

#     rearranged_labels = torch.tensor([1, 4, 1, 4, 1, 1])
#     relations = torch.tensor([[4, 1, 0, 1, 4], [1, 2, 1, 3, 2]])
#     data = {
#         "labels": labels,
#         "discrete_bounding_boxes": bounding_boxes,
#         "discrete_gold_bounding_boxes": bounding_boxes,
#         "relations": relations,
#         "rearranged_labels": rearranged_labels,
#     }
#     print("--------")
#     print(ls.build_input(data))
#     print("--------")
#     print(ls.build_output(data))
