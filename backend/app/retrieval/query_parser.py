"""Query parser – extracts intent and filters from a natural language query."""

import re
from dataclasses import dataclass, field
from typing import Optional


class IntentType:
    FACTUAL = "factual"
    TIMELINE = "timeline"
    COMMITMENT = "commitment"
    PERSON_CENTRIC = "person_centric"
    PROJECT_CENTRIC = "project_centric"
    REFLECTION = "reflection"
    PLANNING = "planning"
    CONFLICT = "conflict"


@dataclass
class QueryIntent:
    intent_type: str
    entities: list[str] = field(default_factory=list)
    time_filter: Optional[str] = None
    source_filter: Optional[str] = None
    keywords: list[str] = field(default_factory=list)


class QueryParser:
    """Parse a natural language query into a structured QueryIntent."""

    _COMMITMENT_RE = re.compile(
        r"\b(?:commit|promise|said|told|owe|due|deadline|by when|when did I agree)\b",
        re.IGNORECASE,
    )
    _TIMELINE_RE = re.compile(
        r"\b(?:when|timeline|history|last time|first time|recent|latest|ago|yesterday|last week)\b",
        re.IGNORECASE,
    )
    _PERSON_RE = re.compile(r"\b(?:about|from|with|by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b")
    _PROJECT_RE = re.compile(r"\b(?:project|sprint|milestone|epic)\b", re.IGNORECASE)
    _REFLECTION_RE = re.compile(r"\b(?:pattern|habit|often|usually|always|trend)\b", re.IGNORECASE)
    _PLANNING_RE = re.compile(r"\b(?:plan|should|next step|todo|priority|upcoming)\b", re.IGNORECASE)
    _CONFLICT_RE = re.compile(r"\b(?:conflict|clash|overlap|double.booked|contradict)\b", re.IGNORECASE)
    _TIME_RE = re.compile(
        r"\b(today|yesterday|this week|last week|this month|last month|\d{4}-\d{2}-\d{2})\b",
        re.IGNORECASE,
    )
    _SOURCE_RE = re.compile(r"\b(?:email|gmail|calendar|notion|meeting|note)\b", re.IGNORECASE)

    def parse(self, query: str) -> QueryIntent:
        """Return a QueryIntent from *query*."""
        # Determine intent
        if self._CONFLICT_RE.search(query):
            intent_type = IntentType.CONFLICT
        elif self._COMMITMENT_RE.search(query):
            intent_type = IntentType.COMMITMENT
        elif self._TIMELINE_RE.search(query):
            intent_type = IntentType.TIMELINE
        elif self._PLANNING_RE.search(query):
            intent_type = IntentType.PLANNING
        elif self._REFLECTION_RE.search(query):
            intent_type = IntentType.REFLECTION
        elif self._PROJECT_RE.search(query):
            intent_type = IntentType.PROJECT_CENTRIC
        elif self._PERSON_RE.search(query):
            intent_type = IntentType.PERSON_CENTRIC
        else:
            intent_type = IntentType.FACTUAL

        # Extract entities (person names)
        entities = [m.group(1) for m in self._PERSON_RE.finditer(query)]

        # Time filter
        time_m = self._TIME_RE.search(query)
        time_filter = time_m.group(1) if time_m else None

        # Source filter
        source_m = self._SOURCE_RE.search(query)
        source_filter = source_m.group(0).lower() if source_m else None

        # Keywords: non-stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "i", "me", "my",
            "what", "when", "where", "who", "how", "did", "do", "does",
            "about", "with", "for", "from", "in", "on", "at", "to",
        }
        keywords = [
            w.lower()
            for w in re.findall(r"\b\w{3,}\b", query)
            if w.lower() not in stop_words
        ]

        return QueryIntent(
            intent_type=intent_type,
            entities=entities,
            time_filter=time_filter,
            source_filter=source_filter,
            keywords=keywords,
        )
