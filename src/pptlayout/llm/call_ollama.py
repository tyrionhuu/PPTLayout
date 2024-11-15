import os

import ollama
from ollama import Options


def call_ollama(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    images: list[str] | None = None,
    json: bool = False,
    # top_p: float = 0.9,
) -> str:
    options = Options(
        temperature=temperature,
        num_ctx=max_tokens,
        # top_p=top_p,
    )
    image_flag = False
    if images is not None:
        image_flag = True
    if image_flag is False:
        # response = ollama.chat(
        #     model=model_name,
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a helpful json Powerpoint layout generator",
        #         },
        #         {"role": "user", "content": prompt},
        #     ],
        #     options=options,
        # )["message"]["content"]
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
        # response = ollama.chat(
        #     model=model_name,
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a helpful json Powerpoint layout generator",
        #         },
        #         {"role": "user", "content": prompt},
        #         {"role": "user", "content": image},
        #     ],
        #     options=options,
        # )["message"]["content"]
        response = ollama.generate(
            model=model_name,
            prompt=prompt,
            images=images,
            options=options,
            format="json" if json else "",
        )["response"]
        return response


def generate_slide_layout_suggestions(
    model_name: str | None = None,
    prompt: str = "",
    temperature: float = 0.8,
    max_tokens: int = 32000,
    images: list[str] | None = None,
    # top_p: float = 0.9,
) -> str:
    if images is None:
        if model_name is None:
            model_name = "llama3.1:8b"
        return call_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        if model_name is None:
            model_name = "llama3.2-vision:11b"
        return call_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=images,
        )
