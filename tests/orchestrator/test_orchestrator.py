"""Tests for SwarmOrchestrator — all cases from contract §Test Coverage."""

import logging

import pytest

from unittest.mock import AsyncMock, MagicMock

from src.orchestrator.orchestrator import SwarmOrchestrator
from src.orchestrator.models import (
    Subtask,
    SubtaskResult,
    SubtaskStatus,
    SwarmResult,
    TaskRequest,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def make_subtask(sid: str, desc: str = "task") -> Subtask:
    """Canonical valid Subtask for reuse across tests."""
    return Subtask(id=sid, description=desc)


def make_result(
    sid: str = "s1",
    aid: str = "a1",
    status: SubtaskStatus = SubtaskStatus.OK,
) -> SubtaskResult:
    """Canonical valid SubtaskResult for reuse across tests."""
    return SubtaskResult(subtask_id=sid, agent_id=aid, status=status, content="ok")


def make_agent(
    aid: str = "a1",
    result: SubtaskResult | None = None,
) -> MagicMock:
    """Mock AbstractAgent with configurable run result."""
    agent = MagicMock()
    agent.agent_id.return_value = aid
    agent.run = AsyncMock(return_value=result or make_result())
    return agent


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def decomposer() -> AsyncMock:
    """Async mock for AbstractTaskDecomposer."""
    mock = AsyncMock()
    mock.decompose.return_value = []
    return mock


@pytest.fixture
def registry() -> MagicMock:
    """Mock for AgentRegistry."""
    return MagicMock()


@pytest.fixture
def selector() -> MagicMock:
    """Mock for AbstractAgentSelector."""
    mock = MagicMock()
    mock.select.return_value = None
    return mock


@pytest.fixture
def aggregator() -> MagicMock:
    """Mock for AbstractResultAggregator."""
    mock = MagicMock()
    mock.aggregate.return_value = SwarmResult(
        task_id="", final_content="", subtask_results=[],
    )
    return mock


@pytest.fixture
def orch(
    decomposer: AsyncMock,
    registry: MagicMock,
    selector: MagicMock,
    aggregator: MagicMock,
) -> SwarmOrchestrator:
    """Real orchestrator with all collaborators mocked."""
    return SwarmOrchestrator(decomposer, registry, selector, aggregator)


# ─── __init__ ────────────────────────────────────────────────────────────────


class TestInit:
    """All four collaborators required. None instantiated internally."""

    def test_should_set_attributes_when_all_provided(
        self,
        decomposer: AsyncMock,
        registry: MagicMock,
        selector: MagicMock,
        aggregator: MagicMock,
    ) -> None:
        o = SwarmOrchestrator(decomposer, registry, selector, aggregator)
        assert o._decomposer is decomposer
        assert o._registry is registry
        assert o._selector is selector
        assert o._aggregator is aggregator

    def test_should_raise_typeerror_when_decomposer_missing(
        self,
        registry: MagicMock,
        selector: MagicMock,
        aggregator: MagicMock,
    ) -> None:
        with pytest.raises(TypeError):
            SwarmOrchestrator(  # type: ignore[call-arg]
                registry=registry, selector=selector, aggregator=aggregator,
            )

    def test_should_raise_typeerror_when_registry_missing(
        self, decomposer: AsyncMock, selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        with pytest.raises(TypeError):
            SwarmOrchestrator(  # type: ignore[call-arg]
                decomposer=decomposer, selector=selector, aggregator=aggregator,
            )

    def test_should_raise_typeerror_when_selector_missing(
        self, decomposer: AsyncMock, registry: MagicMock, aggregator: MagicMock,
    ) -> None:
        with pytest.raises(TypeError):
            SwarmOrchestrator(  # type: ignore[call-arg]
                decomposer=decomposer, registry=registry, aggregator=aggregator,
            )

    def test_should_raise_typeerror_when_aggregator_missing(
        self, decomposer: AsyncMock, registry: MagicMock, selector: MagicMock,
    ) -> None:
        with pytest.raises(TypeError):
            SwarmOrchestrator(  # type: ignore[call-arg]
                decomposer=decomposer, registry=registry, selector=selector,
            )


# ─── run — happy path ───────────────────────────────────────────────────────


class TestRunHappyPath:

    @pytest.mark.asyncio
    async def test_should_return_aggregator_result_when_single_subtask_ok(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        subtask = make_subtask("sub-1")
        decomposer.decompose.return_value = [subtask]
        agent = make_agent(result=make_result("sub-1"))
        selector.select.return_value = agent
        final = SwarmResult(task_id="t1", final_content="done", subtask_results=[])
        aggregator.aggregate.return_value = final

        result = await orch.run("build feature")

        assert result is final
        decomposer.decompose.assert_awaited_once()
        args, _ = decomposer.decompose.call_args
        assert isinstance(args[0], TaskRequest)
        assert args[0].description == "build feature"
        aggregator.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_execute_all_three_subtasks_in_order(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        subs = [make_subtask(f"sub-{i}") for i in (1, 2, 3)]
        decomposer.decompose.return_value = subs
        results = [make_result(f"sub-{i}") for i in (1, 2, 3)]
        selector.select.side_effect = [make_agent(result=r) for r in results]
        aggregator.aggregate.return_value = SwarmResult(
            task_id="t1", final_content="all done", subtask_results=results,
        )

        result = await orch.run("big task")

        assert result.final_content == "all done"
        assert aggregator.aggregate.call_count == 1
        _, (task_id, passed) = aggregator.aggregate.call_args
        assert len(passed) == 3
        assert [r.subtask_id for r in passed] == ["sub-1", "sub-2", "sub-3"]

    @pytest.mark.asyncio
    async def test_should_route_mixed_kind_subtasks_to_different_agents(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        subs = [
            make_subtask("arch-1", "design"),
            make_subtask("code-1", "implement"),
            make_subtask("rev-1", "review"),
        ]
        decomposer.decompose.return_value = subs
        agents = [
            make_agent("arch", make_result("arch-1")),
            make_agent("code", make_result("code-1")),
            make_agent("rev", make_result("rev-1")),
        ]
        selector.select.side_effect = agents
        aggregator.aggregate.return_value = SwarmResult(
            task_id="t-mix", final_content="ok", subtask_results=[],
        )

        await orch.run("full pipeline")

        assert selector.select.call_count == 3
        calls = selector.select.call_args_list
        assert calls[0].args[0].id == "arch-1"
        assert calls[1].args[0].id == "code-1"
        assert calls[2].args[0].id == "rev-1"


# ─── run — boundary / error paths ──────────────────────────────────────────


class TestRunBoundaryErrorPaths:

    @pytest.mark.asyncio
    async def test_should_forward_empty_description_to_decomposer(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        decomposer.decompose.return_value = [make_subtask("sub-1")]
        selector.select.return_value = make_agent()
        await orch.run("")
        _, (req,) = decomposer.decompose.await_args
        assert isinstance(req, TaskRequest)
        assert req.description == ""

    @pytest.mark.asyncio
    async def test_should_raise_runtimeerror_when_empty_subtasks(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        decomposer.decompose.return_value = []
        caplog.set_level(logging.WARNING)
        with pytest.raises(RuntimeError, match="No subtasks"):
            await orch.run("empty")
        assert any("zero subtasks" in m.lower() for m in caplog.messages)

    @pytest.mark.asyncio
    async def test_should_raise_valueerror_when_selector_returns_none(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, caplog: pytest.LogCaptureFixture,
    ) -> None:
        decomposer.decompose.return_value = [make_subtask("sub-1")]
        selector.select.return_value = None
        caplog.set_level(logging.ERROR)
        with pytest.raises(ValueError, match="No matching agent"):
            await orch.run("no match")
        assert any("no agent" in m.lower() for m in caplog.messages)

    @pytest.mark.asyncio
    async def test_should_continue_when_agent_fails(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        subs = [make_subtask("s1"), make_subtask("s2")]
        decomposer.decompose.return_value = subs
        agent_ok = make_agent("ok", make_result("s1", "ok"))
        agent_fail = make_agent("fail")
        agent_fail.run = AsyncMock(side_effect=RuntimeError("boom"))
        selector.select.side_effect = [agent_ok, agent_fail]
        aggregator.aggregate.return_value = SwarmResult(
            task_id="t1", final_content="partial", subtask_results=[],
        )
        caplog.set_level(logging.ERROR)

        result = await orch.run("partial fail")

        assert result is not None
        _, (_, passed) = aggregator.aggregate.call_args
        assert len(passed) == 2
        failed = [r for r in passed if r.status == SubtaskStatus.FAILED]
        assert len(failed) == 1
        assert failed[0].error == "boom"
        assert any("execution failed" in m.lower() for m in caplog.messages)

    @pytest.mark.asyncio
    async def test_should_call_aggregator_when_all_agents_fail(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        subs = [make_subtask(f"s{i}") for i in (1, 2, 3)]
        decomposer.decompose.return_value = subs
        agents = []
        for i in (1, 2, 3):
            ag = make_agent(f"a{i}")
            ag.run = AsyncMock(side_effect=RuntimeError("fail"))
            agents.append(ag)
        selector.select.side_effect = agents
        aggregator.aggregate.return_value = SwarmResult(
            task_id="t1", final_content="all fail", subtask_results=[],
        )

        result = await orch.run("total failure")

        assert result is not None
        _, (_, passed) = aggregator.aggregate.call_args
        assert all(r.status == SubtaskStatus.FAILED for r in passed)

    @pytest.mark.asyncio
    async def test_should_propagate_decomposer_exception(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
    ) -> None:
        decomposer.decompose.side_effect = ValueError("decompose bad")
        with pytest.raises(ValueError, match="decompose bad"):
            await orch.run("boom")

    @pytest.mark.asyncio
    async def test_should_propagate_aggregator_exception(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        decomposer.decompose.return_value = [make_subtask("s1")]
        selector.select.return_value = make_agent()
        aggregator.aggregate.side_effect = RuntimeError("agg broke")
        with pytest.raises(RuntimeError, match="agg broke"):
            await orch.run("agg fails")


# ─── run — invariants ──────────────────────────────────────────────────────


class TestRunInvariants:

    @pytest.mark.asyncio
    async def test_should_produce_different_task_ids_on_consecutive_calls(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        selector.select.return_value = make_agent()
        decomposer.decompose.return_value = [make_subtask("s1")]
        captured_ids: list[str] = []

        async def capture(task_id: str, results: list) -> SwarmResult:
            captured_ids.append(task_id)
            return SwarmResult(task_id=task_id, final_content="", subtask_results=[])

        aggregator.aggregate.side_effect = capture

        await orch.run("first")
        await orch.run("second")

        assert len(captured_ids) == 2
        assert captured_ids[0] != captured_ids[1]

    @pytest.mark.asyncio
    async def test_should_preserve_execution_order(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
    ) -> None:
        order_ids = ["C", "A", "B"]
        subs = [make_subtask(sid) for sid in order_ids]
        decomposer.decompose.return_value = subs
        executed: list[str] = []

        def track_select(*args) -> MagicMock:
            executed.append(args[0].id)
            return make_agent(result=make_result(args[0].id))

        selector.select.side_effect = track_select
        aggregator.aggregate.return_value = SwarmResult(
            task_id="t1", final_content="ok", subtask_results=[],
        )

        await orch.run("order test")

        assert executed == order_ids

    @pytest.mark.asyncio
    async def test_should_pass_same_task_id_to_aggregator_as_logged(
        self, orch: SwarmOrchestrator, decomposer: AsyncMock,
        selector: MagicMock, aggregator: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        decomposer.decompose.return_value = [make_subtask("s1")]
        selector.select.return_value = make_agent()
        caplog.set_level(logging.INFO)
        captured_task_id: str | None = None

        async def capture(task_id: str, results: list) -> SwarmResult:
            nonlocal captured_task_id
            captured_task_id = task_id
            return SwarmResult(task_id=task_id, final_content="", subtask_results=results)

        aggregator.aggregate.side_effect = capture

        await orch.run("id match")

        start_logs = [m for m in caplog.messages if "workflow started" in m.lower()]
        assert len(start_logs) == 1
        assert captured_task_id is not None
        assert captured_task_id in caplog.text
