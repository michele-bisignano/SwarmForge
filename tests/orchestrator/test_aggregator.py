import pytest
from src.orchestrator.models import SubtaskResult, SwarmResult, SubtaskStatus
from src.orchestrator.aggregator import SequentialResultAggregator


@pytest.fixture
def aggregator() -> SequentialResultAggregator:
    """Fixture for SequentialResultAggregator."""
    return SequentialResultAggregator()


def test_should_aggregate_ok_results_when_multiple_ok_tasks(aggregator: SequentialResultAggregator) -> None:
    task_id = "task1"
    results = [
        SubtaskResult(subtask_id="1", agent_id="a1", status=SubtaskStatus.OK, content="Hello"),
        SubtaskResult(subtask_id="2", agent_id="a2", status=SubtaskStatus.OK, content="World"),
    ]
    swarm_result = aggregator.aggregate(task_id, results)
    assert swarm_result.task_id == task_id
    assert swarm_result.results == results
    assert swarm_result.final_content == "Hello\nWorld"


def test_should_ignore_failed_results_when_mixed_status(aggregator: SequentialResultAggregator) -> None:
    task_id = "task1"
    results = [
        SubtaskResult(subtask_id="1", agent_id="a1", status=SubtaskStatus.OK, content="Hello"),
        SubtaskResult(subtask_id="2", agent_id="a2", status=SubtaskStatus.FAILED, content="Error", error="Fail"),
    ]
    swarm_result = aggregator.aggregate(task_id, results)
    assert swarm_result.final_content == "Hello"


def test_should_return_empty_content_when_no_results(aggregator: SequentialResultAggregator) -> None:
    task_id = "task1"
    swarm_result = aggregator.aggregate(task_id, [])
    assert swarm_result.final_content == ""
    assert swarm_result.results == []
