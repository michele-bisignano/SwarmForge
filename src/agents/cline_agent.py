"""ClineAgent — provider-agnostic agent that calls any OpenAI-compatible chat completions endpoint."""

import logging
import os

import httpx

from src.agents.base import AbstractAgent
from src.agents.config import AgentConfig
from src.orchestrator.models import Subtask, SubtaskResult, SubtaskStatus

logger = logging.getLogger(__name__)


class ClineAgent(AbstractAgent):
    """Implements AbstractAgent by calling an OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the agent with its configuration.

        @param config: AgentConfig instance with role, model, endpoint, and API key metadata.
        """
        self._config = config

    async def run(self, subtask: Subtask) -> SubtaskResult:
        """Execute the subtask by calling the configured OpenAI-compatible endpoint.

        Reads the API key from the environment variable named by config.api_key_env_var.
        If the key is missing, returns SubtaskResult with status FAILED and a descriptive error.
        Sends a POST to {config.api_base_url}/v1/chat/completions with the system prompt
        and subtask description as messages. Spreads config.extra_params into the request body.
        On HTTP success, extracts the first choice's message content as the result.
        On HTTP error or exception, returns FAILED with the exception message.

        @param subtask: The Subtask to execute. Its description field is used as the user message.
        @return: SubtaskResult with status OK and the model's response text, or FAILED with an error.
        """
        api_key: str | None = os.getenv(self._config.api_key_env_var)
        if api_key is None:
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=f"Missing API key: {self._config.api_key_env_var}",
            )

        url: str = f"{self._config.api_base_url}/v1/chat/completions"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self._config.system_prompt},
            {"role": "user", "content": subtask.description},
        ]
        body: dict = {
            "model": self._config.model,
            "messages": messages,
            **self._config.extra_params,
        }

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response: httpx.Response = await client.post(
                    url, headers=headers, json=body
                )
                response.raise_for_status()
                data: dict = response.json()
                content: str = data["choices"][0]["message"]["content"]
                return SubtaskResult(
                    subtask_id=subtask.id,
                    agent_id=self.agent_id(),
                    status=SubtaskStatus.OK,
                    content=content,
                    error=None,
                )
        except httpx.HTTPStatusError as exc:
            logger.warning("HTTP error from %s: %s", url, exc)
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=f"HTTP {exc.response.status_code}: {exc.response.text}",
            )
        except httpx.TimeoutException as exc:
            logger.warning("Request timeout to %s: %s", url, exc)
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=f"Request timeout: {exc}",
            )
        except httpx.ConnectError as exc:
            logger.warning("Connection failed to %s: %s", url, exc)
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=f"Connection failed: {exc}",
            )
        except (ValueError, KeyError) as exc:
            logger.warning("Invalid response from %s: %s", url, exc)
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=f"Invalid response: {exc}",
            )
        except Exception as exc:
            logger.error("Unexpected error calling %s: %s", url, exc)
            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=self.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=str(exc),
            )

    def agent_id(self) -> str:
        """Return a unique, role-scoped identifier for this agent.

        @return: A string of the form "cline_{role}" (e.g. "cline_architect").
        """
        return f"cline_{self._config.role}"

    def capabilities(self) -> list[str]:
        """Return the task types this agent can handle.

        @return: Single-element list containing config.role — the agent claims capability
                 for subtasks whose kind matches its configured role.
        """
        return [self._config.role]

    def health(self) -> bool:
        """Check whether the configured endpoint is reachable.

        Performs a lightweight HEAD or GET request to config.api_base_url.
        Catches ALL exceptions (ConnectionError, TimeoutException, HTTPError, etc.)
        and returns False gracefully. Never propagates exceptions.

        @return: True if the endpoint responds without error; False if unreachable,
                 timed out, or the API key environment variable is not set.
        """
        api_key: str | None = os.getenv(self._config.api_key_env_var)
        if api_key is None:
            return False
        try:
            with httpx.Client() as client:
                response: httpx.Response = client.get(self._config.api_base_url)
                response.raise_for_status()
                return True
        except Exception:
            return False
