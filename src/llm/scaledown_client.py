import requests
from src.config import SCALEDOWN_API_KEY, SCALEDOWN_COMPRESS_URL, LLM_MODEL

class ScaleDownClient:
    def __init__(self, api_key: str = SCALEDOWN_API_KEY):
        self.api_key = api_key

    def compress(self, context: str, prompt: str, model: str = LLM_MODEL, rate: str = "auto") -> dict:
        if not self.api_key:
            raise ValueError("Missing SCALEDOWN_API_KEY in .env")

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "context": context,
            "prompt": prompt,
            "model": model,
            "scaledown": {
                "rate": rate
            }
        }

        response = requests.post(
            SCALEDOWN_COMPRESS_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()