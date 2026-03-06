"""Text processing utilities."""

import re
from typing import Optional


def clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")
    except Exception:
        # Fallback: simple tag stripping
        return re.sub(r"<[^>]+>", " ", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def detect_language(text: str) -> str:
    """Detect the language of *text*. Returns ISO 639-1 code or 'en'."""
    try:
        from langdetect import detect, LangDetectException  # type: ignore

        return detect(text)
    except Exception:
        return "en"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate *text* to *max_length* characters, appending '…' if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def extract_sentences(text: str) -> list[str]:
    """Split *text* into individual sentences."""
    # Simple sentence splitter using punctuation boundaries
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]
