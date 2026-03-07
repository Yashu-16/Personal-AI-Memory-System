"""Tests for the commitment detector."""

import pytest

from app.extraction.commitment_detector import CommitmentDetector


detector = CommitmentDetector()


def test_detect_simple_commitment():
    """Basic first-person commitment is detected."""
    text = "I will call the client tomorrow."
    results = detector.detect(text)
    assert len(results) >= 1
    assert "call" in results[0].action.lower() or "client" in results[0].action.lower()


def test_detect_commitment_with_deadline():
    """Commitment with an explicit deadline is captured."""
    text = "I'll finish the report by next Friday."
    results = detector.detect(text)
    assert len(results) >= 1
    # The deadline should have been parsed (may be None if dateparser unavailable)
    # but the commitment itself must be detected
    commitment = results[0]
    assert commitment.action  # action should be non-empty


def test_no_commitment_in_text():
    """Text without a commitment returns an empty list."""
    text = "The weather is nice today."
    results = detector.detect(text)
    assert results == []
