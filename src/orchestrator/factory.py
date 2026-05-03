"""SwarmFactory — builds a ready-to-use SwarmOrchestrator from YAML agent configs."""

import logging
import os
from pathlib import Path

import yaml

from src.agents.cline_agent import ClineAgent
from src.agents.config import AgentConfig
from src.orchestrator.aggregator import SequentialResultAggregator
from src.orchestrator.decomposer import RuleBasedTaskDecomposer
from src.orchestrator.orchestrator import SwarmOrchestrator
from src.orchestrator.registry import AgentRegistry
from src.orchestrator.selector import CapabilityMatchSelector

logger = logging.getLogger(__name__)

_DEFAULT_ROLES: tuple[str, ...] = ("architect", "coder", "reviewer")


class SwarmFactory:
    """Builds a fully wired SwarmOrchestrator from YAML agent configuration files."""

    @staticmethod
    def create(configs_dir: str = "configs/agents") -> SwarmOrchestrator:
        """Build SwarmOrchestrator with real ClineAgent instances.

        Loads agent YAML configs from configs_dir, resolves environment variable
        overrides for model and api_base_url, creates ClineAgent instances, and
        wires them into a SwarmOrchestrator with default strategy implementations.

        @param configs_dir: Path to directory containing agent YAML configs
            (architect.yaml, coder.yaml, reviewer.yaml).
        @return: Fully wired SwarmOrchestrator ready for use.
        @raise FileNotFoundError: If any expected agent YAML file is missing.
        @raise yaml.YAMLError: If a YAML file cannot be parsed.
        @raise pydantic.ValidationError: If a YAML config fails AgentConfig validation.
        """
        registry = AgentRegistry()

        for role in _DEFAULT_ROLES:
            config_path = Path(configs_dir) / f"{role}.yaml"
            if not config_path.is_file():
                raise FileNotFoundError(
                    f"Missing agent config for role '{role}': {config_path}"
                )

            with open(config_path, encoding="utf-8") as fh:
                raw: dict = yaml.safe_load(fh)

            agent_config = SwarmFactory._resolve_config(raw, role)
            agent = ClineAgent(agent_config)
            registry.register(agent)
            logger.info("Registered agent: role=%s model=%s", role, agent_config.model)

        return SwarmOrchestrator(
            decomposer=RuleBasedTaskDecomposer(),
            registry=registry,
            selector=CapabilityMatchSelector(),
            aggregator=SequentialResultAggregator(),
        )

    @staticmethod
    def _resolve_config(raw: dict, role: str) -> AgentConfig:
        """Resolve environment variable overrides for model and api_base_url.

        Checks for {ROLE}_MODEL and {ROLE}_API_BASE_URL environment variables.
        If set, they override the corresponding YAML values. The api_key_env_var
        field is left unchanged — it is already defined in the YAML config.

        @param raw: Raw YAML dictionary for a single agent.
        @param role: Agent role string (e.g. "architect").
        @return: Validated AgentConfig with resolved values.
        """
        env_model = os.getenv(f"{role.upper()}_MODEL")
        if env_model:
            raw["model"] = env_model

        env_api_base = os.getenv(f"{role.upper()}_API_BASE_URL")
        if env_api_base:
            raw["api_base_url"] = env_api_base

        return AgentConfig(**raw)