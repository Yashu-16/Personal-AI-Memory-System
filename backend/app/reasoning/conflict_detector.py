"""Conflict detector – find contradicting memories."""

import re
from dataclasses import dataclass

from app.models.memory import Memory


@dataclass
class Conflict:
    memory_a: Memory
    memory_b: Memory
    reason: str


class ConflictDetector:
    """Detect contradictions between memories about the same entity/topic."""

    _NEGATION_PAIRS = [
        ("yes", "no"),
        ("true", "false"),
        ("confirmed", "cancelled"),
        ("approved", "rejected"),
        ("will", "won't"),
        ("can", "cannot"),
        ("is", "is not"),
        ("completed", "pending"),
    ]

    def detect(self, memories: list[Memory]) -> list[Conflict]:
        """Return conflicts found among *memories*."""
        conflicts: list[Conflict] = []
        for i, mem_a in enumerate(memories):
            for mem_b in memories[i + 1 :]:
                conflict = self._check_pair(mem_a, mem_b)
                if conflict:
                    conflicts.append(conflict)
        return conflicts

    def _check_pair(self, mem_a: Memory, mem_b: Memory) -> Conflict | None:
        """Check if two memories contradict each other."""
        content_a = (mem_a.content or "").lower()
        content_b = (mem_b.content or "").lower()

        # Simple heuristic: check for negation pairs in the same topic
        for positive, negative in self._NEGATION_PAIRS:
            if positive in content_a and negative in content_b:
                return Conflict(
                    memory_a=mem_a,
                    memory_b=mem_b,
                    reason=f"Conflicting: '{positive}' vs '{negative}'",
                )
            if negative in content_a and positive in content_b:
                return Conflict(
                    memory_a=mem_a,
                    memory_b=mem_b,
                    reason=f"Conflicting: '{negative}' vs '{positive}'",
                )
        return None
