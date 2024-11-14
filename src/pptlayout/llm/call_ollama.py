import os

import ollama
from ollama import Options


def call_ollama(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    image_flag: bool = False,
    image: str | None = None,
    # top_p: float = 0.9,
) -> str:
    options = Options(
        temperature=temperature,
        num_ctx=max_tokens,
        # top_p=top_p,
    )
    if image_flag is False:
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful json Powerpoint layout generator",
                },
                {"role": "user", "content": prompt},
            ],
            options=options,
        )["message"]["content"]
        return response
    else:
        if image is None:
            raise ValueError("image is None")
        if not os.path.exists(image):
            raise FileNotFoundError(f"image not found: {image}")
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful json Powerpoint layout generator",
                },
                {"role": "user", "content": prompt},
                {"role": "user", "content": image},
            ],
            options=options,
        )["message"]["content"]
        return response


def generate_slide_layout_suggestions(
    model_name: str | None = None,
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    image: str | None = None,
    # top_p: float = 0.9,
) -> str:
    if image is None:
        if model_name is None:
            model_name = "llama3.1:8b"
        return call_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            image_flag=False,
        )
    else:
        if model_name is None:
            model_name = "llama3.2-vision:11b"
        return call_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            image_flag=True,
            image=image,
        )
