import json
import re


def extract_json_with_markers(text: str) -> dict | None:
    start_marker = "```json"
    end_marker = "```"

    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index + len(start_marker))

    if start_index != -1 and end_index != -1:
        json_string = text[start_index + len(start_marker) : end_index].strip()
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("JSON markers not found in the text.")
        return None


def extract_json_with_regex(text: str) -> dict | None:
    json_pattern = r"```json(.*?)```"
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        json_string = match.group(1).strip()
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No JSON found in the text with markers.")
        return None


def extract_json(text: str) -> dict | None:
    json_data = extract_json_with_markers(text)
    if json_data is None:
        json_data = extract_json_with_regex(text)
    # check if json_data is None and return an empty dictionary if so
    if json_data is None:
        json_data = {}
    return json_data
