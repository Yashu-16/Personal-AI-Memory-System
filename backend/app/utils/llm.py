"""LLM client with OpenAI / Anthropic fallbacks."""

import logging
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Generate text using configured LLM provider."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
    ) -> str:
        """Return a generated response string."""
        if settings.OPENAI_API_KEY:
            return await self._openai_generate(prompt, system_prompt, max_tokens)
        if settings.ANTHROPIC_API_KEY:
            return await self._anthropic_generate(prompt, system_prompt, max_tokens)
        return self._template_response(prompt)

    @staticmethod
    async def _openai_generate(
        prompt: str, system_prompt: Optional[str], max_tokens: int
    ) -> str:
        from openai import AsyncOpenAI  # type: ignore

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    @staticmethod
    async def _anthropic_generate(
        prompt: str, system_prompt: Optional[str], max_tokens: int
    ) -> str:
        from anthropic import AsyncAnthropic  # type: ignore

        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        kwargs: dict = {
            "model": "claude-haiku-20240307",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""

    @staticmethod
    def _template_response(prompt: str) -> str:
        """Minimal fallback when no LLM is configured."""
        logger.debug("No LLM configured; returning template response.")
        return (
            "I found relevant information in your memories, but no AI provider "
            "is configured to generate a summary. "
            "Please review the supporting memories directly."
        )
