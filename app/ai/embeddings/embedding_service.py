import re
from typing import List, Tuple
from app.ai.embeddings.base import TextChunk
from app.ai.embeddings.model_loader import EmbeddingModelRegistry
from app.utils.text_normalization import PersianArabicNormalizer
from app.core.config import get_settings

settings = get_settings()


class TextChunker:
    """
    Intelligent sentence and paragraph chunker for historical Persian and Arabic texts.
    Respects sentence boundaries (dots, commas, verses, Arabic question marks).
    """

    SENTENCE_SPLIT_REGEX = re.compile(r"([\.!\?؟\n]+|[\.!\?؟]\s+)")

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size_words: int = settings.CHUNK_SIZE_WORDS,
        overlap_words: int = settings.CHUNK_OVERLAP_WORDS,
    ) -> List[TextChunk]:
        if not text or not text.strip():
            return []

        # Split into approximate sentences / phrases
        sentences = [s.strip() for s in cls.SENTENCE_SPLIT_REGEX.split(text) if s.strip()]

        chunks: List[TextChunk] = []
        current_words: List[str] = []
        chunk_idx = 0

        for sentence in sentences:
            words = sentence.split()
            if len(current_words) + len(words) > chunk_size_words and current_words:
                chunk_str = " ".join(current_words)
                norm_str = PersianArabicNormalizer.normalize_for_search(chunk_str)
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_idx,
                        text=chunk_str,
                        normalized_text=norm_str,
                        word_count=len(current_words),
                    )
                )
                chunk_idx += 1
                # Overlap: keep last N words
                current_words = current_words[-overlap_words:] if overlap_words > 0 else []

            current_words.extend(words)

        # Residual words
        if current_words:
            chunk_str = " ".join(current_words)
            norm_str = PersianArabicNormalizer.normalize_for_search(chunk_str)
            chunks.append(
                TextChunk(
                    chunk_index=chunk_idx,
                    text=chunk_str,
                    normalized_text=norm_str,
                    word_count=len(current_words),
                )
            )

        return chunks


class EmbeddingService:
    @classmethod
    def generate_embeddings_for_transcription(
        cls, text: str
    ) -> List[Tuple[TextChunk, List[float]]]:
        """
        Chunks transcription text and computes vector embeddings for each chunk.
        """
        chunks = TextChunker.chunk_text(text)
        if not chunks:
            return []

        model = EmbeddingModelRegistry.get_model()
        # Embed normalized chunk texts for optimal cross-lingual match
        normalized_texts = [c.normalized_text for c in chunks]
        vectors = model.embed_documents(normalized_texts)

        return list(zip(chunks, vectors))

    @classmethod
    def generate_query_embedding(cls, query: str) -> List[float]:
        norm_query = PersianArabicNormalizer.normalize_for_search(query)
        model = EmbeddingModelRegistry.get_model()
        return model.embed_query(norm_query)
