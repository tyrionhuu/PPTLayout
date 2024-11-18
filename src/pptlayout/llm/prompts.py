from json import dumps

slide_layout_suggestion_prompts = (
    "Given an input in the form of a JSON format describing the layout of a PowerPoint slide, "
    + "analyze the input and suggest an improved version of the layout in JSON format. \n"
    + "Only change existing layout parameters, such as position, size, and content, without adding or removing elements. \n"
    + "The improvements should enhance the slide's readability, visual appeal, and overall coherence. \n"
    + "Ensure that consistent alignment, spacing, visual hierarchy, and design principles are maintained. \n"
    + "The input JSON format will include information about the slide layout, such as the position, size, and content of each element. \n"
    + "In the json, all the quotes for keys and values should be double quotes. \n"
    + "The slide width is {} and the slide height is {}. \n"
    + "The top left corner of the slide is considered the origin (0, 0). \n"
    + "The input JSON is: \n"
    + "```json\n"
    + "{}\n"
    + "```\n"
    # + "Some suggestions for the layout are: \n"
    # + "{}\n"
    + "Now generate the output JSON: \n"
)

vision_slide_layout_suggestion_prompts = (
    "Given an image of a slide with grid for you to better locate shapes and a JSON format describing the layout of a PowerPoint slide, "
    + "analyze the input and suggest an improved version of the layout in JSON format. \n"
    + "Only change existing layout parameters, such as position, size, and content, without adding or removing elements. \n"
    + "The improvements should enhance the slide's readability, visual appeal, and overall coherence. \n"
    + "Ensure that consistent alignment, spacing, visual hierarchy, and design principles are maintained. \n"
    + "The input JSON format will include information about the slide layout, such as the position, size, and content of each element. \n"
    + "In the json, all the quotes for keys and values should be double quotes. \n"
    + "The slide width is {} and the slide height is {}. \n"
    + "The top left corner of the slide is considered the origin (0, 0). \n"
    + "The input JSON is: \n"
    + "```json\n"
    + "{}\n"
    + "```\n"
    # + "Some suggestions for the layout are: \n"
    # + "{}\n"
    + "Now generate the output JSON: \n"
)


def build_slide_layout_suggestion_prompts(
    json_input: str,
    slide_width: int | float,
    slide_height: int | float,
    # suggestion: str,
    image_flag: bool = False,
) -> str:
    if image_flag is False:
        return slide_layout_suggestion_prompts.format(
            slide_width,
            slide_height,
            dumps(json_input, indent=4),
        )
    else:
        return vision_slide_layout_suggestion_prompts.format(
            slide_width,
            slide_height,
            dumps(json_input, indent=4),
        )
