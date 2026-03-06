"""DateTime utility functions."""

from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def parse_date(text: str) -> Optional[datetime]:
    """Parse a natural language date string using dateparser."""
    if not text or not text.strip():
        return None
    try:
        import dateparser  # type: ignore

        result = dateparser.parse(
            text,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "PREFER_DATES_FROM": "future",
                "PREFER_DAY_OF_MONTH": "first",
            },
        )
        return result
    except Exception:
        return None


def format_relative(dt: datetime) -> str:
    """Return a human-friendly relative time string.

    Examples: '2 days ago', 'in 3 hours', 'just now'
    """
    now = now_utc()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    delta = now - dt
    total_seconds = delta.total_seconds()

    if abs(total_seconds) < 60:
        return "just now"

    abs_seconds = abs(total_seconds)
    future = total_seconds < 0

    if abs_seconds < 3600:
        minutes = int(abs_seconds // 60)
        label = f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif abs_seconds < 86400:
        hours = int(abs_seconds // 3600)
        label = f"{hours} hour{'s' if hours != 1 else ''}"
    elif abs_seconds < 86400 * 30:
        days = int(abs_seconds // 86400)
        label = f"{days} day{'s' if days != 1 else ''}"
    elif abs_seconds < 86400 * 365:
        months = int(abs_seconds // (86400 * 30))
        label = f"{months} month{'s' if months != 1 else ''}"
    else:
        years = int(abs_seconds // (86400 * 365))
        label = f"{years} year{'s' if years != 1 else ''}"

    return f"in {label}" if future else f"{label} ago"


def is_overdue(deadline: datetime) -> bool:
    """Return True if *deadline* is in the past."""
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return deadline < now_utc()
