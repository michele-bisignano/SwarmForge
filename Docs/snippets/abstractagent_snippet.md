# Doc Snippet: AbstractAgent

**Class docstring:** Defines the foundational contract and common interface for all agents.

It ensures all derived agents adhere to a consistent operational structure
within the SwarmForge execution framework.

## Methods

### `run(subtask: {'cls': 'ExprName', 'member': 'run', 'name': 'Subtask'}) -> None`
```
Executes the core logic defined by a specific subtask.

Coordinates necessary sub-operations (e.g., planning, coding, reviewing).

@param subtask: The Subtask object containing task instructions and metadata.
@return: A SubtaskResult containing the outcome, status, and content.
@raise ConnectionError: If the underlying external resource is unreachable.
```

### `agent_id() -> None`
```
Returns a unique, immutable identifier for this agent instance.

@return: A string identifier following the pattern [AgentType]_[UniqueID].
```

### `capabilities() -> None`
```
Returns a list of generic task types that this agent handles.

@return: A list of strings corresponding to the subtask kinds.
```

### `health() -> None`
```
Checks the operational status of the agent.

@return: True if the agent is fully operational; False otherwise.
```
