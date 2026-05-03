import abc
from src.agents.base import AbstractAgent
from src.orchestrator.models import Subtask
from src.orchestrator.registry import AgentRegistry

class AbstractAgentSelector(abc.ABC):
    """Defines the strategy for selecting an agent for a given subtask."""

    @abc.abstractmethod
    def select(self, subtask: Subtask, registry: AgentRegistry) -> AbstractAgent | None:
        """Selects an appropriate agent from the registry for the given subtask.

        @param subtask: The subtask requiring execution.
        @param registry: The registry of available agents.
        @return: The selected AbstractAgent, or None if no match is found.
        """
        ...

class CapabilityMatchSelector(AbstractAgentSelector):
    """Selects the first agent that declares support for the subtask's capability."""

    def select(self, subtask: Subtask, registry: AgentRegistry) -> AbstractAgent | None:
        """Selects the first agent that declares support for the subtask's capability.

        @param subtask: The subtask requiring execution.
        @param registry: The registry of available agents.
        @return: The selected AbstractAgent, or None if no match is found.
        """
        eligible = registry.by_capability(subtask.kind)
        return eligible[0] if eligible else None
