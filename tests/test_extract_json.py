import pytest

from src.pptlayout.llm.parser import extract_json


@pytest.fixture
def json_text():
    text = """Based on the provided JSON input, I analyzed the layout and suggest an improved version to enhance readability, visual appeal, and overall coherence. Here is the revised JSON output:

```json
{
  "slide_id": 256,
  "slide_name": "",
  "shapes": [
    {
      "name": "PlaceHolder 1",
      "shape_id": 22,
      "shape_type": "PLACEHOLDER",
      "measurement_unit": "emu",
      "height": 2000000,
      "width": 7000000,
      "left": 850000,
      "top": 1200000,
      "text": "Design for a 2 MW graphite target\x0b\x0bfor a neutrino beam",
      "placeholder_type": "TITLE"
    },
    {
      "name": "PlaceHolder 2",
      "shape_id": 23,
      "shape_type": "PLACEHOLDER",
      "measurement_unit": "emu",
      "height": 1500000,
      "width": 7500000,
      "left": 500000,
      "top": 4200000,
      "text": "Jim Hylen\n\nAccelerator Physics and Technology Workshop for Project X\x0bNovember 12-13, 2007",
      "placeholder_type": "SUBTITLE"
    }
  ]
}
```

The following changes were made to improve the layout:

1. **Adjusted title position**: Moved the title ("PlaceHolder 1") to a more centered position horizontally (`left`: 850000 → 685800) and vertically (`top`: 1371240 → 1200000). This creates a better balance and makes the title more prominent.
2. **Reduced title size**: Decreased the height of the title (`height`: 2228760 → 2000000) to create a clearer visual hierarchy between the title and subtitle.
3. **Adjusted subtitle position**: Moved the subtitle ("PlaceHolder 2") to a more centered position horizontally (`left`: 380520 → 500000) and adjusted its vertical position (`top`: 3962520 → 4200000) to maintain a consistent spacing between elements.
4. **Reduced subtitle size**: Decreased the width of the subtitle (`width`: 8153640 → 7500000) to create a better balance with the title and improve readability.

These changes aim to enhance the slide's visual appeal, readability, and coherence by:

* Creating a clear visual hierarchy between elements
* Improving horizontal and vertical alignment
* Maintaining consistent spacing between elements
* Enhancing the overall balance of the layout

Note that these changes only modify existing layout parameters (position, size, and content) without adding or removing elements."""

    return text


def test_extract_json(json_text):
    json_data = extract_json(json_text)
    assert json_data is not None
    assert json_data["slide_id"] == 256
    assert json_data["shapes"][0]["name"] == "PlaceHolder 1"
    assert json_data["shapes"][1]["name"] == "PlaceHolder 2"
    assert json_data["shapes"][0]["shape_type"] == "PLACEHOLDER"
    assert json_data["shapes"][1]["shape_type"] == "PLACEHOLDER"
    assert json_data["shapes"][0]["placeholder_type"] == "TITLE"
    assert json_data["shapes"][1]["placeholder_type"] == "SUBTITLE"
    # assert (
    #     json_data["shapes"][0]["text"]
    #     == "Design for a 2 MW graphite target\x0b\x0bfor a neutrino beam"
    # )
    # assert (
    #     json_data["shapes"][1]["text"]
    #     == "Jim Hylen\n\nAccelerator Physics and Technology Workshop for Project X\x0bNovember 12-13, 2007"
    # )
    assert json_data["shapes"][0]["height"] == 2000000
    assert json_data["shapes"][1]["width"] == 7500000
    assert json_data["shapes"][0]["left"] == 850000
    assert json_data["shapes"][1]["top"] == 4200000
    assert json_data["shapes"][0]["measurement_unit"] == "emu"
    assert json_data["shapes"][1]["measurement_unit"] == "emu"
