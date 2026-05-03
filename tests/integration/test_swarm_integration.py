import pytest
from src.orchestrator.orchestrator import SwarmOrchestrator
from src.orchestrator.decomposer import RuleBasedTaskDecomposer
from src.orchestrator.registry import AgentRegistry
from src.agents.stubs import ArchitectAgent, CoderAgent, ReviewerAgent
from src.orchestrator.selector import CapabilityMatchSelector
from src.orchestrator.aggregator import SequentialResultAggregator
from src.orchestrator.models import SwarmResult, SubtaskStatus

@pytest.mark.asyncio
async def test_swarm_orchestrator_integration():
    # Setup components
    decomposer = RuleBasedTaskDecomposer()
    registry = AgentRegistry()
    
    # Register agents
    registry.register(ArchitectAgent())
    registry.register(CoderAgent())
    registry.register(ReviewerAgent())
    
    selector = CapabilityMatchSelector()
    aggregator = SequentialResultAggregator()
    
    # Setup orchestrator
    orchestrator = SwarmOrchestrator(
        decomposer=decomposer,
        registry=registry,
        selector=selector,
        aggregator=aggregator
    )
    
    # Execute workflow
    task_description = "Design the module architecture. Implement the core logic. Review the implementation."
    result = await orchestrator.run(task_description)
    
    # Assertions
    assert isinstance(result, SwarmResult)
    assert len(result.results) == 3
    
    # Verify all results are OK
    for subtask_result in result.results:
        assert subtask_result.status == SubtaskStatus.OK
        
    # Verify final content
    assert len(result.final_content) > 0
