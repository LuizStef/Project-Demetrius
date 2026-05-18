import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticMemory:
    def __init__(self):
        self.__model = SentenceTransformer("all-MiniLM-L6-v2")
        self.__index = faiss.IndexFlatL2(384)
        self.__memories = []

    def add(self, text):
        embedding = self.__model.encode([text])
        self.__index.add(np.array(embedding, dtype=np.float32))
        self.__memories.append(text)

    def search(self, query, k=3):
        if len(self.__memories) == 0:
            return []
        embedding = self.__model.encode([query])
        distances, indices = self.__index.search(
            np.array(embedding, dtype=np.float32), int(k)
        )
        return [self.__memories[i] for i in indices[0] if i < len(self.__memories)]