"""Task extractor using keyword patterns."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.task import TaskPriority
from app.utils.datetime_utils import parse_date


@dataclass
class ExtractedTask:
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    deadline: Optional[datetime] = None


class TaskExtractor:
    """Extract tasks from text using regex heuristics."""

    # Task markers
    _TASK_MARKERS = re.compile(
        r"(?:"
        r"TODO:\s*|"
        r"\[ \]\s*|"
        r"Action item:\s*|"
        r"Action:\s*|"
        r"Need to\s+|"
        r"Must\s+|"
        r"Should\s+|"
        r"Remember to\s+"
        r")(.{5,200}?)(?:[.!?\n]|$)",
        re.IGNORECASE,
    )

    # Urgency keywords → TaskPriority mapping
    _URGENCY_PATTERNS: list[tuple[re.Pattern, TaskPriority]] = [
        (re.compile(r"\b(?:asap|urgent|immediately|critical|blocker)\b", re.IGNORECASE), TaskPriority.urgent),
        (re.compile(r"\b(?:high priority|important|soon)\b", re.IGNORECASE), TaskPriority.high),
        (re.compile(r"\b(?:low priority|whenever|eventually|nice to have)\b", re.IGNORECASE), TaskPriority.low),
    ]

    _DEADLINE_RE = re.compile(
        r"\b(?:by|before|due|deadline)\s+(.{3,60}?)(?:[,;.!?\n]|$)", re.IGNORECASE
    )

    def extract(self, text: str) -> list[ExtractedTask]:
        """Return extracted tasks from *text*."""
        results: list[ExtractedTask] = []

        for m in self._TASK_MARKERS.finditer(text):
            raw_title = m.group(1).strip()
            if len(raw_title) < 5:
                continue

            # Determine priority
            priority = TaskPriority.medium
            for pattern, prio in self._URGENCY_PATTERNS:
                if pattern.search(raw_title):
                    priority = prio
                    break

            # Deadline
            deadline: Optional[datetime] = None
            dl_m = self._DEADLINE_RE.search(raw_title)
            if dl_m:
                deadline = parse_date(dl_m.group(1))
                # Remove deadline fragment from title
                raw_title = raw_title[: dl_m.start()].strip()

            results.append(
                ExtractedTask(
                    title=raw_title,
                    priority=priority,
                    deadline=deadline,
                )
            )

        return results
