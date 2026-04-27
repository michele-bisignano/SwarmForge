# Contract: AbstractTaskDecomposer
# File: src/orchestrator/decomposer.py

## Responsibility
Define the interface for decomposing a natural language task description into a list of ordered subtasks.

## Public Interface

### `async decompose(request: TaskRequest) -> list[Subtask]`
"""
Decompose a task request into a sequence of subtasks.

@param request: The task request containing the natural language description.
@return: A list of Subtask objects representing the decomposed plan.
@raise NotImplementedError: Always, as this is an abstract method.
"""

## Dependencies — What This Class Consumes

### TaskRequest
- Methods used: None (Value Object).

### Subtask
- Methods used: None (Value Object).

## SRP Boundary
Implementation of concrete subclasses should not exceed ~150 lines of logic.

## Test Coverage
- Validate that concrete subclasses correctly handle empty or invalid task descriptions.
- Validate that concrete subclasses correctly populate all Subtask fields.

---

# Contract: RuleBasedTaskDecomposer
# File: src/orchestrator/decomposer.py

## Responsibility
Decompose tasks into a static sequence of Architect -> Coder -> Reviewer subtasks.

## Public Interface

### `async decompose(request: TaskRequest) -> list[Subtask]`
"""
Decompose a task into a fixed sequence: Architect, then Coder, then Reviewer.

@param request: The task request.
@return: A list containing three subtasks in the fixed order.
"""

## Dependencies — What This Class Consumes

### TaskRequest
- Methods used: None (Value Object).

### Subtask
- Methods used: None (Value Object).

## Behavioral Constraints
- Always return exactly three subtasks.
- Order: Architect (kind=architect), then Coder (kind=coder), then Reviewer (kind=reviewer).
- All three subtasks share the same `task_id` and the original `description`.
- Assign unique `id` (UUID4) to each subtask.

## SRP Boundary
- Complexity threshold: ~40 lines.
- Stop and escalate if dynamic decomposition logic is requested.

## Test Coverage
- Test that it always returns three subtasks.
- Test that the order and kinds are correct.
- Test-first enabled: YES
- Model tier: cheap

## Ownership
- contract: Docs/contracts/TaskDecomposer.contract.md
- implementation: src/orchestrator/decomposer.py
- responsible_contract: Docs/contracts/TaskDecomposer.contract.md
