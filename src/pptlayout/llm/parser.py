import json
import re


def sanitize_json_string(json_string: str) -> str:
    """Sanitize the JSON string by escaping special characters and ensuring valid JSON format."""
    sanitized_string = re.sub(
        r"[\x00-\x1F\x7F]", " ", json_string
    )  # Remove control characters
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


def extract_json_with_regex(text: str) -> dict | None:
    json_pattern = r"```json(.*?)```"
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        json_string = match.group(1).strip()
        json_string = sanitize_json_string(json_string)  # Sanitize the JSON string

        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON after sanitization: {e}")
            return None
    else:
        print("No JSON found in the text with markers.")
        return None


def extract_json(text: str) -> dict | None:
    json_data = extract_json_with_markers(text)
    if json_data is None:
        json_data = extract_json_with_regex(text)
    if json_data is None:
        json_data = {}
    return json_data
