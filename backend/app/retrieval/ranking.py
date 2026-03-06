"""Memory ranker using weighted fusion."""

from datetime import datetime, timezone

from app.models.memory import Memory


class Ranker:
    """Rank memories using weighted fusion of multiple signals."""

    # Default weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "semantic_relevance": 0.40,
        "recency": 0.20,
        "confidence": 0.15,
        "salience": 0.15,
        "source_trust": 0.10,
    }

    _SOURCE_TRUST: dict[str, float] = {
        "gmail": 0.85,
        "calendar": 0.90,
        "notion": 0.80,
        "meeting": 0.75,
        "notes": 0.70,
    }

    def rank(
        self,
        memories: list[Memory],
        query: str,
        weights: dict[str, float] | None = None,
    ) -> list[Memory]:
        """Return *memories* sorted by composite score descending."""
        w = weights or self.DEFAULT_WEIGHTS
        now = datetime.now(timezone.utc)

        scored: list[tuple[float, Memory]] = []
        for mem in memories:
            semantic = self._semantic_score(mem, query)
            recency = self._recency_score(mem, now)
            confidence = mem.confidence or 0.5
            salience = mem.salience_score or 0.5
            source_trust = self._SOURCE_TRUST.get(mem.source_type or "", 0.7)

            composite = (
                w.get("semantic_relevance", 0.4) * semantic
                + w.get("recency", 0.2) * recency
                + w.get("confidence", 0.15) * confidence
                + w.get("salience", 0.15) * salience
                + w.get("source_trust", 0.1) * source_trust
            )
            scored.append((composite, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored]

    @staticmethod
    def _semantic_score(memory: Memory, query: str) -> float:
        """Simple keyword overlap as a proxy for semantic relevance."""
        if not query or not memory.content:
            return 0.0
        query_words = set(query.lower().split())
        content_words = set(memory.content.lower().split())
        overlap = query_words & content_words
        return len(overlap) / max(len(query_words), 1)

    @staticmethod
    def _recency_score(memory: Memory, now: datetime) -> float:
        """Exponential decay: score = 1 for brand new, ~0.5 at 7 days."""
        if memory.created_at is None:
            return 0.5
        created = memory.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_days = (now - created).total_seconds() / 86400
        import math  # noqa: PLC0415

        return math.exp(-0.1 * age_days)
