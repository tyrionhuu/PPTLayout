import os

import ollama
from ollama import Options

# from json import dumps

# from tqdm import tqdm

# from pptlayout.extractors.run_extractors import run_extractors

# from .prompts import build_slide_layout_suggestion_prompts


def generate_slide_layout(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    images: list[str] | None = None,
    json: bool = False,
    # top_p: float = 0.9,
) -> str:
    model_name = get_model_name(model_name, images)

    options = Options(
        temperature=temperature,
        num_ctx=max_tokens,
        # top_p=top_p,
    )

    if images is None:
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            options=options,
            format="json" if json else "",
        )["response"]
        return response
    else:
        if images is None:
            raise ValueError("image is None")
        for image in images:
            if not os.path.exists(image):
                raise ValueError(f"Image file not found: {image}")
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            images=images,
            options=options,
            format="json" if json else "",
        )["response"]
        return response


def get_model_name(model_name: str | None, images: list[str] | None) -> str:
    if images is None:
        if model_name is None:
            return "llama3.1:8b"
    else:
        if model_name is None:
            return "llama3.2-vision:11b"
    return model_name


# def process_pptx(pptx_path, output_dir, model_name="llama3.1:8b", temperature=0.5):
#     """
#     Extracts slide information from a PPTX file, generates layout suggestions using a specified model,
#     and saves the output to text files.

#     Parameters:
#     - pptx_path (str): Path to the PPTX file.
#     - output_dir (str): Directory to save the output suggestions.
#     - model_name (str): Name of the model to generate slide layout suggestions.
#     - temperature (float): Temperature setting for the model to control randomness.

#     Returns:
#     - suggestions_list (list): List of layout suggestions for each slide.
#     """
#     # Run extractors to get slide information
#     info = run_extractors(pptx_path, "emu")
#     print(dumps(info, indent=4))

#     # Prepare for storing suggestions
#     suggestions_list = []

#     for slide_info in tqdm(info["slides"], desc="Processing slides"):
#         slide_id = slide_info["slide_id"]
#         slide_output_dir = os.path.join(output_dir, f"{slide_id}")
#         suggestions_file_path = os.path.join(slide_output_dir, "suggestions.txt")

#         # Check if suggestions already exist
#         if os.path.exists(suggestions_file_path):
#             with open(suggestions_file_path, "r") as f:
#                 suggestions = f.read()
#             suggestions_list.append(suggestions)
#             continue

#         # Build prompt and generate suggestions
#         prompt = build_slide_layout_suggestion_prompts(
#             json_input=slide_info,
#             slide_width=info["slide_width"],
#             slide_height=info["slide_height"]
#         )
#         suggestions = generate_slide_layout(
#             model_name=model_name,
#             prompt=prompt,
#             temperature=temperature,
#         )
#         suggestions_list.append(suggestions)

#         # Save suggestions
#         os.makedirs(slide_output_dir, exist_ok=True)
#         with open(suggestions_file_path, "w") as f:
#             f.write(suggestions)

#     return suggestions_list

# # Example usage
# pptx_path = "/data/tianyuhu/PPTLayout/data/pptx/ZK7FNUZ33GBBCG7CFVYS56TQCTD72CJR.pptx"
# output_dir = os.path.join(os.curdir, "test_output")
# suggestions = process_pptx(pptx_path, output_dir)
