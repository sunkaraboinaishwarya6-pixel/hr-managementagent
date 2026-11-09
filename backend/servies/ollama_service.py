import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_qwen(prompt):
    data = {
        "model": "qwen3:1.7b",
        "prompt": prompt,
        "stream": True,
    }

    response = requests.post(
        OLLAMA_URL,
        json={**data, "think": False},
        stream=True,
        timeout=120
    )

    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            text = chunk.get("response", "")

            if text:
                yield text