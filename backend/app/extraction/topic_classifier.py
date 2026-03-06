"""Topic classifier based on keyword matching."""

import re

# Mapping of topic label → representative keywords
_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "work": [
        "meeting", "project", "deadline", "client", "team", "office", "task",
        "budget", "report", "presentation", "sprint", "standup", "jira",
    ],
    "personal": [
        "family", "home", "personal", "hobby", "friend", "birthday", "anniversary",
    ],
    "health": [
        "doctor", "hospital", "medication", "exercise", "gym", "diet", "sleep",
        "appointment", "symptom", "insurance", "therapy", "fitness",
    ],
    "finance": [
        "invoice", "payment", "expense", "salary", "tax", "bank", "budget",
        "invest", "loan", "mortgage", "subscription", "bill",
    ],
    "education": [
        "course", "class", "study", "learn", "exam", "assignment", "university",
        "school", "degree", "certification", "workshop", "tutorial",
    ],
    "relationships": [
        "colleague", "partner", "spouse", "friend", "mentor", "manager", "boss",
        "coworker", "contact", "introduction",
    ],
    "travel": [
        "flight", "hotel", "travel", "trip", "vacation", "conference", "airport",
        "booking", "itinerary", "passport", "visa",
    ],
    "technology": [
        "code", "software", "api", "server", "database", "deploy", "bug", "feature",
        "github", "docker", "cloud", "kubernetes", "python", "javascript",
    ],
}


class TopicClassifier:
    """Classify text into one or more topic labels."""

    def __init__(self) -> None:
        # Pre-compile patterns
        self._patterns: dict[str, re.Pattern] = {
            topic: re.compile(
                r"\b(?:" + "|".join(re.escape(kw) for kw in keywords) + r")\b",
                re.IGNORECASE,
            )
            for topic, keywords in _TOPIC_KEYWORDS.items()
        }

    def classify(self, text: str) -> list[str]:
        """Return a list of topic labels that match *text*."""
        matched: list[str] = []
        for topic, pattern in self._patterns.items():
            if pattern.search(text):
                matched.append(topic)
        return matched if matched else ["general"]
