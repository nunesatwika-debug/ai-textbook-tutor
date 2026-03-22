import requests
from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

class LLMClient:
    def __init__(self, api_key: str = LLM_API_KEY, base_url: str = LLM_BASE_URL, model: str = LLM_MODEL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.base_url or not self.api_key:
            return (
                "Generation endpoint not configured.\n\n"
                "Compressed context prepared successfully.\n"
                "Set LLM_BASE_URL and LLM_API_KEY in .env to enable final answer generation."
            )

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            return f"Final answer generation failed: {e}"
        except Exception as e:
            return f"Unexpected generation error: {e}"