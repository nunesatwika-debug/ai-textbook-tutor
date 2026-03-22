import os
import faiss
import numpy as np
from src.utils import save_json, load_json

class VectorStore:
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []

    def build(self, embeddings: np.ndarray, metadata: list):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # cosine-like with normalized vectors
        self.index.add(embeddings.astype("float32"))
        self.metadata = metadata

    def save(self):
        if self.index is None:
            raise ValueError("Index is not built.")
        faiss.write_index(self.index, self.index_path)
        save_json(self.metadata_path, self.metadata)

    def load(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(self.index_path)
        self.index = faiss.read_index(self.index_path)
        self.metadata = load_json(self.metadata_path) or []

    def search(self, query_embedding, top_k: int = 10):
        if self.index is None:
            raise ValueError("Index is not loaded.")

        query_embedding = np.array([query_embedding]).astype("float32")
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)

        return results