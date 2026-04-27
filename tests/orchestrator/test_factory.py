"""Tests for SwarmFactory."""

from unittest.mock import MagicMock, patch

import pytest
import yaml

from src.agents.config import AgentConfig
from src.agents.cline_agent import ClineAgent
from src.orchestrator.factory import SwarmFactory
from src.orchestrator.orchestrator import SwarmOrchestrator
from src.orchestrator.registry import AgentRegistry


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_raw_config(
    role: str = "coder",
    model: str = "test-model",
    api_base_url: str = "https://api.example.com",
) -> dict:
    """Return a minimal valid raw YAML dict for an agent."""
    return {
        "role": role,
        "system_prompt": f"You are a {role}.",
        "model": model,
        "api_base_url": api_base_url,
        "api_key_env_var": f"{role.upper()}_API_KEY",
        "extra_params": {"temperature": 0.1},
    }


def _get_agents(orch: SwarmOrchestrator) -> list[ClineAgent]:
    """Extract agents from orchestrator's registry, cast to ClineAgent."""
    return list(orch._registry.all())  # type: ignore[return-value]


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def raw_architect() -> dict:
    """Raw YAML dict for architect role."""
    return _make_raw_config(role="architect")


@pytest.fixture
def raw_coder() -> dict:
    """Raw YAML dict for coder role."""
    return _make_raw_config(role="coder")


@pytest.fixture
def raw_reviewer() -> dict:
    """Raw YAML dict for reviewer role."""
    return _make_raw_config(role="reviewer")


@pytest.fixture
def all_raw(raw_architect: dict, raw_coder: dict, raw_reviewer: dict) -> dict[str, dict]:
    """Map of role name to raw config dict."""
    return {
        "architect": raw_architect,
        "coder": raw_coder,
        "reviewer": raw_reviewer,
    }


@pytest.fixture
def mock_path_is_file():  # type: ignore[misc]
    """Mock Path.is_file always returning True."""
    with patch("pathlib.Path.is_file", return_value=True) as mock:
        yield mock


# ─── create — happy path ─────────────────────────────────────────────────────


def test_should_return_swarm_orchestrator_instance(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Factory.create() must return a SwarmOrchestrator instance."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    assert isinstance(result, SwarmOrchestrator)


def test_should_register_three_agents(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Factory must register exactly three agents (architect, coder, reviewer)."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    agents = result._registry.all()
    assert len(agents) == 3


def test_should_register_agents_in_order_architect_coder_reviewer(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Agents must be registered in architect, coder, reviewer order."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    ids = [a.agent_id() for a in result._registry.all()]
    assert ids == ["cline_architect", "cline_coder", "cline_reviewer"]


def test_should_create_cline_agent_instances(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """All registered agents must be ClineAgent instances."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    for agent in result._registry.all():
        assert isinstance(agent, ClineAgent)


def test_should_set_correct_roles_on_agents(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Each agent must have capabilities matching its role."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    expected = [
        (["architect"], "cline_architect"),
        (["coder"], "cline_coder"),
        (["reviewer"], "cline_reviewer"),
    ]
    for agent, (caps, aid) in zip(result._registry.all(), expected):
        assert agent.capabilities() == caps
        assert agent.agent_id() == aid


# ─── create — env var overrides ──────────────────────────────────────────────


def test_should_override_model_from_env_var(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """ARCHITECT_MODEL env var must override the YAML model field."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", side_effect=lambda k, d=None: {
            "ARCHITECT_MODEL": "custom-arch-model",
        }.get(k, d)):
            result = SwarmFactory.create()

    agents = _get_agents(result)
    assert agents[0].agent_id() == "cline_architect"
    assert agents[0]._config.model == "custom-arch-model"


def test_should_override_api_base_url_from_env_var(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """CODER_API_BASE_URL env var must override the YAML api_base_url field."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", side_effect=lambda k, d=None: {
            "CODER_API_BASE_URL": "https://custom-coder.example.com",
        }.get(k, d)):
            result = SwarmFactory.create()

    agents = _get_agents(result)
    assert agents[1].agent_id() == "cline_coder"
    assert agents[1]._config.api_base_url == "https://custom-coder.example.com"


def test_should_not_override_api_key_env_var_field(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """api_key_env_var from YAML must NOT be overridden by env vars."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    agents = _get_agents(result)
    assert agents[0]._config.api_key_env_var == "ARCHITECT_API_KEY"
    assert agents[1]._config.api_key_env_var == "CODER_API_KEY"
    assert agents[2]._config.api_key_env_var == "REVIEWER_API_KEY"


def test_should_keep_yaml_model_when_env_var_not_set(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """When no env var override is set, the YAML model value must be used."""
    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    agents = _get_agents(result)
    assert agents[0]._config.model == "test-model"
    assert agents[1]._config.model == "test-model"
    assert agents[2]._config.model == "test-model"


def test_should_wire_default_strategies_into_orchestrator(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Orchestrator must be wired with RuleBasedTaskDecomposer,
    CapabilityMatchSelector, AgentRegistry, and SequentialResultAggregator."""
    from src.orchestrator.aggregator import SequentialResultAggregator
    from src.orchestrator.decomposer import RuleBasedTaskDecomposer
    from src.orchestrator.selector import CapabilityMatchSelector

    with patch("yaml.safe_load", side_effect=list(all_raw.values())):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    assert isinstance(result._decomposer, RuleBasedTaskDecomposer)
    assert isinstance(result._registry, AgentRegistry)
    assert isinstance(result._selector, CapabilityMatchSelector)
    assert isinstance(result._aggregator, SequentialResultAggregator)


# ─── create — error paths ────────────────────────────────────────────────────


def test_should_raise_file_not_found_when_config_missing() -> None:
    """Must raise FileNotFoundError when an expected YAML file is absent."""
    with patch("pathlib.Path.is_file", return_value=False):
        with pytest.raises(FileNotFoundError, match="Missing agent config"):
            SwarmFactory.create()


def test_should_raise_yaml_error_when_yaml_is_invalid(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Must propagate yaml.YAMLError when safe_load fails."""
    with patch("yaml.safe_load", side_effect=yaml.YAMLError("bad yaml")):
        with pytest.raises(yaml.YAMLError, match="bad yaml"):
            SwarmFactory.create()


def test_should_raise_validation_error_when_config_invalid(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """Must propagate pydantic.ValidationError when config misses required fields."""
    broken = _make_raw_config(role="coder")
    del broken["model"]  # missing required field

    with patch("yaml.safe_load", return_value=broken):
        with patch("os.getenv", return_value=None):
            from pydantic import ValidationError

            with pytest.raises(ValidationError):
                SwarmFactory.create()


def test_should_pass_extra_params_from_yaml_to_agent_config(
    all_raw: dict, mock_path_is_file: MagicMock,
) -> None:
    """extra_params from YAML must flow through to AgentConfig and ClineAgent."""
    coder = all_raw["coder"].copy()
    coder["extra_params"] = {"temperature": 0.1, "max_tokens": 8192}

    with patch("yaml.safe_load", side_effect=[all_raw["architect"], coder, all_raw["reviewer"]]):
        with patch("os.getenv", return_value=None):
            result = SwarmFactory.create()

    agents = _get_agents(result)
    assert agents[1]._config.extra_params == {"temperature": 0.1, "max_tokens": 8192}


def test_should_accept_custom_configs_dir(
    tmp_path, all_raw: dict,
) -> None:
    """configs_dir parameter must be respected — factory loads from custom path."""
    import yaml as yaml_module

    agents_dir = tmp_path / "my_agents"
    agents_dir.mkdir()
    expected_configs: dict[str, AgentConfig] = {}
    for role, raw in all_raw.items():
        path = agents_dir / f"{role}.yaml"
        path.write_text(yaml_module.dump(raw), encoding="utf-8")
        expected_configs[role] = AgentConfig(**raw)

    result = SwarmFactory.create(configs_dir=str(agents_dir))

    agents = _get_agents(result)
    assert len(agents) == 3
    for agent in agents:
        role = agent._config.role
        assert role in expected_configs
