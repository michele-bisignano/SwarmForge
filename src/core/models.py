from pydantic import BaseModel, Field
from typing import Annotated, Optional

# --- API Models ---
# Defined using Pydantic v2 for FastAPI standards.

class UserIdentity(BaseModel):
    """Represents a simplified user identity context."""
    user_id: str = Field(..., description="Unique identifier of the calling user.")
    role: str = Field(..., description="User role (e.g., admin, basic, guest).")

class AuthToken(BaseModel):
    """Represents an authentication token payload."""
    token: str
    expires_at: float = Field(..., description="Timestamp when the token expires.")

# --- AI Completion Models (OpenAI compatible) ---

class Message(BaseModel):
    """Standard message object for chat/completion endpoints."""
    role: str = Field(..., description="The role of the message (user, system, assistant).")
    content: str = Field(..., description="The message content.")

class CompletionRequest(BaseModel):
    """OpenAI-compatible completion request payload."""
    model: str = Field(..., description="The AI model identifier to use.")
    messages: list[Message] = Field(..., description="List of message history in chat format.")
    stream: bool = Field(False, description="If streaming responses.")
    temperature: float | None = Field(default=0.7, ge=0.0, le=2.0, description="Controls randomness.")

class CompletionResponse(BaseModel):
    """OpenAI-compatible response structure."""
    id: str
    object: str = Field("chat.completion")
    created: int
    model: str
    choices: list[dict[str, str]] = Field(..., description="The model's response options.")
    usage: dict = Field(..., description="Token usage statistics.")

# --- System State Models ---

class AgentConfig(BaseModel):
    """Configuration parameters for an operational agent."""
    endpoint: str = Field(..., description="The primary API endpoint this agent utilizes.")
    max_retries: int = Field(3, description="Maximum number of retries on failure.")

class NodeTelemetry(BaseModel):
    """Telemetry metrics for monitoring agent and node performance."""
    vram_utilization: float = Field(..., ge=0.0, le=1.0, description="VRAM utilization percentage (0.0 to 1.0).")
    cpu_load: float = Field(..., ge=0.0, le=1.0, description="Current CPU load factor.")
    memory_usage_mb: int = Field(..., ge=0, description="Current memory usage in MB.")