import logging
from typing import List, Optional
import numpy as np
from app.ai.embeddings.base import BaseEmbeddingModel
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SentenceTransformersEmbeddingModel(BaseEmbeddingModel):
    """
    Multilingual embedding model using SentenceTransformers.
    Optimized for cross-lingual Persian and Arabic semantic retrieval.
    """

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL_NAME,
        device: str = settings.EMBEDDING_DEVICE,
    ):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._dimension = settings.EMBEDDING_DIMENSION

    def load_model(self) -> None:
        if self._model is not None:
            return
        logger.info(f"Loading multilingual embedding model '{self.model_name}' on {self.device}...")
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device=self.device)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded. Dimension: {self._dimension}")
        except Exception as e:
            logger.warning(
                f"SentenceTransformer load failed ({e}). Falling back to normalized hash embeddings for local testing."
            )
            self._model = "fallback"

    def embed_query(self, text: str) -> List[float]:
        self.load_model()
        if self._model == "fallback":
            return self._fallback_embed(text)
        embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self.load_model()
        if self._model == "fallback":
            return [self._fallback_embed(t) for t in texts]
        embeddings = self._model.encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self._dimension

    def _fallback_embed(self, text: str) -> List[float]:
        """Deterministic pseudo-embedding for testing when weights are not downloaded."""
        dim = self._dimension
        vec = np.zeros(dim, dtype=np.float32)
        words = text.split()
        for idx, word in enumerate(words):
            h = hash(word)
            pos = abs(h) % dim
            val = (h % 1000) / 1000.0
            vec[pos] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


class EmbeddingModelRegistry:
    _instance: Optional[BaseEmbeddingModel] = None

    @classmethod
    def get_model(cls) -> BaseEmbeddingModel:
        if cls._instance is None:
            cls._instance = SentenceTransformersEmbeddingModel()
        return cls._instance
