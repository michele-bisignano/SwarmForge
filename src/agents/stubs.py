from src.agents.base import AbstractAgent
from src.orchestrator.models import Subtask, SubtaskResult, SubtaskStatus


class ArchitectAgent(AbstractAgent):
    """Stub implementation for the primary architectural planning agent."""

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the stub architect agent.

        @param config: Configuration necessary for agent instantiation.
        """
        self._config = config or {}

    async def run(self, subtask: Subtask) -> SubtaskResult:
        """Returns a pre-defined architectural plan.

        @param subtask: The subtask to process.
        @return: A stub result containing a pre-defined architectural plan.
        """
        return SubtaskResult(
            subtask_id=subtask.id,
            agent_id=self.agent_id(),
            status=SubtaskStatus.OK,
            content="STUB ARCHITECTURE: 1. Service Layer 2. Repository Pattern 3. API Endpoints.",
        )

    def agent_id(self) -> str:
        """Returns the stub identifier for the architect.

        @return: Architect_Stub_001
        """
        return "Architect_Stub_001"

    def capabilities(self) -> list[str]:
        """Returns architect capabilities.

        @return: ["architect"]
        """
        return ["architect"]

    def health(self) -> bool:
        """Stub health check.

        @return: True
        """
        return True


class CoderAgent(AbstractAgent):
    """Stub implementation for the code generation agent."""

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the stub coder agent.

        @param config: Configuration necessary for agent instantiation.
        """
        self._config = config or {}

    async def run(self, subtask: Subtask) -> SubtaskResult:
        """Returns pre-generated code examples.

        @param subtask: The subtask to process.
        @return: A stub result containing pre-generated code.
        """
        return SubtaskResult(
            subtask_id=subtask.id,
            agent_id=self.agent_id(),
            status=SubtaskStatus.OK,
            content="STUB CODE: def hello_world():\n    print('Hello from SwarmForge')",
        )

    def agent_id(self) -> str:
        """Returns the stub identifier for the coder.

        @return: Coder_Stub_001
        """
        return "Coder_Stub_001"

    def capabilities(self) -> list[str]:
        """Returns coder capabilities.

        @return: ["coder"]
        """
        return ["coder"]

    def health(self) -> bool:
        """Stub health check.

        @return: True
        """
        return True


class ReviewerAgent(AbstractAgent):
    """Stub implementation for the code review agent."""

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the stub reviewer agent.

        @param config: Configuration necessary for agent instantiation.
        """
        self._config = config or {}

    async def run(self, subtask: Subtask) -> SubtaskResult:
        """Returns a pre-written review summary.

        @param subtask: The subtask to process.
        @return: A stub result containing a review summary.
        """
        return SubtaskResult(
            subtask_id=subtask.id,
            agent_id=self.agent_id(),
            status=SubtaskStatus.OK,
            content="STUB REVIEW: Code follows standards. No security issues found.",
        )

    def agent_id(self) -> str:
        """Returns the stub identifier for the reviewer.

        @return: Reviewer_Stub_001
        """
        return "Reviewer_Stub_001"

    def capabilities(self) -> list[str]:
        """Returns reviewer capabilities.

        @return: ["reviewer"]
        """
        return ["reviewer"]

    def health(self) -> bool:
        """Stub health check.

        @return: True
        """
        return True
