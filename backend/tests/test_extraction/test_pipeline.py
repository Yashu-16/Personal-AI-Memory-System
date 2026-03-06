"""Tests for the extraction pipeline."""

import pytest

from app.extraction.commitment_detector import CommitmentDetector
from app.extraction.salience_scorer import SalienceScorer
from app.extraction.task_extractor import TaskExtractor
from app.extraction.topic_classifier import TopicClassifier


def test_extract_commitment_from_text():
    detector = CommitmentDetector()
    text = "I will send the report to John by Friday."
    commitments = detector.detect(text)
    assert len(commitments) >= 1
    assert "send" in commitments[0].action.lower() or "report" in commitments[0].action.lower()


def test_extract_task_from_text():
    extractor = TaskExtractor()
    text = "TODO: Review the pull request before end of day."
    tasks = extractor.extract(text)
    assert len(tasks) >= 1
    assert "Review" in tasks[0].title or "review" in tasks[0].title.lower()


def test_topic_classification():
    classifier = TopicClassifier()

    work_text = "We had a standup meeting and discussed the sprint deadline."
    topics = classifier.classify(work_text)
    assert "work" in topics

    health_text = "My doctor appointment is scheduled for next Monday."
    topics = classifier.classify(health_text)
    assert "health" in topics


def test_salience_scoring():
    scorer = SalienceScorer()

    # High salience: has commitment, named person, urgency
    score_high = scorer.score(
        memory_content="URGENT: I will send the contract to Alice Smith by tomorrow.",
        entities=[object()],  # 1 entity
        commitment_count=1,
        task_count=0,
        dates=[],
    )
    # Low salience: no entities, no commitments
    score_low = scorer.score(
        memory_content="Hello world.",
        entities=[],
        commitment_count=0,
        task_count=0,
        dates=[],
    )
    assert score_high > score_low
    assert 0.0 <= score_high <= 1.0
    assert 0.0 <= score_low <= 1.0
