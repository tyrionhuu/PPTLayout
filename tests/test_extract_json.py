import pytest

from src.pptlayout.llm.parser import extract_json


@pytest.fixture
def json_text():
    text = """Based on the provided JSON input, I've analyzed the layout and suggested an improved version. Here is the revised JSON output:
```json
{
  "slide_id": 268,
  "slide_name": "",
  "shapes": [
    {
      "name": "PlaceHolder 1",
      "shape_id": 84,
      "shape_type": "PLACEHOLDER",
      "measurement_unit": "emu",
      "height": 533520,
      "width": 6477120,
      "left": 1523880,
      "top": 228600, // Changed top position to create more space between title and content
      "text": "Efficiency of neutrino generation",
      "placeholder_type": "TITLE"
    },
    {
      "name": "",
      "shape_id": 85,
      "shape_type": "AUTO_SHAPE",
      "measurement_unit": "emu",
      "height": 762120,
      "width": 6553080,
      "left": 1143000,
      "top": 5181480, // Changed top position to align with the bottom of the title
      "text": "The  “2MW” target is about 10% less efficient at neutrino generation\n  than a 0.4 MW “Medium Energy” target \n(ME target is more optimized to NoVA than the existing LE target)"
    },
    {
      "name": "",
      "shape_id": 86,
      "shape_type": "AUTO_SHAPE",
      "measurement_unit": "emu",
      "height": 228600, // Changed height to create more space between content and image
      "width": 609480,
      "left": 7772400,
      "top": 3581280, // Changed top position to align with the bottom of the content
      "text": ""
    },
    {
      "name": "",
      "shape_id": 87,
      "shape_type": "AUTO_SHAPE",
      "measurement_unit": "emu",
      "height": 152280, // Changed height to create more space between image and slide number
      "width": 1447560,
      "left": 4191120,
      "top": 4191120, // Changed top position to align with the bottom of the image
      "text": ""
    },
    {
      "name": "",
      "shape_id": 88,
      "shape_type": "PICTURE",
      "measurement_unit": "emu",
      "height": 4192560, // Changed height to create more space between image and slide number
      "width": 7315200,
      "left": 762120,
      "top": 870120, // Changed top position to align with the bottom of the content
      "auto_shape_type": <MSO_AUTO_SHAPE_TYPE.RECTANGLE: 1>
    },
    {
      "name": "PlaceHolder 2",
      "shape_id": 3,
      "shape_type": "PLACEHOLDER",
      "measurement_unit": "emu",
      "height": 380880, // Changed height to create more space between slide number and bottom of the slide
      "width": 838440,
      "left": 7695720,
      "top": 6477120, // Changed top position to align with the bottom of the image
      "text": "13",
      "placeholder_type": "SLIDE_NUMBER"
    }
  ]
}
```
Here is a list of changes made to improve the layout:

1. **Increased space between title and content**: Moved the top position of the first shape (title) down by 228600 emu to create more space between the title and the content.
2. **Aligned content with the bottom of the title**: Changed the top position of the second shape (content) to align with the bottom of the title, creating a clear visual hierarchy.
3. **Increased space between content and image**: Changed the height of the third shape (empty shape) to create more space between the content and the image.
4. **Aligned image with the bottom of the content**: Changed the top position of the fourth shape (image) to align with the bottom of the content, creating a clear visual hierarchy.
5. **Increased space between image and slide number**: Changed the height of the fifth shape (empty shape) to create more space between the image and the slide number.
6. **Aligned slide number with the bottom of the image**: Changed the top position of the sixth shape (slide number) to align with the bottom of the image, creating a clear visual hierarchy.

These changes improve the readability, visual appeal, and overall coherence of the slide by maintaining consistent alignment, spacing, visual hierarchy, and design principles."""

    return text


def test_extract_json(json_text):
    json_data = extract_json(json_text)
    assert json_data is not None
    # assert json_data["slide_id"] == 256
    # assert json_data["shapes"][0]["name"] == "PlaceHolder 1"
    # assert json_data["shapes"][1]["name"] == "PlaceHolder 2"
    # assert json_data["shapes"][0]["shape_type"] == "PLACEHOLDER"
    # assert json_data["shapes"][1]["shape_type"] == "PLACEHOLDER"
    # assert json_data["shapes"][0]["placeholder_type"] == "TITLE"
    # assert json_data["shapes"][1]["placeholder_type"] == "SUBTITLE"
    # # assert (
    # #     json_data["shapes"][0]["text"]
    # #     == "Design for a 2 MW graphite target\x0b\x0bfor a neutrino beam"
    # # )
    # # assert (
    # #     json_data["shapes"][1]["text"]
    # #     == "Jim Hylen\n\nAccelerator Physics and Technology Workshop for Project X\x0bNovember 12-13, 2007"
    # # )
    # assert json_data["shapes"][0]["height"] == 2000000
    # assert json_data["shapes"][1]["width"] == 7500000
    # assert json_data["shapes"][0]["left"] == 850000
    # assert json_data["shapes"][1]["top"] == 4200000
    # assert json_data["shapes"][0]["measurement_unit"] == "emu"
    # assert json_data["shapes"][1]["measurement_unit"] == "emu"
