"""Salience scorer for memory content."""

import re


class SalienceScorer:
    """Compute a 0-1 salience score for a memory."""

    _URGENCY_RE = re.compile(
        r"\b(?:urgent|asap|critical|important|deadline|overdue|immediately|priority)\b",
        re.IGNORECASE,
    )
    _PERSON_RE = re.compile(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)+\b")

    def score(
        self,
        memory_content: str,
        entities: list,
        commitment_count: int,
        task_count: int,
        dates: list,
    ) -> float:
        """Return a salience score between 0.0 and 1.0.

        Scoring components:
        - Named entities present           → +0.15 per entity, cap 0.3
        - Commitment present               → +0.25 per commitment, cap 0.25
        - Task present                     → +0.20 per task, cap 0.20
        - Urgency keyword found            → +0.15
        - Deadline date found              → +0.10
        - Content length > 100 chars       → +0.05
        """
        score = 0.0

        # Entity contribution
        entity_bonus = min(len(entities) * 0.15, 0.30)
        score += entity_bonus

        # Commitment contribution
        commitment_bonus = min(commitment_count * 0.25, 0.25)
        score += commitment_bonus

        # Task contribution
        task_bonus = min(task_count * 0.20, 0.20)
        score += task_bonus

        # Urgency keywords
        if self._URGENCY_RE.search(memory_content):
            score += 0.15

        # Deadline dates
        deadline_dates = [d for d in dates if getattr(d, "is_deadline", False)]
        if deadline_dates:
            score += 0.10

        # Length bonus
        if len(memory_content) > 100:
            score += 0.05

        return min(round(score, 4), 1.0)
