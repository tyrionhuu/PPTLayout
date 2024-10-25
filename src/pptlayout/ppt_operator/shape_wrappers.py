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
    def text_info(self) -> None:
        pass

    @property
    def position_info(self) -> str:
        return f"Position: left={self.left}, top={self.top}\n"

    @property
    def size_info(self) -> str:
        return f"Size: width={self.width}, height={self.height}\n"

    @property
    def style_info(self) -> None:
        # return f"Name: {self.name}, Shape ID: {self.shape_id}\n"
        pass

    @property
    def shape_description(self) -> str:
        try:
            assert self.name.split(" ")[0] == "Google"
            return f"{self.name.split(' ')[0]}\n"
        except AssertionError:
            return f"{str(self.shape_type).split(' ')[0].strip()}\n"

    def __repr__(self):
        description = ""
        description += self.shape_description
        description += self.size_info
        if self.text_info is not None:
            description += self.text_info
        description += self.position_info
        if self.style_info is not None:
            description += self.style_info
        return description
