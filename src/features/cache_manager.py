import hashlib
import os
from src.config import CACHE_DIR
from src.utils import save_json, load_json

class CacheManager:
    def _hash_key(self, question: str, mode: str) -> str:
        return hashlib.md5(f"{question}::{mode}".encode("utf-8")).hexdigest()

    def get(self, question: str, mode: str):
        key = self._hash_key(question, mode)
        path = os.path.join(CACHE_DIR, f"{key}.json")
        return load_json(path)

    def set(self, question: str, mode: str, data: dict):
        key = self._hash_key(question, mode)
        path = os.path.join(CACHE_DIR, f"{key}.json")
        save_json(path, data)