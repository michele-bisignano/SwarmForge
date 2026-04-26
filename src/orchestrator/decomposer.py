from abc import ABC, abstractmethod
from src.orchestrator.models import TaskRequest, Subtask


class AbstractTaskDecomposer(ABC):
    """Contract for decomposing a task into subtasks."""

    @abstractmethod
    async def decompose(self, request: TaskRequest) -> list[Subtask]:
        """Decompose a task into ordered subtasks.

        @param request: The task request to decompose.
        @return: A list of subtasks.
        """
        ...


class RuleBasedTaskDecomposer(AbstractTaskDecomposer):
    """Rule-based implementation of task decomposition."""

    async def decompose(self, request: TaskRequest) -> list[Subtask]:
        """Decompose task based on keywords in description.

        @param request: The task request.
        @return: List of subtasks.
        """
        parts = [p.strip() for p in request.description.split(". ") if p.strip()]
        subtasks = []
        for i, part in enumerate(parts):
            kind = self._determine_kind(part)
            dependencies = [f"subtask-{i-1}"] if i > 0 else []
            subtasks.append(
                Subtask(
                    id=f"subtask-{i}",
                    kind=kind,
                    description=part,
                    dependencies=dependencies,
                )
            )
        return subtasks

    def _determine_kind(self, description: str) -> str:
        """Determine subtask kind based on keywords.

        @param description: Subtask description.
        @return: Kind identifier.
        """
        desc = description.lower()
        if any(k in desc for k in ["code", "implement", "write"]):
            return "coder"
        if any(k in desc for k in ["architect", "design", "plan"]):
            return "architect"
        if any(k in desc for k in ["review", "check", "validate"]):
            return "reviewer"
        return "coder"
