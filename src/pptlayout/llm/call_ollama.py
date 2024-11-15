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
