import json
from typing import Union

import regex as re


class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r"([^\\])\\([^\\])"), r"\1\\\\\2"),
            (re.compile(r",(\s*])"), r"\1"),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)


def sanitize_json_string(json_string: str) -> str:
    """Sanitize the JSON string by removing comments, escaping special characters, and ensuring valid JSON format."""

    # Remove comments (anything following // until the end of the line)
    sanitized_string = re.sub(r"//.*", "", json_string)

    # Remove control characters
    sanitized_string = re.sub(r"[\x00-\x1F\x7F]", " ", sanitized_string)

    # Escape newline characters for consistency
    sanitized_string = re.sub(r"\n", "\\n", sanitized_string)

    return sanitized_string


def extract_json_with_markers(text: str) -> dict | None:
    start_marker = "```json"
    end_marker = "```"

    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index + len(start_marker))

    if start_index != -1 and end_index != -1:
        json_string = text[start_index + len(start_marker) : end_index].strip()
        json_string = sanitize_json_string(json_string)  # Sanitize the JSON string
        print(json_string)
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON after sanitization: {e}")
            return None
    else:
        print("JSON markers not found in the text.")
        return None


def extract_json_with_regex(text: str) -> Union[dict, None]:
    # Regular expression to find JSON objects in the text (supports recursion)
    json_pattern = r"\{(?:[^{}]|(?R))*\}"

    # Search for the first JSON object match
    match = re.search(json_pattern, text)

    if match:
        try:
            # Parse the JSON string and return it as a dictionary
            return json.loads(match.group())
        except json.JSONDecodeError:
            print("Invalid JSON format detected.")
            return None
    else:
        print("No JSON object found in the input text.")
        return None


def extract_json(text: str) -> dict | None:
    json_data = extract_json_with_markers(text)
    if json_data is None:
        json_data = extract_json_with_regex(text)
    if json_data is None:
        raise ValueError("No valid JSON object found in the input text.")
    return json_data
