layout_suggestion_prompts = (
    "Given an input in the form of a JSON format describing the layout of a PowerPoint presentation, "
    + "analyze the input and suggest an improved version of the layout in JSON format. "
    + "Along with the revised JSON output, provide a list of changes that were made, including explanations for each change. "
    + "The improvements should enhance the slide's readability, visual appeal, and overall coherence. "
    + "Ensure that consistent alignment, spacing, visual hierarchy, and design principles are maintained."
    + "The input JSON format will include information about the slide layout, such as the position, size, and content of each element. "
    + "The top left corner of the slide is considered the origin (0, 0). "
    + "The input JSON is formatted as follows: "
    + "```json\n"
    + "{}"
    + "\n```"
)

slide_layout_suggestion_prompts = (
    "Given an input in the form of a JSON format describing the layout of a PowerPoint slide, "
    + "analyze the input and suggest an improved version of the layout in JSON format. "
    + "Along with the revised JSON output, provide a list of changes that were made, including explanations for each change. "
    + "Only change existing layout parameters, such as position, size, and content, without adding or removing elements. "
    + "The improvements should enhance the slide's readability, visual appeal, and overall coherence. "
    + "Ensure that consistent alignment, spacing, visual hierarchy, and design principles are maintained."
    + "The input JSON format will include information about the slide layout, such as the position, size, and content of each element. "
    + "The slide width is {} and the slide height is {}. "
    + "The top left corner of the slide is considered the origin (0, 0). "
    + "The input JSON is formatted as follows: "
    + "```json\n"
    + "{}"
    + "\n```"
)

vision_slide_layout_suggestion_prompts = (
    "Given an image of a slide and a JSON format describing the layout of a PowerPoint slide, "
    + "analyze the input and suggest an improved version of the layout in JSON format. "
    + "Along with the revised JSON output, provide a list of changes that were made, including explanations for each change. "
    + "Only change existing layout parameters, such as position, size, and content, without adding or removing elements. "
    + "The improvements should enhance the slide's readability, visual appeal, and overall coherence. "
    + "Ensure that consistent alignment, spacing, visual hierarchy, and design principles are maintained."
    + "The input JSON format will include information about the slide layout, such as the position, size, and content of each element. "
    + "The slide width is {} and the slide height is {}. "
    + "The top left corner of the slide is considered the origin (0, 0). "
    + "The input JSON is formatted as follows: "
    + "```json\n"
    + "{}"
    + "\n```"
)


def build_layout_suggestion_prompts(
    json_input: str,
    vision_flag: bool = False,
) -> str:
    if vision_flag is False:
        return layout_suggestion_prompts.format(json_input)
    else:
        return vision_slide_layout_suggestion_prompts.format(json_input)


def build_slide_layout_suggestion_prompts(
    json_input: str, slide_width: int | float, slide_height: int | float
) -> str:
    return slide_layout_suggestion_prompts.format(json_input, slide_width, slide_height)
