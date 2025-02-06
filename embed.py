from sentence_transformers import SentenceTransformer
from typing import List

class EmbedManager:
    def __init__(self):
        self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

    def embed(self, text: str) -> List[float]:
        return self.model.encode([text]).flatten().tolist()
