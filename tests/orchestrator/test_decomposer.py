import pytest
from src.orchestrator.decomposer import RuleBasedTaskDecomposer
from src.orchestrator.models import TaskRequest


@pytest.mark.asyncio
async def test_rule_based_task_decomposer():
    """Test that the RuleBasedTaskDecomposer returns exactly 3 subtasks in correct order."""
    decomposer = RuleBasedTaskDecomposer()
    request = TaskRequest(description="Build a new login feature.")
    
    subtasks = await decomposer.decompose(request)
    
    # Verify exactly 3 subtasks
    assert len(subtasks) == 3
    
    # Verify order and kinds
    assert subtasks[0].kind == "architect"
    assert subtasks[1].kind == "coder"
    assert subtasks[2].kind == "reviewer"
    
    # Verify dependencies
    assert subtasks[0].dependencies == []
    assert subtasks[1].dependencies == [subtasks[0].id]
    assert subtasks[2].dependencies == [subtasks[1].id]
    
    # Verify unique IDs
    ids = [s.id for s in subtasks]
    assert len(set(ids)) == 3
    
    # Verify descriptions
    for s in subtasks:
        assert s.description == "Build a new login feature."

@pytest.mark.asyncio
async def test_rule_based_task_decomposer_empty_description():
    """Test decomposer handles empty description cleanly."""
    decomposer = RuleBasedTaskDecomposer()
    request = TaskRequest(description="")
    
    subtasks = await decomposer.decompose(request)
    assert len(subtasks) == 3
    for s in subtasks:
        assert s.description == ""
