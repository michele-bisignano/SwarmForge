"""Tests for CapabilityMatchSelector."""
import pytest
from unittest.mock import MagicMock
from src.orchestrator.selector import CapabilityMatchSelector
from src.orchestrator.models import Subtask
from src.orchestrator.registry import AgentRegistry
from src.agents.base import AbstractAgent

@pytest.fixture
def selector() -> CapabilityMatchSelector:
    """Return a CapabilityMatchSelector."""
    return CapabilityMatchSelector()

@pytest.fixture
def subtask() -> MagicMock:
    """Return a mock subtask."""
    subtask = MagicMock(spec=Subtask)
    subtask.kind = "coding"
    return subtask

@pytest.fixture
def registry() -> MagicMock:
    """Return a mock registry."""
    return MagicMock(spec=AgentRegistry)

def test_should_return_first_matching_agent(selector: CapabilityMatchSelector, subtask: MagicMock, registry: MagicMock) -> None:
    """Verify first matching agent is returned."""
    agent1 = MagicMock(spec=AbstractAgent)
    agent2 = MagicMock(spec=AbstractAgent)
    
    registry.by_capability.return_value = [agent1, agent2]
    
    selected = selector.select(subtask, registry)
    
    assert selected == agent1
    registry.by_capability.assert_called_once_with("coding")

def test_should_return_none_when_no_matching_agent(selector: CapabilityMatchSelector, subtask: MagicMock, registry: MagicMock) -> None:
    """Verify None is returned when no agent matches."""
    registry.by_capability.return_value = []
    
    selected = selector.select(subtask, registry)
    
    assert selected is None
    registry.by_capability.assert_called_once_with("coding")
