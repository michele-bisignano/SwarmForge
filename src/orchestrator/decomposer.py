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


import uuid


class RuleBasedTaskDecomposer(AbstractTaskDecomposer):
    """Rule-based implementation of task decomposition."""

    async def decompose(self, request: TaskRequest) -> list[Subtask]:
        """Decompose task into a static sequence: Architect -> Coder -> Reviewer.

        @param request: The task request.
        @return: List of exactly three subtasks in fixed order.
        """
        architect_id = str(uuid.uuid4())
        coder_id = str(uuid.uuid4())
        reviewer_id = str(uuid.uuid4())

        return [
            Subtask(
                id=architect_id,
                kind="architect",
                description=request.description,
                dependencies=[],
            ),
            Subtask(
                id=coder_id,
                kind="coder",
                description=request.description,
                dependencies=[architect_id],
            ),
            Subtask(
                id=reviewer_id,
                kind="reviewer",
                description=request.description,
                dependencies=[coder_id],
            ),
        ]
