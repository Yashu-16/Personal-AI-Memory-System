"""Embedding service with OpenAI and sentence-transformers fallback."""

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_CACHE: dict[str, list[float]] = {}
_TARGET_DIM = 1536


class EmbeddingService:
    """Produce fixed-size (1536-dim) text embeddings."""

    _model: Any = None  # sentence-transformers model, lazy-loaded

    async def get_embedding(self, text: str) -> list[float]:
        """Return a 1536-dimensional embedding for *text*."""
        cache_key = text[:512]
        if cache_key in _CACHE:
            return _CACHE[cache_key]

        embedding: list[float]

        if settings.USE_OPENAI_EMBEDDINGS and settings.OPENAI_API_KEY:
            embedding = await self._openai_embedding(text)
        else:
            embedding = self._local_embedding(text)

        # Pad or truncate to TARGET_DIM
        if len(embedding) < _TARGET_DIM:
            embedding = embedding + [0.0] * (_TARGET_DIM - len(embedding))
        elif len(embedding) > _TARGET_DIM:
            embedding = embedding[:_TARGET_DIM]

        _CACHE[cache_key] = embedding
        return embedding

    @staticmethod
    async def _openai_embedding(text: str) -> list[float]:
        """Get embedding from OpenAI text-embedding-3-small."""
        from openai import AsyncOpenAI  # type: ignore

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            input=text[:8191],
            model="text-embedding-3-small",
        )
        return response.data[0].embedding

    def _local_embedding(self, text: str) -> list[float]:
        """Get embedding from a local sentence-transformers model."""
        if EmbeddingService._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                EmbeddingService._model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info("Loaded sentence-transformers model: %s", settings.EMBEDDING_MODEL)
            except Exception as exc:
                logger.warning("sentence-transformers unavailable: %s", exc)
                return self._fallback_embedding(text)

        try:
            vector = EmbeddingService._model.encode(text, convert_to_numpy=True).tolist()
            return [float(v) for v in vector]
        except Exception as exc:
            logger.warning("Encoding failed: %s", exc)
            return self._fallback_embedding(text)

    @staticmethod
    def _fallback_embedding(text: str) -> list[float]:
        """Simple hash-based pseudo-embedding for environments without ML libs."""
        import hashlib  # noqa: PLC0415

        digest = hashlib.sha256(text.encode()).digest()
        # Repeat the 32-byte digest to fill 1536 floats
        values: list[float] = []
        while len(values) < _TARGET_DIM:
            for byte in digest:
                values.append((byte / 255.0) * 2 - 1)
                if len(values) >= _TARGET_DIM:
                    break
        return values[:_TARGET_DIM]
