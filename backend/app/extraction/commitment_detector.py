"""Commitment detector using keyword patterns."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.utils.datetime_utils import parse_date


@dataclass
class DetectedCommitment:
    subject: str
    action: str
    person: Optional[str] = None
    deadline: Optional[datetime] = None
    raw_text: str = ""


class CommitmentDetector:
    """Detect first-person commitments in text using regex heuristics."""

    # Commitment trigger phrases
    _TRIGGERS = [
        r"I(?:'ll| will| need to| should| must| promise to| am going to|'m going to)",
        r"(?:will|shall) (?:send|complete|finish|deliver|submit|write|call|email|review|update|schedule|fix|prepare|create|make|do|handle|follow up|reach out|contact)",
        r"(?:Let me|I'll make sure to|I commit to|I plan to)",
    ]
    _TRIGGER_RE = re.compile(
        r"(?:" + "|".join(_TRIGGERS) + r")\s+(.{5,200}?)(?:[.!?]|$)",
        re.IGNORECASE,
    )

    # Deadline indicators within a commitment sentence
    _DEADLINE_RE = re.compile(
        r"\b(?:by|before|due|deadline|until|no later than)\s+(.{3,60}?)(?:[,;.!?]|$)",
        re.IGNORECASE,
    )

    # Person indicator: "to <Name>" or "@Name"
    _PERSON_RE = re.compile(r"(?:to|for|@)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", re.IGNORECASE)

    def detect(self, text: str) -> list[DetectedCommitment]:
        """Return a list of detected commitments."""
        results: list[DetectedCommitment] = []

        for sentence in re.split(r"(?<=[.!?\n])\s+", text):
            sentence = sentence.strip()
            if not sentence:
                continue

            m = self._TRIGGER_RE.search(sentence)
            if not m:
                continue

            action_fragment = m.group(1).strip()
            # Truncate at next sentence-like boundary
            action_fragment = re.split(r"(?<=[.!?])\s", action_fragment)[0].strip()

            # Deadline extraction
            deadline: Optional[datetime] = None
            deadline_m = self._DEADLINE_RE.search(sentence)
            if deadline_m:
                deadline = parse_date(deadline_m.group(1))

            # Person extraction
            person: Optional[str] = None
            person_m = self._PERSON_RE.search(sentence)
            if person_m:
                person = person_m.group(1).strip()

            results.append(
                DetectedCommitment(
                    subject="I",
                    action=action_fragment,
                    person=person,
                    deadline=deadline,
                    raw_text=sentence,
                )
            )

        return results
