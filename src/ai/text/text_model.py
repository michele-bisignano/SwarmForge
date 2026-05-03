from abc import abstractmethod
from typing import Any, Iterator

from ..core.ai_model import AbstractAIModel

class AbstractTextModel(AbstractAIModel):
    """Base contract for AI models that generate text or analyze context.
    
    Inherits identity properties and adds text generation capabilities.
    """
    
    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        images: list[Any] | None = None, 
        ai_context: dict[str, Any] | None = None, 
        **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        """Generate text based on a prompt, optionally maintaining context history.
        
        @param prompt: The instruction or query for the model.
        @param images: Optional list of images (str path or PIL.Image) to include in the context.
        @param ai_context: Optional history/state object for conversational multi-turn context.
        @param kwargs: Optional parameters (e.g., image references, temperature).
        @return: A tuple containing the generated text string and the updated context dictionary.
        """
        ...

    @abstractmethod
    def stream_text(
        self,
        prompt: str,
        images: list[Any] | None = None,
        ai_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream text token-by-token instead of waiting for full response.

        @param prompt: The instruction or query for the model.
        @param images: Optional image list for multimodal input.
        @param ai_context: Optional conversational state.
        @return: Iterator yielding text chunks as they arrive.
        """
        ...

    @abstractmethod
    def count_tokens(
        self,
        prompt: str,
        images: list[Any] | None = None,
    ) -> int:
        """Estimate token count for a prompt before sending.

        Used to pre-validate against context window limits.
        @param prompt: The text to measure.
        @param images: Optional images (affect token count).
        @return: Estimated token count as integer.
        """
        ...

    @abstractmethod
    def reset_context(self) -> None:
        """Clear all conversational state and history.

        Must be called between independent sessions to prevent
        context bleed across unrelated tasks.
        """
        ...

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if this model supports token-by-token streaming.

        @return: True if stream_text() is functional, False if stub only.
        """
        ...

    @abstractmethod
    def supports_vision(self) -> bool:
        """Check if this model accepts image inputs.

        @return: True if images parameter in generate_text() is functional.
        """
        ...