# Contract: AbstractResultAggregator
# File: src/orchestrator/aggregator.py

## Responsibility
Define the interface for aggregating multiple subtask results into a single swarm result.

## Public Interface

### `aggregate(task_id: str, results: list[SubtaskResult]) -> SwarmResult`
"""
Aggregate a list of subtask results into a final SwarmResult.

@param task_id: Unique identifier of the original task.
@param results: List of SubtaskResult objects to be aggregated.
@return: A SwarmResult containing the aggregated final_content and all input results.
@raise NotImplementedError: Always, as this is an abstract method.
"""

## Dependencies — What This Class Consumes

### SubtaskResult
- Methods used: None (Value Object).

### SwarmResult
- Methods used: None (Value Object).

## SRP Boundary
Implementation of concrete subclasses should not exceed ~100 lines of logic.

## Test Coverage
- Validate that concrete subclasses correctly handle empty result lists.
- Validate that concrete subclasses correctly integrate with SwarmResult.

---

# Contract: SequentialResultAggregator
# File: src/orchestrator/aggregator.py

## Responsibility
Aggregate subtask results sequentially by concatenating content of successful results.

## Public Interface

### `aggregate(task_id: str, results: list[SubtaskResult]) -> SwarmResult`
"""
Aggregate subtask results by concatenating the content of all 'OK' results.

@param task_id: Unique identifier of the original task.
@param results: List of SubtaskResult objects to be aggregated.
@return: A SwarmResult where final_content is the newline-separated concatenation of all 'OK' results, and results list is preserved.
"""

## Dependencies — What This Class Consumes

### SubtaskResult
- Methods used: None (Value Object).

### SwarmResult
- Methods used: None (Value Object).

## Behavioral Constraints
- Concatenate content from all SubtaskResult (where status == OK) using "\n" as a separator.
- Include ALL results in the returned SwarmResult.results (including FAILED status).
- If results list is empty, return SwarmResult with empty final_content and empty results list.
- Never raise exceptions; handle empty/invalid input gracefully.

## SRP Boundary
- Complexity threshold: ~40 lines. 
- Stop and escalate if logic for formatting or filtering becomes significantly more complex.

## Test Coverage
- Test aggregation with mixed OK and FAILED results.
- Test aggregation with an empty results list.
- Test aggregation with multiple OK results ensuring correct order and newline separation.
- Test-first enabled: YES
- Model tier: cheap
