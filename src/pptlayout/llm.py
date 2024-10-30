import ollama
from ollama import Options


class OllamaClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def response(
        self,
        prompt: str,
        temperature: float = 0.5,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
    ):
        return ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options=Options(
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            ),
        )["response"]
