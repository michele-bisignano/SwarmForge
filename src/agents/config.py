"""AgentConfig — provider-agnostic agent configuration value object."""

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Carries provider-agnostic agent configuration for any AbstractAgent subclass.

    No behavior — pure data. New roles added via YAML config without code changes.
    """

    role: str
    """Role identifier for this agent instance (e.g. "architect", "coder", "reviewer")."""

    system_prompt: str
    """System-level instruction injected as the first message in every API call."""

    model: str
    """Model name string sent in the API request body (e.g. "gemini-2.0-flash"). No default."""

    api_base_url: str
    """Base URL of the OpenAI-compatible endpoint. No trailing slash expected."""

    api_key_env_var: str
    """Name of the environment variable holding the API key (e.g. "GOOGLE_AI_STUDIO_API_KEY")."""

    extra_params: dict = Field(default_factory=dict)
    """Provider-specific params merged into the request body (e.g. temperature, max_tokens)."""