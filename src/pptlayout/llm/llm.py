import os

import ollama
from ollama import Options
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

model_dir = "/data/share_weight/Qwen2-VL-7B-Instruct"


def call_llm(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    images: list[str] | None = None,
    json: bool = False,
    # top_p: float = 0.9,
) -> str:
    model_name = get_model_name(model_name=model_name, images=images)

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
    model_name = get_model_name(model_name=model_name, images=images)

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
    # model_dir = "/data/share_weight/Qwen2-VL-7B-Instruct"

    # default: Load the model on the available device(s)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_dir,
        torch_dtype="auto",
        device_map="auto",
    ).to("cuda")

    min_pixels = 256 * 28 * 28
    max_pixels = 1280 * 28 * 28
    processor = AutoProcessor.from_pretrained(
        model_dir, min_pixels=min_pixels, max_pixels=max_pixels
    )
    messages = generate_qwen2_vl_message(images=images, prompt=prompt)
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
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
) -> list[dict]:
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


# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# test_image = "/data/tianyuhu/PPTLayout/notebooks/test_input/image_grid.jpg"
# prompt = "Take the grid as reference. Tell me what is wrong with the layout of the slide. Be concise."

# suggestion = call_llm(
#     model_name="Qwen2-VL-7B-Instruct",
#     prompt=prompt,
#     images=[test_image],
#     # json=True,
# )
# print(suggestion)
