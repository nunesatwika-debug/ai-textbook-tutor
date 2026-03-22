from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    def embed_query(self, query: str):
        return self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]