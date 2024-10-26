"""
from python-pptx documentation:

for real-life shapes, there are these nine types:

shape shapes – auto shapes with fill and an outline
text boxes – auto shapes with no fill and no outline
placeholders – auto shapes that can appear on a slide layout or master and be inherited on slides that use that layout, allowing content to be added that takes on the formatting of the placeholder
line/connector – as described above
picture – as described above
table – that row and column thing
chart – pie chart, line chart, etc.
smart art – not supported yet, although preserved if present
media clip – video or audio

"""

from tabulate import tabulate
from utils import get_fill_color


class BaseShapeWrapper:
    def __init__(self, shape):
        self.shape_type = shape.shape_type
        self.height = shape.height
        self.width = shape.width
        self.left = shape.left
        self.top = shape.top
        self.name = shape.name
        self.shape_id = shape.shape_id

    @property
    def text_info(self):
        pass

    @property
    def position_info(self) -> str:
        return f"Position: left={self.left}, top={self.top}\n"

    @property
    def size_info(self) -> str:
        return f"Size: width={self.width}, height={self.height}\n"

    @property
    def style_info(self):
        pass

    @property
    def shape_description(self) -> str:
        try:
            assert self.name.split(" ")[0] == "Google"
            return f"{self.name.split(' ')[0]}\n"
        except AssertionError:
            return f"{str(self.shape_type).split(' ')[0].strip()}\n"

    def describe_self(self) -> str:
        content = ""
        # content += str(self.shape_type) if self.shape_type is not None else ""
        content += self.shape_description if self.shape_description is not None else ""
        content += self.size_info if self.size_info is not None else ""
        content += self.text_info if self.text_info is not None else ""
        content += self.position_info if self.position_info is not None else ""
        content += self.style_info if self.style_info is not None else ""
        return content

    def __repr__(self):
        return self.describe_self()


class PictureWrapper(BaseShapeWrapper):
    def __init__(self, shape, id=None):
        super().__init__(shape)
        self.image = shape.image
        self.rotation = int(shape.rotation)
        self.id = id

    @property
    def shape_description(self) -> str:
        if self.id is not None:
            return f"[Picture {self.id}]\n"
        else:
            return "[Picture]\n"

    @property
    def rotation_info(self) -> str:
        return f"Rotation: {self.rotation}\n"

    def __repr__(self):
        return super().__repr__() + self.rotation_info


class TableWrapper(BaseShapeWrapper):
    def __init__(self, shape):
        super().__init__(shape)
        self.table = shape.table
        self.rows = shape.table.rows
        self.columns = shape.table.columns

    @property
    def text_info(self) -> str:
        content = "Table:\n"
        table_data = []
        for row in self.rows:
            table_data.append([cell.text for cell in row.cells])
        content += tabulate(table_data, tablefmt="grid")
        content += "\n"
        return content

    @property
    def shape_description(self) -> str:
        return f"[Table] with {len(self.rows)} rows and {len(self.columns)} columns\n"

    def describe_self(self):
        return super().describe_self()


class TextBoxWrapper(BaseShapeWrapper):
    def __init__(self, shape, id=None):
        super().__init__(shape)
        self.text = shape.text_frame.text
        self.paragraphs = shape.text_frame.paragraphs
        try:
            self.font = self.paragraphs[0].runs[0].font
        except Exception:
            self.font = self.paragraphs[0].font
        self.bold = self.font.bold
        self.italic = self.font.italic
        self.underline = self.font.underline
        self.size = (
            self.font.size
            if self.font.size is not None
            else self.paragraphs[0].font.size
        )
        try:
            self.color = self.font.color.rgb
        except Exception:
            self.color = None
        self.fill = get_fill_color(shape)
        self.font_name = self.font.name
        self.line_spacing = self.paragraphs[0].line_spacing
        self.align = self.paragraphs[0].alignment
        self.id = id

    @property
    def text_info(self):
        return f"Text: {self.text}\n"

    @property
    def style_info(self):
        return f"Font Style: bold={self.bold}, italic={self.italic}, underline={self.underline}, size={self.size}, color={self.color}, fill={self.fill}, font style={self.font_name}, line_space={self.line_spacing}, align={self.align}\n"

    @property
    def shape_description(self):
        if self.id is not None:
            return f"[TextBox {self.id}]\n"
        else:
            return "[TextBox]\n"

    def describe_self(self):
        return super().describe_self()


class PlaceholderWrapper(BaseShapeWrapper):
    def __init__(self, shape):
        super().__init__(shape)
        self.fill = get_fill_color(shape)
        self.text = shape.text_frame.text
        if shape.has_text_frame:
            textframe = shape.text_frame
            try:
                font = shape.text_frame.paragraphs[0].runs[0].font
            except Exception:
                font = shape.text_frame.paragraphs[0].font
            self.bold = font.bold
            self.italic = font.italic
            self.underline = font.underline
            self.size = font.size
            try:
                self.color = font.color.rgb
            except Exception:
                self.color = None
            self.font_name = font.name
            self.line_spacing = textframe.paragraphs[0].line_spacing
            self.align = textframe.paragraphs[0].alignment

    @property
    def text_info(self):
        if self.text is not None:
            return f"Text: \n{self.text}\n"
        else:
            return ""

    @property
    def style_info(self):
        return f"Font Style: bold={self.bold}, italic={self.italic}, underline={self.underline}, size={self.size}, color={self.color}, fill={self.fill}, font style={self.font_name}, line_space={self.line_spacing}, align={self.align}\n"

    def describe_self(self):
        return super().describe_self()


class AutoShapeWrapper(BaseShapeWrapper):
    def __init__(self, shape):
        super().__init__(shape)
        self.text = shape.text_frame.text
        self.fill = get_fill_color(shape)

    @property
    def text_info(self):
        return f"Text: {self.text}\n"

    @property
    def style_info(self):
        return f"Shape Style: fill={self.fill}\n"

    def describe_self(self):
        return super().describe_self()
