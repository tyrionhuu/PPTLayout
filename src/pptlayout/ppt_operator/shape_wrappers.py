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
    def text_info(self) -> str:
        return ""

    @property
    def position_info(self) -> str:
        return f"Position: left={self.left}, top={self.top}\n"

    @property
    def size_info(self) -> str:
        return f"Size: width={self.width}, height={self.height}\n"

    @property
    def style_info(self) -> str:
        return f"Name: {self.name}, Shape ID: {self.shape_id}\n"

    @property
    def shape_description(self) -> str:
        try:
            assert self.name.split(" ")[0] == "Google"
            return f"{self.name.split(' ')[0]}\n"
        except AssertionError:
            return f"{str(self.shape_type).split(' ')[0].strip()}\n"

    def __repr__(self):
        content = ""
        content += self.shape_description
        content += self.size_info
        if self.text_info is not None:
            content += self.text_info
        content += self.position_info
        if self.style_info is not None:
            content += self.style_info
        return content


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


class TableWrapper(BaseShapeWrapper):
    def __init__(self, shape):
        super().__init__(shape)
        self.table = shape.table
        self.rows = shape.table.rows
        self.columns = shape.table.columns

    @property
    def text_info(self) -> str:
        content = "Data:\n"
        for row in self.rows:
            content += "|"
            for cell in row.cells:
                content += f"{cell.text}|"
            content += "\n"
        return content

    @property
    def shape_description(self) -> str:
        return f"[Table] with {len(self.rows)} rows and {len(self.columns)} columns\n"
