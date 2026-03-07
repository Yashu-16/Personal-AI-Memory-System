"""Pattern analyzer – find recurring topics and behaviors in memories."""

from collections import Counter
from dataclasses import dataclass

from app.models.memory import Memory


@dataclass
class Pattern:
    label: str
    frequency: int
    example_memory_ids: list


class PatternAnalyzer:
    """Identify patterns in a user's memories."""

    def analyze(self, memories: list[Memory]) -> list[Pattern]:
        """Return patterns found in *memories*."""
        if not memories:
            return []

        # Count source types
        source_counter: Counter = Counter(m.source_type for m in memories if m.source_type)
        # Count memory types
        type_counter: Counter = Counter(m.memory_type.value for m in memories)

        patterns: list[Pattern] = []

        for source, count in source_counter.most_common(5):
            if count >= 3:
                examples = [
                    str(m.id) for m in memories if m.source_type == source
                ][:3]
                patterns.append(
                    Pattern(
                        label=f"Frequent source: {source}",
                        frequency=count,
                        example_memory_ids=examples,
                    )
                )

        for mtype, count in type_counter.most_common(5):
            if count >= 5:
                examples = [
                    str(m.id) for m in memories if m.memory_type.value == mtype
                ][:3]
                patterns.append(
                    Pattern(
                        label=f"High volume {mtype} memories",
                        frequency=count,
                        example_memory_ids=examples,
                    )
                )

        # Unresolved commitments pattern
        unresolved = [
            m for m in memories if m.memory_type.value == "commitment"
        ]
        if len(unresolved) >= 3:
            patterns.append(
                Pattern(
                    label="Multiple open commitments",
                    frequency=len(unresolved),
                    example_memory_ids=[str(m.id) for m in unresolved[:3]],
                )
            )

        return patterns
