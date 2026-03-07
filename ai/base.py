from abc import ABC, abstractmethod


class AIService(ABC):
    """
    Abstract base class for AI service providers.

    Implement this interface to swap between AI backends (e.g. OpenAI, Anthropic,
    local LLMs) without changing the calling code. Register your implementation
    via dependency injection or a simple factory.

    Example usage::

        class MyAI(AIService):
            async def chat(self, prompt: str, **kwargs) -> str:
                ...

            async def analyze_image(self, image_url: str, **kwargs) -> str:
                ...
    """

    @abstractmethod
    async def chat(self, prompt: str, **kwargs) -> str:
        """
        Send a text prompt and return the model's response.

        Args:
            prompt: The user's input message.
            **kwargs: Optional provider-specific parameters (e.g. model, temperature).

        Returns:
            The generated text response.
        """

    @abstractmethod
    async def analyze_image(self, image_url: str, **kwargs) -> str:
        """
        Describe or analyse an image located at *image_url*.

        Args:
            image_url: Publicly accessible URL of the image to analyse.
            **kwargs: Optional provider-specific parameters.

        Returns:
            A natural-language description or analysis of the image.
        """
