from utils import LAYOUT_DOMAIN, canvas_size

PREAMBLE = (
    "Please generate a powerpoint layout based on the given information. "
    "You need to ensure that the generated layout looks realistic, with elements well aligned and avoiding unnecessary overlap.\n"
    "Task Description: {}\n"
    "Layout Domain: {} layout\n"
    "Canvas Size: canvas width is {}px, canvas height is {}px"
)


def build_prompt(
    serializer,
    exemplars,
    test_data,
    dataset,
    max_length=8000,
    separator_in_samples="\n",
    separator_between_samples="\n\n",
    pptx_path=None,
):
    prompt = [
        PREAMBLE.format(
            serializer.task_type,
            LAYOUT_DOMAIN[dataset],
            *canvas_size(dataset, pptx_path),
        )
    ]
    for i in range(len(exemplars)):
        _prompt = (
            serializer.build_input(exemplars[i])
            + separator_in_samples
            + serializer.build_output(exemplars[i])
        )
        if len(separator_between_samples.join(prompt) + _prompt) <= max_length:
            prompt.append(_prompt)
        else:
            break
    prompt.append(serializer.build_input(test_data) + separator_in_samples)
    return separator_between_samples.join(prompt)
