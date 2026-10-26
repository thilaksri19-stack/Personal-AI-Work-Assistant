from importlib import import_module

MODEL_NAME = "llama3.2:3b"


def _chat(**kwargs):
    try:
        ollama = import_module("ollama")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency: install it with 'pip install ollama'."
        ) from exc
    return ollama.chat(**kwargs)


def generate_answer(prompt):

    response = _chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]