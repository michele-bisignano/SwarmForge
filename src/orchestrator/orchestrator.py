import logging
import uuid
from typing import TYPE_CHECKING

from src.orchestrator.models import (
    Subtask,
    SubtaskResult,
    SubtaskStatus,
    SwarmResult,
    TaskRequest,
)

if TYPE_CHECKING:
    from src.orchestrator.agents.base import AbstractAgent
    from src.orchestrator.aggregator import AbstractResultAggregator
    from src.orchestrator.decomposer import AbstractTaskDecomposer
    from src.orchestrator.registry import AgentRegistry
    from src.orchestrator.selector import AbstractAgentSelector

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    """Thin coordinator for the swarm workflow: decompose, route, execute, aggregate.

    This class owns the workflow loop only. All decision logic — task
    decomposition, agent selection, result aggregation — is delegated to
    injected strategies, keeping the class under the ~150-line SRP threshold.
    """

    def __init__(
        self,
        decomposer: "AbstractTaskDecomposer",
        registry: "AgentRegistry",
        selector: "AbstractAgentSelector",
        aggregator: "AbstractResultAggregator",
    ) -> None:
        """Initialize the orchestrator with all collaborator dependencies.

        @param decomposer: Splits a task description into ordered subtasks.
        @param registry: Live pool of registered agents available for execution.
        @param selector: Chooses the best agent for a given subtask from the registry.
        @param aggregator: Combines all subtask results into a final SwarmResult.
        """
        self._decomposer = decomposer
        self._registry = registry
        self._selector = selector
        self._aggregator = aggregator

    async def run(self, task_description: str) -> "SwarmResult":
        """Execute the full swarm workflow for a single task.

        Decompose the description into subtasks, route each to a matching
        agent via the selector, execute sequentially, then aggregate all
        results into a single SwarmResult.

        @param task_description: Natural-language description of the task to execute.
        @return: A SwarmResult containing the final aggregated content and per-subtask trace.
        @raise RuntimeError: If no subtasks are produced during decomposition.
        @raise ValueError: If no matching agent can be selected for a subtask.
        """
        task_id = str(uuid.uuid4())
        logger.info("Swarm workflow started: task_id=%s", task_id)

        request: "TaskRequest" = TaskRequest(description=task_description)
        subtasks = await self._decomposer.decompose(request)
        if not subtasks:
            logger.warning("Decomposition produced zero subtasks: task_id=%s", task_id)
            raise RuntimeError(f"No subtasks produced for task: {task_id}")

        logger.info("Decomposed into %d subtasks: task_id=%s", len(subtasks), task_id)

        results: list["SubtaskResult"] = []
        for subtask in subtasks:
            result = await self._execute_subtask(subtask)
            results.append(result)

        return self._aggregator.aggregate(task_id, results)

    async def _execute_subtask(self, subtask: "Subtask") -> "SubtaskResult":
        """Execute one subtask: select agent, run, handle errors.

        @param subtask: The subtask to execute.
        @return: SubtaskResult with status OK or FAILED.
        """
        agent: "AbstractAgent" = self._selector.select(subtask, self._registry)
        if agent is None:
            logger.error("No agent available for subtask: subtask_id=%s", subtask.id)
            raise ValueError(f"No matching agent for subtask: {subtask.id}")

        try:
            return await agent.run(subtask)
        except Exception as exc:
            logger.error(
                "Agent execution failed: subtask_id=%s agent=%s error=%s",
                subtask.id,
                agent.agent_id(),
                exc,
            )

            return SubtaskResult(
                subtask_id=subtask.id,
                agent_id=agent.agent_id(),
                status=SubtaskStatus.FAILED,
                content="",
                error=str(exc),
            )
