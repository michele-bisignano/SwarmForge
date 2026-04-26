"""Tests for AgentRegistry."""
import pytest
from unittest.mock import MagicMock
from src.orchestrator.registry import AgentRegistry
from src.agents.base import AbstractAgent

@pytest.fixture
def registry() -> AgentRegistry:
    """Return a fresh registry for each test."""
    return AgentRegistry()

@pytest.fixture
def mock_agent() -> MagicMock:
    """Return a mock agent."""
    agent = MagicMock(spec=AbstractAgent)
    return agent

def test_should_register_and_retrieve_all_agents(registry: AgentRegistry, mock_agent: MagicMock) -> None:
    """Verify multiple agents can be registered and retrieved."""
    agent2 = MagicMock(spec=AbstractAgent)
    
    registry.register(mock_agent)
    registry.register(agent2)
    
    all_agents = registry.all()
    assert len(all_agents) == 2
    assert mock_agent in all_agents
    assert agent2 in all_agents

def test_should_filter_by_capability_when_matching(registry: AgentRegistry) -> None:
    """Verify filtering by capability works."""
    agent1 = MagicMock(spec=AbstractAgent)
    agent1.capabilities.return_value = ["coding", "review"]
    
    agent2 = MagicMock(spec=AbstractAgent)
    agent2.capabilities.return_value = ["coding"]
    
    agent3 = MagicMock(spec=AbstractAgent)
    agent3.capabilities.return_value = ["review"]
    
    registry.register(agent1)
    registry.register(agent2)
    registry.register(agent3)
    
    coding_agents = registry.by_capability("coding")
    assert len(coding_agents) == 2
    assert agent1 in coding_agents
    assert agent2 in coding_agents
    assert agent3 not in coding_agents

def test_should_return_empty_list_when_no_match(registry: AgentRegistry) -> None:
    """Verify empty list is returned when no agent matches capability."""
    agent = MagicMock(spec=AbstractAgent)
    agent.capabilities.return_value = ["coding"]
    registry.register(agent)
    
    assert registry.by_capability("review") == []
