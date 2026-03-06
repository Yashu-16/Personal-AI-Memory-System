"""Named entity extractor using regex patterns."""

import re
from dataclasses import dataclass
from enum import Enum


class EntityTypeHint(str, Enum):
    person = "person"
    organization = "organization"
    place = "place"
    topic = "topic"


@dataclass
class ExtractedEntity:
    name: str
    entity_type: EntityTypeHint
    canonical_name: str


class EntityExtractor:
    """Extract entities from text using curated regex patterns."""

    # Email address → treat display name or local part as a person
    _EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.\w{2,}", re.IGNORECASE)

    # @mention
    _MENTION_RE = re.compile(r"@([A-Za-z][\w.-]{1,50})")

    # Capitalised word sequences (likely proper nouns / names)
    _PROPER_NOUN_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b")

    # Organisation suffixes
    _ORG_SUFFIX_RE = re.compile(
        r"\b([A-Z][A-Za-z &-]{1,60}(?:Inc|LLC|Corp|Ltd|GmbH|Co|Company|Group|Agency|Institute|University|School)\.?)\b"
    )

    # Place heuristics (City, Country)
    _PLACE_RE = re.compile(r"\bin ([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b")

    def extract(self, text: str) -> list[ExtractedEntity]:
        """Return a deduplicated list of extracted entities."""
        entities: dict[str, ExtractedEntity] = {}

        # Emails → person
        for m in self._EMAIL_RE.finditer(text):
            name = m.group()
            canonical = name.lower()
            entities[canonical] = ExtractedEntity(
                name=name, entity_type=EntityTypeHint.person, canonical_name=canonical
            )

        # @mentions → person
        for m in self._MENTION_RE.finditer(text):
            name = m.group(1)
            canonical = name.lower()
            entities[canonical] = ExtractedEntity(
                name=name, entity_type=EntityTypeHint.person, canonical_name=canonical
            )

        # Organisations
        for m in self._ORG_SUFFIX_RE.finditer(text):
            name = m.group(1).strip()
            canonical = name.lower()
            entities[canonical] = ExtractedEntity(
                name=name, entity_type=EntityTypeHint.organization, canonical_name=canonical
            )

        # Places
        for m in self._PLACE_RE.finditer(text):
            name = m.group(1)
            canonical = name.lower()
            if canonical not in entities:
                entities[canonical] = ExtractedEntity(
                    name=name, entity_type=EntityTypeHint.place, canonical_name=canonical
                )

        # Capitalised proper nouns (persons, fallback)
        for m in self._PROPER_NOUN_RE.finditer(text):
            name = m.group(1)
            canonical = name.lower()
            if canonical not in entities:
                entities[canonical] = ExtractedEntity(
                    name=name, entity_type=EntityTypeHint.person, canonical_name=canonical
                )

        return list(entities.values())
