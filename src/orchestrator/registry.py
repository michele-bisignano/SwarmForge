from src.agents.base import AbstractAgent

class AgentRegistry:
    """Manages a collection of registered AbstractAgent instances."""

    def __init__(self) -> None:
        """Initializes an empty registry."""
        self._agents: list[AbstractAgent] = []

    def register(self, agent: AbstractAgent) -> None:
        """Registers an agent instance for use within the swarm.

        @param agent: The agent instance to register.
        """
        self._agents.append(agent)

    def all(self) -> list[AbstractAgent]:
        """Retrieves all currently registered agents.

        @return: A list of registered AbstractAgent instances.
        """
        return list(self._agents)

    def by_capability(self, kind: str) -> list[AbstractAgent]:
        """Retrieves all agents capable of handling a specific subtask kind.

        @param kind: The subtask kind to filter by.
        @return: A list of matching AbstractAgent instances.
        """
        return [agent for agent in self._agents if kind in agent.capabilities()]
