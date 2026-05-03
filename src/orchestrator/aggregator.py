from abc import ABC, abstractmethod
from src.orchestrator.models import SubtaskResult, SwarmResult, SubtaskStatus


class AbstractResultAggregator(ABC):
    """Abstract base class for result aggregation strategies."""

    @abstractmethod
    def aggregate(self, task_id: str, results: list[SubtaskResult]) -> SwarmResult:
        """Aggregate subtask results into a final SwarmResult.

        @param task_id: The ID of the original task.
        @param results: List of subtask results to aggregate.
        @return: A consolidated SwarmResult.
        """
        ...


class SequentialResultAggregator(AbstractResultAggregator):
    """Aggregates results by concatenating OK subtask contents."""

    def aggregate(self, task_id: str, results: list[SubtaskResult]) -> SwarmResult:
        """Concatenate content of all OK subtask results.

        @param task_id: The ID of the original task.
        @param results: List of subtask results to aggregate.
        @return: A SwarmResult with aggregated content.
        """
        ok_contents = [r.content for r in results if r.status == SubtaskStatus.OK]
        final_content = "\n".join(ok_contents)
        return SwarmResult(
            task_id=task_id,
            results=results,
            final_content=final_content
        )
