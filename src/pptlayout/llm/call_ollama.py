import ollama
from ollama import Options

# def call_ollama(
#     model_name: str = "llama3.1:8b", prompt: str = "", options: Options | None = None
# ) -> str:
#     response = ollama.generate(
#         model=model_name,
#         system="You are a helpful html Powerpoint layout generator",
#         prompt=prompt,
#         options=options,
#     )["response"]
#     return response


def call_ollama(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    # top_p: float = 0.9,
) -> str:
    options = Options(
        temperature=temperature,
        num_ctx=max_tokens,
        # top_p=top_p,
    )
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


def generate_slide_layout_suggestions(
    model_name: str = "llama3.1:8b",
    prompt: str = "",
    temperature: float = 0.5,
    max_tokens: int = 32000,
    # top_p: float = 0.9,
) -> str:
    response = call_ollama(
        model_name=model_name,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        # top_p=top_p,
    )
    return response
