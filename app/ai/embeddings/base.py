from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class TextChunk(BaseModel):
    chunk_index: int
    text: str
    normalized_text: str
    word_count: int


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        pass
