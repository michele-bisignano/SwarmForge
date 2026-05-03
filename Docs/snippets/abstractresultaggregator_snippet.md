# Doc Snippet: AbstractResultAggregator

**Class docstring:** Abstract base class for result aggregation strategies.

## Methods

### `aggregate(task_id: {'cls': 'ExprName', 'member': 'aggregate', 'name': 'str'}, results: {'cls': 'ExprSubscript', 'left': {'cls': 'ExprName', 'member': 'aggregate', 'name': 'list'}, 'slice': {'cls': 'ExprName', 'member': 'aggregate', 'name': 'SubtaskResult'}}) -> None`
```
Aggregate subtask results into a final SwarmResult.

@param task_id: The ID of the original task.
@param results: List of subtask results to aggregate.
@return: A consolidated SwarmResult.
```
