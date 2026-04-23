from abc import ABC, abstractmethod


class AbstractAgent(ABC):
    """Abstract base class for all agents in the SwarmForge ecosystem."""

    @abstractmethod
    def execute(self, task: str) -> str:
        """Execute the given task and return the result.

        @param task: Description of the task to perform.
        @return: Result of the task execution.
        """
        ...

    @abstractmethod
    def validate_output(self, output: str) -> bool:
        """Validate the output produced by the agent.

        @param output: The output string to validate.
        @return: True if the output is valid, False otherwise.
        """
        ...
