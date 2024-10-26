from utils import get_slide_size

PREAMBLE = (
    "Please generate a PowerPoint slide layout based on the provided details."
    "Ensure that the layout is visually appealing, with well-aligned elements and no unnecessary overlapping content.\n"
    "Task Description: {}\n"
    "Layout Domain: {} slide layout\n"
    "Slide Dimensions: width is {} units, height is {} units"
)

HTML_PREFIX = """<html>
<body>
<div class="canvas" style="left: 0units; top: 0units; width: {}units; height: {}units"></div>
"""

HTML_SUFFIX = """</body>
</html>"""

HTML_TEMPLATE = """<div class="{}" style="left: {}units; top: {}units; width: {}units; height: {}units"></div>
"""

HTML_TEMPLATE_WITH_INDEX = """<div class="{}" style="index: {}; left: {}units; top: {}units; width: {}units; height: {}units"></div>
"""


class Serializer:
    def __init__(
        self,
        input_format: str,
        output_format: str,
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
            label = labels[index]
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
            label = labels[index]
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
            label = labels[index]
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
            label = labels[index]
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
        '<div class="{}" style="width: {}units; height: {}units"></div>\n'
    )
    HTML_TEMPLATE_WITHOUT_UNKNOWN_TOKEN_WITH_INDEX = (
        '<div class="{}" style="index: {}; width: {}units; height: {}units"></div>\n'
    )

    def _build_sequence_input(self, data):
        labels = data["labels"]
        bounding_boxes = data["discrete_gold_bounding_boxes"]
        tokens = []

        for index in range(len(labels)):
            label = labels[index]
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
            label = labels[index]
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


SERIALIZER_MAP = {
    "gent": BasicElementSerializer,
    "gents": SizedElementSerializer,
    # "genr": GenRelationSerializer,
    # "completion": CompletionSerializer,
    # "refinement": RefinementSerializer,
    # "content": ContentAwareSerializer,
    # "text": TextToLayoutSerializer,
}


def create_serializer(
    dataset,
    task,
    input_format,
    output_format,
    add_index_token,
    add_separation_token,
    add_unknown_token,
    presentation,
):
    serializer_class = SERIALIZER_MAP[task]
    canvas_width, canvas_height = get_slide_size(presentation)
    serializer = serializer_class(
        input_format=input_format,
        output_format=output_format,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        add_index_token=add_index_token,
        add_sep_token=add_separation_token,
        add_unk_token=add_unknown_token,
    )
    return serializer
