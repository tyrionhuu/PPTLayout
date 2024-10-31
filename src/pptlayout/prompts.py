from utils import LAYOUT_DOMAIN, canvas_size

PREAMBLE = (
    "Please give me a html powerpoint layout based on the given information. "
    "Follow the format in the examples strictly. Generate the layout in the **exact HTML structure provided**, with matching indentation and CSS style properties. Do not add or omit any tags or modify the structure in any way. "
    "You need to ensure that the generated layout looks realistic, with elements well aligned and avoiding unnecessary overlap.\n"
    "Task Description: {}\n"
    "Layout Domain: {} layout\n"
    "Canvas Size: canvas width is {}px, canvas height is {}px"
)

EXAMPLE_ELEMENT = "-Examples-"
INPUT_ELEMENT = "Input:\n"
OUTPUT_ELEMENT = "Output:\n"
DATA = "-Real Data-"
MESSAGE = "Please output an HTML structure that exactly matches the format of the provided examples, without using any variables, loops, or dynamic generation code. Use static values and follow the structure, indentation, and CSS styling exactly as shown in the example outputs. Here is the input constraint: Only provide a single block of static HTML as the output, with no explanations or placeholders. \n Here is the contraints.\n"


def build_prompt(
    serializer,
    exemplars,
    test_data,
    dataset,
    max_length=10000,
    separator_in_samples="\n----------------------------------------------\n",
    separator_between_samples="\n############################################\n",
    pptx_path=None,
):
    prompt = [
        PREAMBLE.format(
            serializer.task_type,
            LAYOUT_DOMAIN[dataset],
            *canvas_size(dataset, pptx_path),
        )
    ]
    prompt.append(EXAMPLE_ELEMENT)
    for i in range(len(exemplars)):
        _prompt = (
            f"Example {i+1}:\n\n"
            + INPUT_ELEMENT
            + serializer.build_input(exemplars[i])
            + separator_in_samples
            + OUTPUT_ELEMENT
            + serializer.build_output(exemplars[i])
        )
        if len(separator_between_samples.join(prompt) + _prompt) <= max_length:
            prompt.append(_prompt)
        else:
            break
    prompt.append(MESSAGE + DATA)
    prompt.append(
        INPUT_ELEMENT
        + serializer.build_input(test_data)
        + separator_in_samples
        + OUTPUT_ELEMENT
    )
    return separator_between_samples.join(prompt)
