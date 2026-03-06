"""Answer generator – produces grounded answers from memories."""

import logging
from typing import Optional

from app.models.memory import Memory

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generate a grounded natural-language answer from retrieved memories."""

    async def generate(
        self,
        query: str,
        memories: list[Memory],
    ) -> tuple[str, float, list[str]]:
        """Return (answer, confidence, suggested_actions).

        Tries LLM first, falls back to template-based generation.
        """
        if not memories:
            return (
                "I don't have any memories related to your query. "
                "Try ingesting some documents first.",
                0.0,
                [],
            )

        # Build context string
        context_lines: list[str] = []
        for i, mem in enumerate(memories[:10], start=1):
            ts = mem.created_at.strftime("%Y-%m-%d") if mem.created_at else "unknown date"
            context_lines.append(f"[{i}] ({ts}) {mem.content[:300]}")
        context = "\n".join(context_lines)

        # Try LLM
        try:
            answer, confidence, actions = await self._llm_generate(query, context, memories)
            return answer, confidence, actions
        except Exception as exc:
            logger.debug("LLM generation failed, using template: %s", exc)
            return self._template_generate(query, memories)

    @staticmethod
    async def _llm_generate(
        query: str,
        context: str,
        memories: list[Memory],
    ) -> tuple[str, float, list[str]]:
        """Generate answer via configured LLM."""
        from app.utils.llm import LLMClient  # noqa: PLC0415

        client = LLMClient()
        system_prompt = (
            "You are a personal memory assistant. Answer the user's question "
            "using ONLY the provided memory context. Be concise and factual. "
            "If the context doesn't contain the answer, say so clearly."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        answer = await client.generate(
            prompt=prompt, system_prompt=system_prompt, max_tokens=512
        )
        confidence = min(0.9, 0.5 + 0.05 * len(memories))

        # Suggest actions based on memory types
        actions: list[str] = []
        mem_types = {m.memory_type.value for m in memories}
        if "commitment" in mem_types:
            actions.append("Review open commitments")
        if "task" in mem_types:
            actions.append("Check pending tasks")

        return answer, confidence, actions

    @staticmethod
    def _template_generate(
        query: str, memories: list[Memory]
    ) -> tuple[str, float, list[str]]:
        """Template-based fallback answer."""
        top = memories[0]
        ts = top.created_at.strftime("%Y-%m-%d") if top.created_at else "recently"
        answer = (
            f"Based on your memories, here is the most relevant information from {ts}:\n\n"
            f"{top.content[:500]}"
        )
        if len(memories) > 1:
            answer += f"\n\n(Found {len(memories)} related memories in total.)"

        confidence = min(0.7, 0.3 + 0.05 * len(memories))
        actions: list[str] = ["Review full memory details"]
        return answer, confidence, actions
