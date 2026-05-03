"""Tests for AgentConfig and ClineAgent."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.agents.config import AgentConfig
from src.agents.cline_agent import ClineAgent
from src.orchestrator.models import Subtask, SubtaskResult, SubtaskStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def config() -> AgentConfig:
    """Return a canonical valid AgentConfig for reuse across tests."""
    return AgentConfig(
        role="coder",
        system_prompt="You are an expert coder.",
        model="test-model",
        api_base_url="https://api.example.com",
        api_key_env_var="TEST_API_KEY",
        extra_params={"temperature": 0.1, "max_tokens": 100},
    )


@pytest.fixture
def subtask() -> Subtask:
    """Return a canonical Subtask for reuse across tests."""
    return Subtask(id="sub-1", kind="coder", description="Write a function.")


# ─── AgentConfig Tests ───────────────────────────────────────────────────────

def test_should_instantiate_with_all_required_fields() -> None:
    config = AgentConfig(
        role="architect",
        system_prompt="You are an architect.",
        model="gpt-4",
        api_base_url="https://api.openai.com",
        api_key_env_var="OPENAI_KEY",
    )
    assert config.role == "architect"
    assert config.model == "gpt-4"


def test_should_default_extra_params_to_empty_dict_when_omitted() -> None:
    config = AgentConfig(
        role="reviewer",
        system_prompt="You are a reviewer.",
        model="test",
        api_base_url="https://api.example.com",
        api_key_env_var="KEY",
    )
    assert config.extra_params == {}


def test_should_accept_arbitrary_keys_in_extra_params() -> None:
    config = AgentConfig(
        role="coder",
        system_prompt="prompt",
        model="test",
        api_base_url="https://api.example.com",
        api_key_env_var="KEY",
        extra_params={"custom_provider_param": "value", "top_k": 50},
    )
    assert config.extra_params["custom_provider_param"] == "value"
    assert config.extra_params["top_k"] == 50


def test_should_accept_any_string_value_for_role() -> None:
    config = AgentConfig(
        role="custom_tester",
        system_prompt="prompt",
        model="test",
        api_base_url="https://api.example.com",
        api_key_env_var="KEY",
    )
    assert config.role == "custom_tester"


# ─── ClineAgent Tests — helper ───────────────────────────────────────────────

def _mock_response(content: str, status_code: int = 200) -> MagicMock:
    """Build a mock httpx.Response with the given content and status."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    mock.text = content
    return mock


def _failed_result(agent_id: str, subtask_id: str, error: str) -> SubtaskResult:
    """Return the expected FAILED SubtaskResult for assertion convenience."""
    return SubtaskResult(
        subtask_id=subtask_id,
        agent_id=agent_id,
        status=SubtaskStatus.FAILED,
        content="",
        error=error,
    )


# ─── ClineAgent — agent_id ───────────────────────────────────────────────────

def test_should_return_cline_role_agent_id(config: AgentConfig) -> None:
    agent = ClineAgent(config)
    assert agent.agent_id() == "cline_coder"


# ─── ClineAgent — capabilities ───────────────────────────────────────────────

def test_should_return_list_containing_config_role(config: AgentConfig) -> None:
    agent = ClineAgent(config)
    assert agent.capabilities() == ["coder"]


# ─── ClineAgent — run (happy path) ───────────────────────────────────────────

@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-api-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_ok_with_content_when_api_call_succeeds(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.return_value = _mock_response("Hello, world!")
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.OK
    assert result.content == "Hello, world!"
    assert result.subtask_id == "sub-1"
    assert result.agent_id == "cline_coder"
    assert result.error is None
    # Verify extra_params were spread into the request body
    call_kwargs = mock_post.call_args.kwargs
    body = call_kwargs.get("json") or call_kwargs.get("content")
    if isinstance(body, bytes):
        body = json.loads(body)
    assert body is not None, "No body found in request"
    assert body["temperature"] == 0.1
    assert body["max_tokens"] == 100


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-api-key")
@patch("httpx.AsyncClient.post")
async def test_should_send_authorization_header_with_api_key(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.return_value = _mock_response("ok")
    agent = ClineAgent(config)

    await agent.run(subtask)

    call_args = mock_post.call_args
    headers = call_args.kwargs.get("headers", {})
    assert headers.get("Authorization") == "Bearer fake-api-key"


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-api-key")
@patch("httpx.AsyncClient.post")
async def test_should_call_correct_url_with_chat_completions_path(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.return_value = _mock_response("ok")
    agent = ClineAgent(config)

    await agent.run(subtask)

    call_args = mock_post.call_args
    url = call_args.kwargs.get("url", call_args.args[0] if call_args.args else "")
    assert url == "https://api.example.com/v1/chat/completions"


# ─── ClineAgent — run (missing API key) ──────────────────────────────────────

@pytest.mark.asyncio
@patch("os.getenv", return_value=None)
async def test_should_return_failed_when_api_key_missing(
    _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert "Missing API key: TEST_API_KEY" in (result.error or "")


# ─── ClineAgent — run (HTTP errors) ──────────────────────────────────────────

@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_http_4xx(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_response = _mock_response("Not found", 404)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=mock_response
    )
    mock_post.return_value = mock_response
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert result.error is not None


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_http_5xx(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_response = _mock_response("Server error", 500)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=mock_response
    )
    mock_post.return_value = mock_response
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert result.error is not None


# ─── ClineAgent — run (network errors) ───────────────────────────────────────

@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_connection_error(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.side_effect = httpx.ConnectError("Connection refused")
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert "Connection failed" in (result.error or "")


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_timeout(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.side_effect = httpx.TimeoutException("Request timed out")
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert "timeout" in (result.error or "").lower()


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_invalid_json_response(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = 200
    mock.json.side_effect = ValueError("Invalid JSON")
    mock.text = "not json"
    mock_post.return_value = mock
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert "Invalid response" in (result.error or "")


@pytest.mark.asyncio
@patch("os.getenv", return_value="fake-key")
@patch("httpx.AsyncClient.post")
async def test_should_return_failed_on_unexpected_exception(
    mock_post: MagicMock, _mock_getenv: MagicMock, config: AgentConfig, subtask: Subtask
) -> None:
    mock_post.side_effect = RuntimeError("Something unexpected")
    agent = ClineAgent(config)

    result = await agent.run(subtask)

    assert result.status == SubtaskStatus.FAILED
    assert result.content == ""
    assert "Something unexpected" in (result.error or "")


# ─── ClineAgent — health ─────────────────────────────────────────────────────

@patch("os.getenv", return_value="fake-key")
def test_should_return_true_when_endpoint_responds(
    _mock_getenv: MagicMock, config: AgentConfig
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    with patch.object(httpx.Client, "get", return_value=mock_response):
        agent = ClineAgent(config)
        assert agent.health() is True


@patch("os.getenv", return_value="fake-key")
def test_should_return_false_when_endpoint_unreachable(
    _mock_getenv: MagicMock, config: AgentConfig
) -> None:
    with patch.object(httpx.Client, "get", side_effect=httpx.ConnectError("refused")):
        agent = ClineAgent(config)
        assert agent.health() is False


@patch("os.getenv", return_value="fake-key")
def test_should_return_false_on_http_error_in_health(
    _mock_getenv: MagicMock, config: AgentConfig
) -> None:
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=mock_response
    )

    with patch.object(httpx.Client, "get", return_value=mock_response):
        agent = ClineAgent(config)
        assert agent.health() is False


@patch("os.getenv", return_value=None)
def test_should_return_false_when_api_key_missing_in_health(
    _mock_getenv: MagicMock, config: AgentConfig
) -> None:
    agent = ClineAgent(config)
    assert agent.health() is False


@patch("os.getenv", return_value="fake-key")
def test_should_catch_all_exceptions_in_health(
    _mock_getenv: MagicMock, config: AgentConfig
) -> None:
    with patch.object(httpx.Client, "get", side_effect=Exception("boom")):
        agent = ClineAgent(config)
        assert agent.health() is False