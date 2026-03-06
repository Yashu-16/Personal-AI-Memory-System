"""Date extractor using dateparser and regex patterns."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.utils.datetime_utils import parse_date


@dataclass
class ExtractedDate:
    date: datetime
    context: str
    is_deadline: bool = False


class DateExtractor:
    """Extract dates and deadlines from text."""

    # Relative date expressions
    _RELATIVE_DATE_RE = re.compile(
        r"\b("
        r"today|tomorrow|yesterday|"
        r"next (?:week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
        r"last (?:week|month|year)|"
        r"in \d+ (?:day|week|month|year)s?|"
        r"\d{1,2}/\d{1,2}/\d{2,4}|"
        r"\d{4}-\d{2}-\d{2}|"
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?"
        r")\b",
        re.IGNORECASE,
    )

    # Deadline signal words
    _DEADLINE_WORDS_RE = re.compile(
        r"\b(?:by|before|deadline|due|no later than)\b", re.IGNORECASE
    )

    def extract(self, text: str) -> list[ExtractedDate]:
        """Extract dates from *text*."""
        results: list[ExtractedDate] = []
        seen: set[str] = set()

        for m in self._RELATIVE_DATE_RE.finditer(text):
            raw = m.group(1)
            if raw.lower() in seen:
                continue
            seen.add(raw.lower())

            parsed = parse_date(raw)
            if parsed is None:
                continue

            # Determine if this is a deadline by looking at the preceding 20 chars
            start = max(0, m.start() - 30)
            context = text[start : m.end() + 30]
            is_deadline = bool(self._DEADLINE_WORDS_RE.search(text[start : m.start()]))

            results.append(
                ExtractedDate(date=parsed, context=context.strip(), is_deadline=is_deadline)
            )

        return results
