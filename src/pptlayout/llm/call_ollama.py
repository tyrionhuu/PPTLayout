import ollama
from ollama import Options


def call_ollama(
    model_name: str = "llama3.1:8b", prompt: str = "", options: Options | None = None
) -> str:
    response = ollama.generate(
        model=model_name,
        system="You are a helpful html Powerpoint layout generator",
        prompt=prompt,
        options=options,
    )["response"]
    return response
