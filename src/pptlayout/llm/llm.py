import os

import ollama
from ollama import Options
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

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

    if images is None:
        response = generate_no_image(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json=json,
        )
    else:
        if images is None:
            raise ValueError("image is None")
        for image in images:
            if not os.path.exists(image):
                raise ValueError(f"Image file not found: {image}")
        response = generate_with_image(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=images,
            json=json,
        )
    return response


def generate_with_image(
    model_name: str = "llama3.2-vision:11b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    images: list[str] | None = None,
    json: bool = False,
) -> str:
    model_name = get_model_name(model_name, images)

    if model_name == "Qwen2-VL-7B-Instruct":
        response = generate_qwen2_vl(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            # json=json,
            images=images,
        )
        return response
    else:
        options = Options(
            temperature=temperature,
            num_ctx=max_tokens,
        )
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            images=images,
            options=options,
            format="json" if json else "",
        )["response"]
        return response


def generate_no_image(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    json: bool = False,
) -> str:
    if model_name == "Qwen2-VL-7B-Instruct":
        response = generate_qwen2_vl(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            # json=json,
        )
        return response
    else:
        options = Options(
            temperature=temperature,
            num_ctx=max_tokens,
        )
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            options=options,
            format="json" if json else "",
        )["response"]
        return response


def generate_qwen2_vl(
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    # json: bool = False,
    images: list[str] | None = None,
) -> str:
    # model_dir = os.path.abspath("/data/tianyuhu/models/Qwen/Qwen2.5-Coder-7B-Instruct-GPTQ-Int4")
    model_dir = "/data/share_weight/Qwen2-VL-7B-Instruct"

    # default: Load the model on the available device(s)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_dir,
        torch_dtype="auto",
        device_map="auto",
    )
    min_pixels = 256 * 28 * 28
    max_pixels = 1280 * 28 * 28
    processor = AutoProcessor.from_pretrained(
        model_dir, min_pixels=min_pixels, max_pixels=max_pixels
    )
    messages = generate_qwen2_vl_message(images, prompt)
    text = processor.apply_chat_template(
        str(messages), tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")
    # Inference: Generation of the output
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=temperature,
        # response_format={"type": "json_object"} if json else {"type": "text"},
    )
    generated_ids_trimmed = [
        out_ids[len(in_ids) :]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )
    # print(output_text)
    return output_text


def generate_qwen2_vl_message(
    images: list[str] | None = None,
    prompt: str = "",
):
    if images is None:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is the problem with the layout of this slide?",
                    },
                ],
            }
        ]
    else:
        content = []
        for image in images:
            content.append(
                {
                    "type": "image",
                    "image": image,
                }
            )
        content.append(
            {
                "type": "text",
                "text": prompt,
            }
        )
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
    return messages


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
