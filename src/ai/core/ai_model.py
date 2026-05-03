from abc import ABC, abstractmethod
from asyncio.log import logger
from logging import config
from typing import Any

class AbstractAIModel(ABC):
    """Base contract for AI models.
    
    Provides identity and availability status to the model registry.
    """
    
    @abstractmethod
    def get_provider(self) -> str:
        """Return the AI provider identifier.
        
        @return: String provider name (e.g., 'google', 'replicate').
        """
        ...
        
    @abstractmethod
    def get_api_id(self) -> str:
        """Return the specific model API identifier.
        
        @return: String API ID (e.g., 'gemini-3.1-pro-preview').
        """
        ...
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is ready for execution.
        
        @return: True if configured and available, False otherwise.
        """
        ...
        
    @abstractmethod
    def supports_refining(self) -> bool:
        """Check if the model supports iterative refinement or context history.
        
        @return: True if supported (e.g., Gemini chat), False otherwise (e.g., standard API).
        """
        ...

    @abstractmethod
    def get_context_window(self) -> int:
        """Return max token capacity of this model.
    
        @return: Integer token limit (e.g., 1_000_000 for Gemini 1.5).
        """
        ...

    @abstractmethod
    def get_model_limits(self) -> dict[str, Any]:
        """Return rate and output limits for this model.
    
        @return: Dict with keys: rpm, rpd, max_output_tokens.
        """
        ...
