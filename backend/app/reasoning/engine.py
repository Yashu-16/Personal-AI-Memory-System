"""Reasoning engine – orchestrates answer generation and conflict detection."""

from dataclasses import dataclass, field

from app.models.memory import Memory
from app.reasoning.answer_generator import AnswerGenerator
from app.reasoning.conflict_detector import ConflictDetector
from app.retrieval.query_parser import QueryIntent


@dataclass
class ReasoningResult:
    answer: str
    confidence: float
    supporting_memories: list[Memory]
    suggested_actions: list[str] = field(default_factory=list)


class ReasoningEngine:
    """Combine retrieval results into a final answer."""

    def __init__(self) -> None:
        self._generator = AnswerGenerator()
        self._conflict_detector = ConflictDetector()

    async def reason(
        self,
        query: str,
        memories: list[Memory],
        intent: QueryIntent,
    ) -> ReasoningResult:
        """Produce a grounded answer with suggested actions."""
        # Detect conflicts (informational, not blocking)
        conflicts = self._conflict_detector.detect(memories[:20])

        answer, confidence, actions = await self._generator.generate(
            query=query, memories=memories
        )

        if conflicts:
            actions.append(f"Note: {len(conflicts)} potential conflict(s) detected in memories")

        return ReasoningResult(
            answer=answer,
            confidence=confidence,
            supporting_memories=memories[:10],
            suggested_actions=actions,
        )
