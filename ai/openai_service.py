from openai import AsyncOpenAI

from core.config import settings
from ai.base import AIService


class OpenAIService(AIService):
    """
    OpenAI implementation of :class:`AIService`.

    Uses ``gpt-4o`` by default for both text completions and vision tasks.
    The API key is read from ``settings.openai_api_key`` (``OPENAI_API_KEY`` env var).

    Swap this class out for any other :class:`AIService` implementation
    without changing the router layer.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat(
        self,
        prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """
        Send *prompt* to the OpenAI Chat Completions API and return the response text.

        Args:
            prompt: The user's message.
            model: OpenAI model name (default: ``gpt-4o``).
            temperature: Sampling temperature between 0 and 2.
            **kwargs: Additional parameters forwarded to the API.

        Returns:
            The assistant's reply as a plain string.
        """
        response = await self._client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail.",
        model: str = "gpt-4o",
        **kwargs,
    ) -> str:
        """
        Use the GPT-4o vision model to describe the image at *image_url*.

        Args:
            image_url: A publicly accessible URL of the image.
            prompt: The question/instruction to apply to the image.
            model: OpenAI model (must support vision; default: ``gpt-4o``).
            **kwargs: Additional parameters forwarded to the API.

        Returns:
            A natural-language description or analysis produced by the model.
        """
        response = await self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            **kwargs,
        )
        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Singleton instance – import and use directly, or override in tests
# ---------------------------------------------------------------------------
openai_service = OpenAIService()
