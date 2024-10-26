PREAMBLE = (
    "Please generate a layout based on the given information. "
    "You need to ensure that the generated layout looks realistic, with elements well aligned and avoiding unnecessary overlap.\n"
    "Task Description: {}\n"
    "Layout Domain: {} layout\n"
    "Canvas Size: canvas width is {}px, canvas height is {}px"
)

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
        add_sep_token: bool = True,
        sep_token: str = "|",
        add_unk_token: bool = False,
        unk_token: str = "<unk>",  # unknown token
    ):
        self.input_format = input_format
        self.output_format = output_format
        self.index2label = index2label
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.add_index_token = add_index_token
        self.add_sep_token = add_sep_token
        self.sep_token = sep_token
        self.add_unk_token = add_unk_token
        self.unk_token = unk_token

    def build_input(self, data):
        if self.input_format == "seq":
            return self._build_seq_input(data)
        elif self.input_format == "html":
            return self._build_html_input(data)
        else:
            raise ValueError(f"Unsupported input format: {self.input_format}")

    def _build_seq_input(self, data):
        raise NotImplementedError

    def _build_html_input(self, data):
        raise NotImplementedError

    def build_output(
        self, data, label_key="labels", bounding_box_key="discrete_gold_bounding_boxes"
    ):  # bounding_box_key: bounding box key
        if self.output_format == "seq":
            return self._build_seq_output(data, label_key, bounding_box_key)
        elif self.output_format == "html":
            return self._build_html_output(data, label_key, bounding_box_key)

    def _build_seq_output(self, data, label_key, bounding_box_key):
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
            if self.add_sep_token and index < len(labels) - 1:
                tokens.append(self.sep_token)
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
